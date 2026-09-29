"""Validate the bounded quantitative literature measurement resource."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalogues"
DETAILED_M3_SOURCE_IDS = {"LIT-002", "LIT-006", "LIT-007", "LIT-010", "LIT-014", "LIT-018", "LIT-023", "LIT-028"}
REQUIRED = {
    "measurement_id", "provenance_layer", "source_id", "lithology", "sample_state",
    "measurement_family", "geometry_class", "statistic_type", "unit", "method",
    "source_locator", "value_text_raw",
}


def read(name: str) -> list[dict]:
    with (CAT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f"Literature measurement validation failed: {message}")


def main() -> None:
    rows = read("literature_quantitative_measurements_v1.csv")
    coverage = read("literature_quantitative_coverage_v1.csv")
    if not rows or set(rows[0]) != REQUIRED | {"source_citation", "natural_setting", "location_precision", "sample_group_id", "parent_group_id", "component_label", "physical_specimens_represented", "value", "value_min", "value_max", "auxiliary_statistic_type", "auxiliary_value", "native_definition", "weighting_or_definition", "observation_window_or_detection_limit", "depth_stress_state_context", "notes"}:
        fail("unexpected long-form measurement columns")
    ids = [row["measurement_id"] for row in rows]
    if len(ids) != len(set(ids)) or any(not key.startswith("LITM-") for key in ids):
        fail("measurement IDs are missing or non-unique")
    if len(rows) < 250:
        fail(f"expected a bounded resource of at least 250 rows, found {len(rows)}")
    if any(row["source_id"] in DETAILED_M3_SOURCE_IDS for row in rows):
        fail("detailed M3 source rows were copied into the literature resource")
    if any(not row["source_locator"] for row in rows):
        fail("every measurement needs a source locator")
    if any(not any(row[key] for key in ("value", "value_min", "value_max", "auxiliary_value")) for row in rows):
        fail("every row must retain at least one published numeric value")
    for row in rows:
        for key in ("value", "value_min", "value_max", "auxiliary_value"):
            if row[key]:
                try:
                    float(row[key])
                except ValueError:
                    fail(f"non-numeric {key} in {row['measurement_id']}")
        if row["value_min"] and row["value_max"] and float(row["value_min"]) > float(row["value_max"]):
            fail(f"reversed source range in {row['measurement_id']}")

    park = [row for row in rows if row["provenance_layer"] == "park_santamarina_benchmark"]
    if len(park) != 214:
        fail(f"expected 214 Park S2 parameter rows, found {len(park)}")
    components = defaultdict(list)
    for row in park:
        components[(row["parent_group_id"], row["component_label"])].append(row)
        if row["geometry_class"] != "fitted pore-scale distribution" or row["unit"] != "um":
            fail(f"Park S2 semantics changed in {row['measurement_id']}")
    if len(components) != 107:
        fail(f"expected 107 Park S2 fitted components, found {len(components)}")
    if len({row["parent_group_id"] for row in park}) != 83:
        fail("expected 83 named Park S2 groups; state-specific group numbers may have collided")
    for key, component_rows in components.items():
        types = {row["statistic_type"] for row in component_rows}
        if len(component_rows) != 2 or types != {"fitted distribution mean", "fitted distribution standard deviation"}:
            fail(f"Park component {key} is not a mean/standard-deviation pair")

    if len(coverage) != 9:
        fail("coverage must have one row for each high-level lithology")
    cov_rows = sum(int(row["quantitative_measurement_rows"]) for row in coverage)
    if cov_rows != len(rows):
        fail("coverage row counts do not match measurement resource")
    if any("fitted_pore_scale_unresolved_rows" not in row for row in coverage):
        fail("coverage must report unresolved fitted pore-scale rows separately")

    scalar = sum(bool(row["value"]) + bool(row["value_min"]) + bool(row["value_max"]) + bool(row["auxiliary_value"]) for row in rows)
    print(
        f"Literature measurement resource validation passed: {len(rows)} rows, "
        f"{scalar} explicit scalar values, {len(park)} Park S2 parameter rows "
        f"from {len(components)} fitted components, and {len(rows) - len(park)} other-literature rows."
    )


if __name__ == "__main__":
    main()
