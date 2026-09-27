"""Offline structural and scientific-meaning checks for M3 first ingestion."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/m3_first_ingestion"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    samples = rows("samples.csv"); measurements = rows("measurements.csv")
    distributions = rows("measurement_distribution.csv"); objects = rows("network_objects.csv")
    sample_ids = {r["sample_id"] for r in samples}
    measurement_ids = {r["measurement_id"] for r in measurements}
    if len(sample_ids) != len(samples) or len(measurement_ids) != len(measurements):
        raise SystemExit("sample_id and measurement_id must be unique")
    if not all(r["sample_id"] in sample_ids for r in measurements):
        raise SystemExit("measurement references an unknown sample")
    if not all(r["measurement_id"] in measurement_ids for r in distributions + objects):
        raise SystemExit("value row references an unknown measurement")
    for r in distributions:
        if not (float(r["bin_lower_um"]) > 0 and float(r["bin_upper_um"]) > float(r["bin_lower_um"]) and float(r["value_normalized"]) >= 0):
            raise SystemExit(f"invalid MIP bin {r['measurement_id']} {r['bin_id']}")
        if r["value_type"] != "incremental_intrusion_porosity" or r["weighting_basis"] != "incremental_intruded_porosity":
            raise SystemExit("MIP distribution meaning was changed")
    roles = {r["measurement_id"]: r["quantity_role"] for r in measurements}
    for r in objects:
        if float(r["radius_um"]) <= 0 or r["radius_unit_raw"] != "µm":
            raise SystemExit(f"invalid source radius {r['measurement_id']} {r['object_id_raw']}")
        if r["geometry_class"] == "pore_body" and roles[r["measurement_id"]] != "body":
            raise SystemExit("pore body role mismatch")
        if r["geometry_class"] == "pore_throat" and roles[r["measurement_id"]] != "throat_or_entry_equivalent":
            raise SystemExit("pore throat role mismatch")
    print(f"OK: {len(samples)} samples, {len(measurements)} measurements, {len(distributions)} MIP bins, {len(objects)} PNM objects")


if __name__ == "__main__":
    main()
