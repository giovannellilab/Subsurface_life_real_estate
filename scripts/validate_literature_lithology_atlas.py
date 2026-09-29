"""Validate the curated Literature Lithology Atlas v1."""
from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalogues"
OUT = ROOT / "data/processed/m3_literature_lithology_atlas_v1/plots"
LITHOLOGIES = {
    "unconsolidated sand/sediment", "sandstone", "mudstone/shale", "carbonate",
    "basalt/volcanic rock", "granite/granitoid", "gabbro/mafic crystalline",
    "serpentinite/ultramafic", "metamorphic rock",
}
ALLOWED_FLAGS = {
    "broadly representative / within expected range", "special geological state",
    "special analytical construct", "strongly resolution-conditioned",
    "likely biased toward large resolved voids", "requires further investigation",
    "laboratory standard",
}


def read(name):
    with (CAT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value, label, allow_blank=True):
    if value == "" and allow_blank:
        return None
    try:
        result = float(value)
    except ValueError as exc:
        raise AssertionError(f"{label}: expected numeric or blank, got {value!r}") from exc
    assert math.isfinite(result), f"{label}: non-finite value"
    return result


def main():
    sources = read("literature_lithology_atlas_sources_v1.csv")
    observations = read("literature_lithology_atlas_observations_v1.csv")
    locations = read("literature_lithology_atlas_locations_v1.csv")
    envelopes = read("literature_lithology_reference_envelopes_v1.csv")
    void_envelopes = read("literature_lithology_void_envelopes_v1.csv")
    coverage = read("literature_lithology_atlas_coverage_v1.csv")
    porosity_summary = read("literature_lithology_porosity_summary_v1.csv")
    audit = read("m3_literature_envelope_audit_v1.csv")

    source_ids = [r["source_id"] for r in sources]
    assert len(source_ids) == len(set(source_ids)) >= 35
    assert all(r["persistent_identifier"] and r["landing_url"] and r["evidence_role"] for r in sources)
    counts = Counter(c for r in sources for c in r["lithology_classes"].split("|"))
    assert set(counts) == LITHOLOGIES
    assert all(4 <= counts[lith] <= 6 for lith in LITHOLOGIES), counts

    obs_ids = [r["observation_id"] for r in observations]
    assert len(obs_ids) == len(set(obs_ids))
    for row in observations:
        assert row["source_id"] in source_ids
        assert row["lithology"] in LITHOLOGIES
        assert row["geometry_class"] and row["method"]
        values = [number(row[k], f"{row['observation_id']} {k}") for k in ("size_min", "size_central", "size_max")]
        values = [v for v in values if v is not None]
        assert all(v > 0 for v in values)
        if len(values) >= 2:
            assert values == sorted(values), f"{row['observation_id']}: size order"
        if values:
            assert row["radius_diameter_or_definition"] and row["size_unit"]
        # Prevent the most consequential silent conflations.
        if "throat" in row["geometry_class"] or "entry" in row["geometry_class"]:
            assert "throat" in row["radius_diameter_or_definition"].lower() or "entry" in row["radius_diameter_or_definition"].lower() or "mip" in row["method"].lower()
        if any(word in row["geometry_class"] for word in ("crack", "fracture", "vug", "vesicle")):
            assert any(word in (row["geometry_class"] + row["interpretation_note"] + row["radius_diameter_or_definition"]).lower() for word in ("crack", "fracture", "vug", "vesicle"))

    loc_ids = [r["location_id"] for r in locations]
    assert len(loc_ids) == len(set(loc_ids))
    for row in locations:
        lat = number(row["latitude"], row["location_id"], allow_blank=False)
        lon = number(row["longitude"], row["location_id"], allow_blank=False)
        assert -90 <= lat <= 90 and -180 <= lon <= 180
        assert row["location_precision"] in {"exact", "exact borehole", "exact drilling region", "exact volcanic setting", "approximate locality", "regional centroid"}
        assert row["coordinate_provenance"]
        assert set(row["lithology"].split("|")) <= LITHOLOGIES

    assert len(coverage) == len(LITHOLOGIES)
    assert {r["lithology"] for r in coverage} == LITHOLOGIES
    for row in coverage:
        assert int(row["independent_literature_sources"]) == counts[row["lithology"]]
        assert int(row["mapped_natural_settings"]) >= 1
        assert int(row["documented_primary_physical_specimens_minimum"]) >= 1

    assert {r["lithology"] for r in envelopes} == LITHOLOGIES
    for row in envelopes:
        for prefix in ("total_porosity", "effective_porosity", "pore_body_or_matrix_scale", "throat_or_constriction_scale"):
            lo = number(row[f"{prefix}_min_percent"] if "porosity" in prefix else row[f"{prefix}_min_um"], f"{row['lithology']} {prefix} min")
            hi = number(row[f"{prefix}_max_percent"] if "porosity" in prefix else row[f"{prefix}_max_um"], f"{row['lithology']} {prefix} max")
            assert (lo is None) == (hi is None)
            if lo is not None:
                assert 0 <= lo <= hi
        assert set(row["supporting_source_ids"].split("|")) <= set(source_ids)
        assert row["scope_note"]

    allowed_voids = {
        "intergranular pore", "matrix/intergranular pore", "matrix pore", "matrix intercrystalline pore",
        "pore body", "equant pore body", "pore throat / entry constriction", "pore throat / connecting aperture",
        "grain-boundary / intragranular pore", "grain-boundary / reaction nanoporosity",
        "grain-boundary pore / microcrack", "microcrack / crack", "fracture-associated void",
        "vug / dissolution cavity", "vesicle",
    }
    assert len(void_envelopes) >= 25
    for row in void_envelopes:
        assert row["lithology"] in LITHOLOGIES
        assert row["void_class"] in allowed_voids
        lo, hi = number(row["size_min_um"], "void envelope minimum", allow_blank=False), number(row["size_max_um"], "void envelope maximum", allow_blank=False)
        assert 0 < lo <= hi and row["size_unit"] == "um"
        assert set(row["supporting_source_ids"].split("|")) <= set(source_ids)
        assert row["scope_note"]

    assert {r["lithology"] for r in porosity_summary} == LITHOLOGIES
    for row in porosity_summary:
        assert int(row["independent_literature_sources"]) == counts[row["lithology"]]
        for key in ("total_porosity_q1_percent", "total_porosity_median_percent", "total_porosity_q3_percent",
                    "effective_connected_q1_percent", "effective_connected_median_percent", "effective_connected_q3_percent"):
            number(row[key], f"{row['lithology']} {key}")
        assert row["statistical_interpretation"]

    audited = {r["m3_source_id"] for r in audit}
    assert {"M3-001", "M3-002", "M3-RLD-003", "M3-005", "M3-RLD-004", "M3-023", "M3-024", "M3-025-mafic", "M3-025-ultramafic"} <= audited
    for row in audit:
        flags = set(row["atlas_assessment_flags"].split("|"))
        assert flags <= ALLOWED_FLAGS, (row["m3_source_id"], flags - ALLOWED_FLAGS)
        assert row["evidence"] and row["recommended_resource_treatment"]

    expected_plots = {"literature_atlas_global_map.svg", "literature_porosity_envelopes.svg", "literature_atlas_evidence_depth.svg", "literature_void_class_envelopes.svg", "m3_porosity_against_literature_envelopes.svg"}
    assert expected_plots <= {p.name for p in OUT.glob("*.svg")}
    print(f"Literature Lithology Atlas validation passed: {len(sources)} sources, {len(observations)} observation rows, {len(locations)} mapped settings, {len(envelopes)} compact envelope rows, {len(void_envelopes)} void-class envelope rows.")


if __name__ == "__main__":
    main()
