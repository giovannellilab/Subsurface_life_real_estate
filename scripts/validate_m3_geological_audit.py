"""Validate the local M3 geological-resource audit overlay."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/processed/m3_geological_resource_audit_v1"


def read(name: str) -> list[dict]:
    with (AUDIT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = json.loads((AUDIT / "audit_manifest.json").read_text())
    assert manifest["independent_publications"] == 8
    assert manifest["raw_geometry_rows_audited"] == 2_516_715

    sources = read("coverage_by_source.csv")
    lithologies = read("coverage_by_lithology.csv")
    geometry = read("sample_geometry_summary.csv")
    porosity = read("porosity_audit.csv")
    lipnice = read("lipnice_specimen_classification.csv")
    sites = read("geographic_sites.csv")
    mip = read("mip_porosity_aware_overlap.csv")
    discrepancies = read("source_discrepancies.csv")

    assert len(sources) == 8 and len(lithologies) == 8
    assert sum(int(r["geometry_observations_bins_or_objects"]) for r in sources) == 2_516_715
    assert len({r["sample_id"] for r in lipnice}) == 21
    assert sum(r["matrix_reference_eligible"] == "yes" for r in lipnice) == 7
    assert len(sites) == 7
    assert all(r["coordinate_support"] for r in sites)
    assert len(mip) == 63
    assert all(0 <= float(r["whole_specimen_intruded_porosity_fraction_above_width"]) <= float(r["source_connected_porosity_fraction"]) for r in mip)
    assert any(r["field"] == "throat object count" and "4336" in r["machine_readable_artifact"] for r in discrepancies)

    expected_stats = {"minimum_um","p5_um","p25_um","median_um","arithmetic_mean_um","geometric_mean_um","p75_um","p95_um","maximum_um","weighting_basis"}
    assert expected_stats <= geometry[0].keys()
    for row in geometry:
        values = [float(row[k]) for k in ("minimum_um","p5_um","p25_um","median_um","p75_um","p95_um","maximum_um")]
        assert values == sorted(values), row["measurement_id"]
    assert any(r["porosity_type"] == "MIP_connected_total" for r in porosity)
    assert any(r["porosity_type"] == "wet_dry_bulk" for r in porosity)

    site = (ROOT / "site/index.html").read_text(encoding="utf-8")
    for phrase in ("4,452 strict LPSN-supported species", "0.714%", "objects are measurements within specimens", "Park &amp; Santamarina", "modelled multiscale pore-cluster/domain"):
        assert phrase in site
    assert "data/raw/" not in site and "data/processed/" not in site

    for name in ("geological_evidence_depth.svg","global_sampling_map.svg","porosity_context.svg","sample_geometry_summaries.svg"):
        text = (AUDIT / "plots" / name).read_text(encoding="utf-8")
        assert "<svg" in text and "<text" in text

    print("M3 geological resource audit validation passed: 8 sources, 8 lithologies, 2,516,715 geometry rows audited.")


if __name__ == "__main__":
    main()
