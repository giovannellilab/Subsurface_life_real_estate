"""Offline tests for species indexing and conservative exploratory summaries."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from subsurface_life_real_estate.analysis import analyze
from subsurface_life_real_estate.morphology import classify_strain


def row(identifier, *, species="Synthetic example", domain="Bacteria", phylum="Testota", width=0.5,
        length=1.0, classes=None, present=True):
    return {
        "observation_id": f"{identifier}:0", "bacdive_id": str(identifier),
        "observation_present": present, "taxonomy_raw": {"species": species, "domain": domain, "phylum": phylum},
        "cell_shape_raw": "rod-shaped", "cell_length_raw": f"{length} µm" if length is not None else None,
        "cell_width_raw": f"{width} µm" if width is not None else None,
        "length_min_um": length, "length_max_um": length,
        "width_min_um": width, "width_max_um": width,
        "morphology_classes": classes or ["straightforward_numerical_morphology"],
        "qc_flag": [], "source_reference": [], "lpsn_csv_status_raw": "validly published under the ICNP; correct name",
    }


class AnalysisTests(unittest.TestCase):
    def test_multiple_observations_is_a_review_class_not_a_conflict(self):
        rows = [
            {"observation_present": True, "cell_shape_raw": "rod-shaped",
             "length_min_um": 1.0, "length_max_um": 2.0,
             "width_min_um": 0.5, "width_max_um": 0.8,
             "cell_length_raw": "1.0-2.0 µm", "cell_width_raw": "0.5-0.8 µm",
             "morphology_observation_raw": {"cell shape": "rod-shaped"}, "qc_flag": []},
            {"observation_present": True, "cell_shape_raw": "rod-shaped",
             "length_min_um": 1.5, "length_max_um": 2.5,
             "width_min_um": 0.5, "width_max_um": 0.8,
             "cell_length_raw": "1.5-2.5 µm", "cell_width_raw": "0.5-0.8 µm",
             "morphology_observation_raw": {"cell shape": "rod-shaped"}, "qc_flag": []},
        ]
        classify_strain(rows)
        for value in rows:
            self.assertIn("multiple_observations", value["morphology_classes"])
            self.assertNotIn("multiple_conflicting_observations", value["morphology_classes"])

    def test_writes_species_ecdf_coverage_and_excludes_complex_width(self):
        rows = [
            row(1, width=0.2),
            row(2, species="Synthetic other", domain="Archaea", phylum="Archaea group", width=0.4),
            row(3, width=100, classes=["filamentous", "numerical_complex_morphology"]),
            row(4, species="Synthetic example", width=None, length=2),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "observations.jsonl"
            source.write_text("".join(json.dumps(value) + "\n" for value in rows))
            original = source.read_bytes()
            output = Path(tmp) / "analysis"
            first = analyze(source, output)
            before = {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()}
            second = analyze(source, output)
            self.assertEqual(original, source.read_bytes())
            self.assertEqual(first, second)
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()})
            self.assertEqual(first["clean_width_ecdf_n"], 2)
            self.assertEqual(first["species_group_count"], 2)
            self.assertEqual(first["species_groups_with_multiple_bacdive_type_strain_records"], 1)
            self.assertEqual(first["distribution"]["width_min_um"]["major_original_bacdive_phyla"], {})
            ecdf = (output / "width_ecdf.csv").read_text()
            self.assertNotIn("100.0", ecdf)
            self.assertIn("0.2", ecdf)


if __name__ == "__main__":
    unittest.main()
