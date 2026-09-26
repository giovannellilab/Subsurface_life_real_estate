"""Offline tests for immutable scientific-QC overlays and species weighting."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from subsurface_life_real_estate.scientific_qc import (
    eligibility, harmonized_taxonomy, run_scientific_qc, species_table,
    verification_rows,
)


def observation(identifier="1", *, species="Synthetic species", width=0.5,
                phylum="Oldphyla", embedded_phylum="Newphyla", source=True):
    refs = [{"doi/url": "10.9999/example", "title": f"{species} sp. nov. description"}] if source else []
    return {
        "observation_id": f"{identifier}:0", "bacdive_id": identifier,
        "species_name": species, "observation_present": True,
        "taxonomy_raw": {"species": species, "domain": "Bacteria", "phylum": phylum},
        "lpsn_cross_reference": {"species": species, "domain": "Bacteria", "phylum": embedded_phylum},
        "lpsn_csv_name": species, "lpsn_linked_name": None,
        "nomenclature_validation_status": "validated_name_and_type",
        "lpsn_csv_status_raw": "validly published under the ICNP; correct name",
        "lpsn_csv_row_raw": {"authors": "Example et al. 2017"},
        "cell_shape_raw": "rod-shaped", "cell_length_raw": "1-2 µm",
        "cell_width_raw": f"{width} µm", "cell_length_unit_raw": None,
        "cell_width_unit_raw": None, "length_min_um": 1.0, "length_max_um": 2.0,
        "width_min_um": width, "width_max_um": width, "source_reference": refs,
        "morphology_observation_raw": {"cell width": f"{width} µm"},
        "morphology_classes": ["straightforward_numerical_morphology"], "qc_flag": [],
    }


class ScientificQcTests(unittest.TestCase):
    def test_exclusions_are_explicit_and_source_rows_unchanged(self):
        row = observation()
        excluded_row = observation("2")
        excluded_row["morphology_classes"] = ["filamentous", "numerical_complex_morphology"]
        original = copy.deepcopy([row, excluded_row])
        included, excluded = eligibility([row, excluded_row])
        self.assertEqual([value["observation_id"] for value in included], ["1:0"])
        self.assertEqual(excluded[0]["exclusion_reason"], ["provisional_filamentous"])
        self.assertEqual([row, excluded_row], original)

    def test_manual_correction_and_unresolved_overlay_do_not_replace_source(self):
        nanometre = observation("140751", species="Croceitalea marina", width=.0004)
        nanometre["cell_width_raw"] = "0.4-0.6 nm"
        nanometre["width_max_um"] = .0006
        nanometre["source_reference"] = [{"doi/url": "10.1099/ijsem.0.002298", "title": "Croceitalea marina sp. nov."}]
        corrected = observation("141099", species="Nioella aestuarii", width=800)
        corrected["cell_width_raw"] = "0.8-1.0 mm"
        corrected["width_max_um"] = 1000
        corrected["source_reference"] = [{"doi/url": "10.1099/ijsem.0.002442", "title": "Nioella aestuarii sp. nov."}]
        unresolved = observation("3", width=0.05)
        original = copy.deepcopy([nanometre, corrected, unresolved])
        reviews, corrections = verification_rows([nanometre, corrected, unresolved])
        by_id = {row["observation_id"]: row for row in reviews}
        self.assertEqual(by_id["140751:0"]["outcome"], "corrected_unit")
        self.assertEqual(by_id["140751:0"]["corrected_width_min_um"], .4)
        self.assertEqual(by_id["141099:0"]["outcome"], "corrected_unit")
        self.assertEqual(by_id["141099:0"]["corrected_width_min_um"], .8)
        self.assertEqual(by_id["3:0"]["outcome"], "unresolved")
        self.assertEqual(len(corrections), 2)
        self.assertEqual([nanometre, corrected, unresolved], original)

    def test_harmonization_and_nonarbitrary_canonical_choice(self):
        first = observation("1", width=.4)
        second = observation("2", width=.8)
        mapping, records = harmonized_taxonomy([first, second])
        self.assertEqual(mapping["1"]["harmonized_phylum"], "Newphyla")
        self.assertEqual(records[0]["original_bacdive_phylum"], "Oldphyla")
        table = species_table([first, second], mapping, [first, second], [])
        self.assertEqual(table[0]["canonical_selection_status"], "unresolved")
        self.assertEqual(table[0]["canonical_selection_reason"], "multiple_nonidentical_best_priority_observations")

    def test_end_to_end_output_is_deterministic_and_does_not_mutate_source(self):
        rows = [observation("1", species="Species one", width=.4), observation("2", species="Species two", width=.8)]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "observations.jsonl"
            source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            before = source.read_bytes()
            output = Path(tmp) / "scientific_qc"
            first = run_scientific_qc(source, output)
            products = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}
            second = run_scientific_qc(source, output)
            self.assertEqual(before, source.read_bytes())
            self.assertEqual(first, second)
            self.assertEqual(products, {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()})
            self.assertEqual(first["canonical_species_with_width"], 2)
            self.assertTrue((output / "species_width_ecdf.csv").exists())


if __name__ == "__main__":
    unittest.main()
