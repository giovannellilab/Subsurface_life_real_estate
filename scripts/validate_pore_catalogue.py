"""Validate the small, tracked M3 source catalogue without fetching data."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "data/catalogues/m3_pore_geometry_source_catalogue.csv"
REQUIRED = {
    "catalogue_id", "source_id", "title", "year", "persistent_identifier",
    "landing_url", "repository_or_publisher", "lithology_class", "material_name",
    "sample_state", "geometry_class", "method", "size_window_or_resolution",
    "quantitative_artifacts", "access_level", "license_or_terms",
    "ingestion_readiness", "priority_tier", "scope_note",
}
GEOMETRIES = {"pore_body", "pore_throat", "matrix_pore", "grain_boundary_pore", "microcrack", "mixed_or_unresolved"}
READINESS = {"A", "B", "C"}


def values(value: str) -> set[str]:
    return set(value.split("|"))


def main() -> None:
    with CATALOGUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        rows = list(reader)
    if fields != REQUIRED:
        raise SystemExit(f"Unexpected catalogue columns: {sorted(fields)}")
    if not 20 <= len(rows) <= 40:
        raise SystemExit(f"Expected 20–40 reconnaissance candidates, found {len(rows)}")
    ids = [row["catalogue_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("catalogue_id must be unique")
    for row in rows:
        if not row["landing_url"].startswith("https://"):
            raise SystemExit(f"{row['catalogue_id']}: landing_url must be HTTPS")
        if row["ingestion_readiness"] not in READINESS:
            raise SystemExit(f"{row['catalogue_id']}: invalid readiness")
        if not values(row["geometry_class"]) <= GEOMETRIES:
            raise SystemExit(f"{row['catalogue_id']}: invalid geometry class")
        state_tokens = {"fresh", "altered", "weathered", "reacted", "serpentinized"}
        if state_tokens & values(row["lithology_class"].lower()):
            raise SystemExit(f"{row['catalogue_id']}: state must not be encoded as lithology")
    print(f"OK: {len(rows)} M3 candidates; {sum(r['ingestion_readiness'] == 'A' for r in rows)} acquisition-ready")


if __name__ == "__main__":
    main()
