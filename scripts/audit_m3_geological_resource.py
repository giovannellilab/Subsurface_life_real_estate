"""Audit the M3 geological resource without altering its source data.

The audit is intentionally an overlay.  It distinguishes publications,
reported geological settings, specimens, measurements, and extracted objects;
adds source-paper context that is absent from the machine-readable artifacts;
and writes only local, gitignored derived tables and figures.
"""
from __future__ import annotations

import bisect
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/reference_lithology_dataset_v1"
FIRST = ROOT / "data/processed/m3_first_ingestion"
MICROBES = ROOT / "data/processed/census_2026-09-14/scientific_qc_v1/species_analytical_table.csv"
OUT = ROOT / "data/processed/m3_geological_resource_audit_v1"
PLOTS = OUT / "plots"


SOURCE_META = {
    "M3-001": {
        "publication": "Stanek & Geraud (2019), Solid Earth 10:251-274",
        "dataset": "PANGAEA.898001",
        "setting": "Lipnice granite, Melechov pluton; MEL-5 borehole, Czech Republic",
        "reported_locations": 1,
        "boreholes": 1,
        "material": "natural borehole core; specimens deliberately span fresh, fractured, altered, fracture-surface and gouge material",
        "method": "mercury intrusion porosimetry (MIP)",
        "window": "about 0.005-300 um in paper; tabulated bins 0.008-309 um",
    },
    "M3-002": {
        "publication": "Thomson et al. (2018), Frontiers in Earth Science 6:58",
        "dataset": "Zenodo.1184144",
        "setting": "Fontainebleau and Berea reference sandstones; collection localities not reported in the data release",
        "reported_locations": 0,
        "boreholes": 0,
        "material": "two dry reference-rock specimens plus one oil/water-saturated Berea case",
        "method": "synchrotron micro-CT plus PerGeos PNM",
        "window": "0.74 um isotropic voxel; 500^3-voxel ROI; resolved segmented connected phase only",
    },
    "M3-RLD-003": {
        "publication": "Liu, Ma & Zhu (2022), Applied Sciences 12:2611",
        "dataset": "Mendeley Data t8rj6b6gwn",
        "setting": "Nansha Islands, South China Sea; carbonate samples from within 400 m below a coral-reef surface",
        "reported_locations": 1,
        "boreholes": 0,
        "material": "natural marine biogenic carbonate specimens A-E and terrigenous sandstone S",
        "method": "micro-CT plus maximum-ball pore-network extraction",
        "window": "61.75 um voxel for carbonates A-E; 30.45 um voxel for sandstone S",
    },
    "M3-005": {
        "publication": "Menefee et al. (2022), Water Resources Research 58:e2021WR030275",
        "dataset": "Mendeley Data n72yhbppkj",
        "setting": "Bambstone Bluestone quarry near Port Fairy, Victoria, Australia; exact sample coordinates not reported",
        "reported_locations": 1,
        "boreholes": 0,
        "material": "natural basalt block, laboratory-cut unreacted ungrooved half-core control",
        "method": "laboratory micro-CT segmentation plus pore analysis",
        "window": "14.99 um voxel; resolved pores only",
    },
    "M3-RLD-004": {
        "publication": "Payton et al. (2021), Petroleum Geoscience 27:petgeo2020-092",
        "dataset": "Figshare 12707840",
        "setting": "Wilmslow Sandstone Formation; Sellafield borehole 13B, Cumbria, UK",
        "reported_locations": 1,
        "boreholes": 1,
        "material": "seven natural borehole plugs, epoxy impregnated for imaging",
        "method": "micro-CT plus PerGeos PNM",
        "window": "2.6860-2.8409 um voxel, sample-specific; all-object tables mix connected and disconnected objects",
    },
    "M3-023": {
        "publication": "Fan et al. (2022), Fuel 330:125463",
        "dataset": "Harvard Dataverse WBSHKX with D1LDSO companion",
        "setting": "marine shale specimens W23 and J24; source formation/site metadata require confirmation from the paper",
        "reported_locations": 0,
        "boreholes": 0,
        "material": "natural shale specimens represented by image-derived cluster statistics and fractal model curves",
        "method": "CTSTA cluster analysis plus modelled multiscale fractal PSD/connectivity",
        "window": "CTSTA image resolution absent from deposit; model spans nanometres to hundreds of micrometres",
    },
    "M3-024": {
        "publication": "Imperial College pore-network data release (F42A)",
        "dataset": "Figshare 1189259 v1",
        "setting": "laboratory pack of Ottawa F42 quartz sand; not a natural sampling site",
        "reported_locations": 0,
        "boreholes": 0,
        "material": "laboratory-packed sand standard",
        "method": "micro-CT plus Statoil-format extracted PNM",
        "window": "9.996 um voxel; 300^3-voxel image; resolved extracted network only",
    },
    "M3-025": {
        "publication": "Falcon-Suarez et al. (2017), Geophysical Journal International 211:686-699",
        "dataset": "PANGAEA.873535 (tables 873533/873534)",
        "setting": "Atlantis Massif, Mid-Atlantic Ridge; five IODP boreholes",
        "reported_locations": 1,
        "boreholes": 5,
        "material": "eight natural drilled cores: four serpentinised ultramafic and four mafic",
        "method": "wet/dry bulk porosity and pressure-dependent permeability/electrical/elastic measurements",
        "window": "no pore-size distribution or size observation window",
    },
}


LIPNICE_CLASS = {
    "11": ("matrix_representative", "fresh granite matrix", "matrix pores plus grain-boundary/intragranular/cleavage cracks"),
    "3_1": ("fractured_matrix", "non-altered fractured granite", "fracture-associated cracks and matrix porosity"),
    "10_1": ("fracture_surface", "weakly altered barren fracture surface", "fracture-associated voids"),
    "10_2": ("matrix_after_surface_removal", "weakly altered; about 1 mm fracture-surface layer ground off", "alteration-associated matrix and crack porosity"),
    "9_7": ("matrix_with_sealed_fracture", "green matrix with thin dominantly sealed fracture", "alteration-associated matrix, grain-boundary pores and cracks"),
    "9_4": ("fracture_surface", "green clay-rich fracture surface", "fracture/alteration porosity"),
    "9_1": ("open_fracture", "green cohesive partially open fracture", "fracture-associated voids and cracks"),
    "7_3": ("matrix_representative", "yellow matrix in fracture corridor", "alteration-associated matrix pores and cracks"),
    "7_1": ("fracture_surface", "yellow clay-rich fracture surface", "fracture/alteration porosity"),
    "7_10": ("open_fracture", "yellow cohesive partially open fracture", "fracture-associated voids and cracks"),
    "6": ("fault_gouge", "yellow granite fault gouge", "fault-gouge and fracture-associated porosity"),
    "3_2": ("matrix_representative", "pink matrix near a single fracture", "matrix pores and cracks"),
    "5_3": ("porous_fracture_surface", "pink macroscopically porous fracture surface", "fracture-associated voids"),
    "5_5": ("open_fracture", "pink cohesive partially open fracture", "fracture-associated voids and cracks"),
    "4_1": ("fracture_surface", "pink nonporous iron-oxide-rich fracture surface", "fracture/alteration porosity"),
    "4_2": ("matrix_after_surface_removal", "pink fracture-corridor specimen with iron-oxide surface ground off", "matrix and crack porosity near fracture"),
    "1_2": ("matrix_representative", "brown matrix near a single fracture", "matrix pores and cracks"),
    "1_1": ("fracture_surface", "brown iron-oxide-rich fracture surface", "fracture/alteration porosity"),
    "2_2": ("matrix_representative", "brown fracture-corridor matrix with little macroscopic porosity", "matrix pores and cracks"),
    "2_3": ("cavity_rich_matrix", "brown matrix with frequent macroscopic cavities", "alteration cavities plus cracks and matrix porosity"),
    "2_1": ("open_fracture_and_surface", "brown cohesive partially open fracture plus iron-oxide-rich fracture surface", "fracture-associated voids and alteration porosity"),
}


POROSITY_ROWS = [
    # source_id, sample suffix, type, percent, scope, note
    ("M3-002", "Case1FB", "total", 3.8, "sample/ROI", "Fontainebleau source-paper total porosity"),
    ("M3-002", "Case1FB", "connected", 3.0, "sample/ROI", "source-paper resolved connected porosity; isolated 0.8%"),
    ("M3-002", "Case2B", "total", 19.9, "sample/ROI", "dry Berea source-paper total porosity"),
    ("M3-002", "Case2B", "connected", 19.6, "sample/ROI", "source-paper resolved connected porosity; isolated 0.4% (rounded)"),
    ("M3-002", "Case3B", "water_phase", 15.8, "segmented phase/ROI", "oil-water Berea water-bearing porosity; not whole-rock total"),
    ("M3-002", "Case3B", "connected_water_phase", 15.4, "segmented phase/ROI", "connected water-bearing porosity; paper also reports isolated component"),
    ("M3-RLD-003", "Carbonate_rock_A", "CT_total", 23.41, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Carbonate_rock_B", "CT_total", 7.71, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Carbonate_rock_C", "CT_total", 9.32, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Carbonate_rock_D", "CT_total", 8.51, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Carbonate_rock_E", "CT_total", 7.35, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Sandstone_S", "CT_total", 1.06, "whole imaged specimen", "paper Table 2"),
    ("M3-RLD-003", "Carbonate_rock_A", "CT_REV2", 23.99, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-RLD-003", "Carbonate_rock_B", "CT_REV2", 8.58, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-RLD-003", "Carbonate_rock_C", "CT_REV2", 7.59, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-RLD-003", "Carbonate_rock_D", "CT_REV2", 5.85, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-RLD-003", "Carbonate_rock_E", "CT_REV2", 6.73, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-RLD-003", "Sandstone_S", "CT_REV2", 0.83, "400^3-voxel REV", "paper Table 3; distribution table is REV2"),
    ("M3-005", "unreacted_ungrooved_basalt", "CT_context", 9.75, "whole experimental study core", "paper value; contextual, not assigned to the isolated ungrooved-half table"),
    ("M3-005", "unreacted_ungrooved_basalt", "saturation_context", 12.0, "separate bulk core from same rock", "paper value; not the imaged half-core"),
    ("M3-024", "F42A_quartz_sand_pack", "CT_image", 33.0, "laboratory pack image", "Results_F42A source metric"),
]


SITES = [
    ("Lipnice MEL-5", "M3-001", 49.620716, 15.410324, "exact borehole coordinate", "natural"),
    ("Sellafield BH13B", "M3-RLD-004", 54.38815261, -3.47205018, "converted from reported British National Grid NY 04506 00184 using EPSG:27700 to EPSG:4326; map-scale only", "natural"),
    ("304-U1309B", "M3-025", 30.16846, -42.11900, "PANGAEA event coordinate", "natural"),
    ("304-U1309D", "M3-025", 30.16865, -42.11900, "PANGAEA event coordinate", "natural"),
    ("357-M0068B", "M3-025", 30.12515, -42.09577, "PANGAEA event coordinate", "natural"),
    ("357-M0069A", "M3-025", 30.13240, -42.12003, "PANGAEA event coordinate", "natural"),
    ("357-M0076B", "M3-025", 30.12702, -42.11775, "PANGAEA event coordinate", "natural"),
]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cumulative = np.cumsum(weights)
    return float(values[np.searchsorted(cumulative, q * cumulative[-1], side="left")])


def geometry_label(source: str, geometry: str, quantity: str) -> str:
    if source == "M3-001":
        return "pore throat / MIP entry constriction; specimen microstructure may be matrix, crack, fracture surface, cavity, or gouge"
    if source == "M3-023":
        if quantity == "R":
            return "modelled multiscale pore-cluster domain with microfracture-mediated connectivity; not an observed pore body or throat"
        return "unresolved CTSTA connected-pore-cluster class; no physical length unit"
    return {"pore_body": "pore body", "pore_throat": "pore throat", "mixed_or_unresolved": "unresolved / transport-only"}.get(geometry, geometry)


def read_geometry() -> tuple[list[dict], dict[tuple, tuple[list[float], list[float]]], dict, dict]:
    counts = defaultdict(int)
    groups: dict[tuple, tuple[list[float], list[float]]] = {}
    measurement_ids = defaultdict(set)
    lithology_measurement_ids = defaultdict(set)
    with (DATA / "geometry_values.csv").open() as handle:
        for row in csv.DictReader(handle):
            counts[(row["source_id"], row["lithology"], row["sample_id"], row["geometry_class"])] += 1
            measurement_ids[row["source_id"]].add(row["measurement_id"])
            lithology_measurement_ids[(row["source_id"], row["lithology"])].add(row["measurement_id"])
            if not row["size_um"] or not row["weight_raw"] or "source_missing_weight" in row["qc_flags"]:
                continue
            try:
                size, weight = float(row["size_um"]), float(row["weight_raw"])
            except ValueError:
                continue
            if size <= 0 or weight <= 0:
                continue
            key = (
                row["source_id"], row["dataset_id"], row["lithology"], row["sample_id"],
                row["measurement_id"], row["method"], row["geometry_class"], row["quantity_name"],
                row["native_size_definition"], row["size_unit_raw"], row["weighting_basis"],
                row["observation_window_or_resolution"], geometry_label(row["source_id"], row["geometry_class"], row["quantity_name"]),
            )
            if key not in groups:
                groups[key] = ([], [])
            groups[key][0].append(size)
            groups[key][1].append(weight)
    rows = []
    for key, (raw_values, raw_weights) in sorted(groups.items()):
        v, w = np.asarray(raw_values), np.asarray(raw_weights)
        row = dict(zip([
            "source_id", "dataset_id", "lithology", "sample_id", "measurement_id", "method",
            "geometry_class_native", "quantity_name", "native_size_definition", "native_unit",
            "weighting_basis", "observation_window_or_resolution", "audited_geometry_class",
        ], key))
        row.update({
            "observation_or_bin_count": len(v),
            "weight_sum": f"{w.sum():.9g}",
            "minimum_um": f"{v.min():.9g}",
            "p5_um": f"{weighted_quantile(v,w,.05):.9g}",
            "p25_um": f"{weighted_quantile(v,w,.25):.9g}",
            "median_um": f"{weighted_quantile(v,w,.5):.9g}",
            "arithmetic_mean_um": f"{np.average(v,weights=w):.9g}",
            "geometric_mean_um": f"{math.exp(np.average(np.log(v),weights=w)):.9g}",
            "p75_um": f"{weighted_quantile(v,w,.75):.9g}",
            "p95_um": f"{weighted_quantile(v,w,.95):.9g}",
            "maximum_um": f"{v.max():.9g}",
            "interpretation": "Statistics describe the stated weighting population and native radius/diameter convention; they are not pooled across samples or methods.",
        })
        rows.append(row)
    return (rows, groups, {k: len(v) for k, v in measurement_ids.items()},
            {k: len(v) for k, v in lithology_measurement_ids.items()})


def microbial_widths() -> dict[str, list[float]]:
    fields = {"width_minimum": "corrected_width_min_um", "width_midpoint": "corrected_width_midpoint_um", "width_maximum": "corrected_width_max_um"}
    result = {name: [] for name in fields}
    with MICROBES.open() as handle:
        for row in csv.DictReader(handle):
            if row["canonical_selection_status"] != "canonical" or row["canonical_nomenclature_validation_status"] != "validated_name_and_type":
                continue
            for name, field in fields.items():
                result[name].append(float(row[field]))
    for values in result.values():
        values.sort()
    return result


def build_coverage(measurement_counts: dict, lithology_measurement_counts: dict) -> tuple[list[dict], list[dict]]:
    registry = list(csv.DictReader((DATA / "reference_lithology_dataset_v1.csv").open()))
    sample_lithology = {r["sample_id"]: r["lithology"] for r in registry}
    geometry_counts = defaultdict(int)
    with (DATA / "geometry_values.csv").open() as handle:
        for row in csv.DictReader(handle):
            geometry_counts[(row["source_id"], row["lithology"])] += 1
    connectivity_counts = defaultdict(int)
    with (DATA / "connectivity_metrics.csv").open() as handle:
        for row in csv.DictReader(handle):
            connectivity_counts[(row["source_id"], row["lithology"])] += 1
    attribute_counts = defaultdict(int)
    with (DATA / "source_measurement_attributes.csv").open() as handle:
        for row in csv.DictReader(handle):
            attribute_counts[(row["source_id"], sample_lithology[row["sample_id"]])] += 1
    edge_counts = defaultdict(int)
    with (DATA / "network_edges.csv").open() as handle:
        for row in csv.DictReader(handle):
            edge_counts[(row["source_id"], sample_lithology[row["sample_id"]])] += 1
    source_rows = []
    for source, meta in SOURCE_META.items():
        rr = [r for r in registry if r["source_id"] == source]
        liths = sorted({r["lithology"] for r in rr})
        source_rows.append({
            "source_id": source,
            "independent_publication": meta["publication"],
            "dataset_deposit": meta["dataset"],
            "lithologies": ";".join(liths),
            "reported_geological_setting": meta["setting"],
            "distinct_reported_geological_locations_or_formations": meta["reported_locations"],
            "distinct_boreholes": meta["boreholes"],
            "physical_specimens_or_cases": len({r["sample_id"] for r in rr}),
            "geometry_measurement_records": measurement_counts.get(source, 0),
            "geometry_observations_bins_or_objects": sum(geometry_counts[(source, lith)] for lith in liths),
            "connectivity_or_transport_rows": sum(connectivity_counts[(source, lith)] for lith in liths),
            "auxiliary_object_attribute_rows": sum(attribute_counts[(source, lith)] for lith in liths),
            "explicit_network_edge_rows": sum(edge_counts[(source, lith)] for lith in liths),
            "material_and_state": meta["material"],
            "method": meta["method"],
            "geometry_classes_native": ";".join(sorted({r["geometry_class"] for r in rr})),
            "resolution_or_detection_window_audited": meta["window"],
            "replication_warning": "Objects/bins are repeated measurements within specimens, not independent geological replicates.",
        })
    lith_rows = []
    for lith in sorted({r["lithology"] for r in registry}):
        rr = [r for r in registry if r["lithology"] == lith]
        sources = sorted({r["source_id"] for r in rr})
        lith_rows.append({
            "lithology": lith,
            "independent_sources": len(sources),
            "source_ids": ";".join(sources),
            "distinct_reported_natural_locations_or_formations": sum(SOURCE_META[s]["reported_locations"] for s in sources),
            "physical_specimens_or_cases": len({r["sample_id"] for r in rr}),
            "geometry_measurement_records": sum(lithology_measurement_counts.get((s, lith), 0) for s in sources),
            "geometry_observations_bins_or_objects": sum(geometry_counts[(s, lith)] for s in sources),
            "connectivity_or_transport_rows": sum(connectivity_counts[(s, lith)] for s in sources),
            "auxiliary_object_attribute_rows": sum(attribute_counts[(s, lith)] for s in sources),
            "explicit_network_edge_rows": sum(edge_counts[(s, lith)] for s in sources),
            "methods": ";".join(sorted({r["method"] for r in rr})),
            "geometry_classes_native": ";".join(sorted({r["geometry_class"] for r in rr})),
            "independence_note": "Source and site counts, not object counts, express geological replication.",
        })
    return source_rows, lith_rows


def build_porosity() -> list[dict]:
    rows = []
    # MIP intrusion sum is source-defined total connected porosity.
    mip = defaultdict(float)
    with (DATA / "geometry_values.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row["source_id"] == "M3-001":
                mip[row["sample_id"]] += float(row["weight_raw"])
    for sample, value in sorted(mip.items()):
        rows.append({"source_id":"M3-001","sample_id":sample,"porosity_type":"MIP_connected_total","porosity_percent":f"{100*value:.6g}","measurement_scope":"physical specimen","source_support":"sum of source incremental intrusion porosity; paper defines final intrusion as total connected porosity","audit_flag":"fracture/alteration context required; high values are not generic granite matrix porosity"})
    for source, suffix, kind, value, scope, note in POROSITY_ROWS:
        prefix = "M3-RLD:" if source not in {"M3-002"} else "M3-002:"
        rows.append({"source_id":source,"sample_id":prefix+suffix,"porosity_type":kind,"porosity_percent":value,"measurement_scope":scope,"source_support":note,"audit_flag":"CT resolution-conditioned" if "CT" in kind or source in {"M3-002","M3-024"} else "context only; do not assign to a different specimen"})
    with (DATA / "connectivity_metrics.csv").open() as handle:
        for row in csv.DictReader(handle):
            if row["source_id"] == "M3-RLD-004" and row["metric_name"] in {"total_porosity","connected_porosity"}:
                rows.append({"source_id":row["source_id"],"sample_id":row["sample_id"],"porosity_type":"CT_"+row["metric_name"],"porosity_percent":f"{100*float(row['value_normalized']):.6g}","measurement_scope":"imaged plug","source_support":row["definition"],"audit_flag":"2.6860-2.8409 um voxel; all-object size tables include disconnected objects"})
            if row["source_id"] == "M3-025" and row["metric_name"] == "bulk_porosity":
                rows.append({"source_id":row["source_id"],"sample_id":row["sample_id"],"porosity_type":"wet_dry_bulk","porosity_percent":row["value_raw"],"measurement_scope":"physical core specimen","source_support":row["definition"],"audit_flag":"bulk porosity; size distribution unavailable"})
    return rows


def build_mip_porosity_overlap(groups: dict) -> list[dict]:
    widths = microbial_widths()
    rows = []
    for key, (raw_sizes, raw_weights) in groups.items():
        source, dataset, lith, sample, measurement, method, geometry, quantity, definition, unit, basis, window, audited = key
        if source != "M3-001":
            continue
        sizes, weights = np.asarray(raw_sizes), np.asarray(raw_weights)
        total = float(weights.sum())
        for metric, microbial in widths.items():
            compatible = sum(weight * bisect.bisect_right(microbial, size) / len(microbial) for size, weight in zip(sizes, weights))
            rows.append({
                "source_id": source, "sample_id": sample, "microbial_width_metric": metric,
                "source_connected_porosity_fraction": f"{total:.9f}",
                "normalized_conditional_overlap": f"{compatible/total:.9f}",
                "whole_specimen_intruded_porosity_fraction_above_width": f"{compatible:.9f}",
                "whole_specimen_intruded_porosity_percent_above_width": f"{100*compatible:.6f}",
                "definition": "Expected source incremental intruded porosity in entry-equivalent bins >= a cultured-species width; integrates over the 4,452-species width distribution.",
                "caution": "Connected MIP-accessible porosity only; entry geometry and specimen fracture/alteration class remain explicit; not cellular accessibility.",
            })
    return rows


def build_connectivity_summary() -> list[dict]:
    grouped = defaultdict(list)
    definitions = {}
    units = {}
    with (DATA / "connectivity_metrics.csv").open() as handle:
        for row in csv.DictReader(handle):
            try:
                value = float(row["value_normalized"])
            except ValueError:
                continue
            key = (row["source_id"], row["sample_id"], row["lithology"], row["metric_name"])
            grouped[key].append(value)
            definitions[key] = row["definition"]
            units[key] = row["unit"]
    rows = []
    for key, values in sorted(grouped.items()):
        source, sample, lithology, metric = key
        unit = units[key]
        audit_note = "source metric retained"
        multiplier = 1.0
        if source == "M3-RLD-004" and metric == "permeability":
            # The CSV omits a unit and stores Darcy-scale numbers; source-paper
            # Table 2 reports the corresponding values in mD.
            multiplier, unit = 1000.0, "mD"
            audit_note = "unit recovered from source-paper Table 2; raw archive value multiplied by 1000"
        elif source == "M3-025" and metric == "permeability":
            unit = "m2"
            audit_note = "normalized values are SI m2; raw values remain in 10^-12 m2 in the source table"
        elif "porosity" in metric and max(values) <= 1:
            unit = "fraction"
            audit_note = "normalized fraction; source raw percent remains preserved in connectivity_metrics.csv"
        if source == "M3-025" and metric in {"p_wave_velocity", "s_wave_velocity"}:
            audit_note = "PANGAEA header says m/s but values 1.67-6.71 are velocity-scale inconsistent; retained and flagged, not reinterpreted"
        arr = np.asarray(values) * multiplier
        rows.append({
            "source_id":source,"sample_id":sample,"lithology":lithology,"metric_name":metric,
            "measurement_count":len(arr),"minimum":f"{arr.min():.9g}","median":f"{np.median(arr):.9g}","maximum":f"{arr.max():.9g}",
            "audited_unit":unit,"definition":definitions[key],"audit_note":audit_note,
        })
    return rows


def source_discrepancies() -> list[dict]:
    return [
        {
            "source_id":"M3-RLD-003","sample_id":"M3-RLD:Carbonate_rock_A","field":"throat object count",
            "machine_readable_artifact":"4336 nonblank throat-radius rows","source_paper":"4395 throats (Table 4)",
            "assessment":"deposit workbook and paper disagree; current ingestion faithfully reflects the workbook",
            "action":"flag the sample-level throat distribution; do not silently repair or impute the 59 absent rows",
        },
        {
            "source_id":"M3-RLD-003","sample_id":"M3-RLD:Carbonate_rock_A","field":"throat maximum/mean radius",
            "machine_readable_artifact":"maximum 667.501 um; mean 123.104 um","source_paper":"maximum 1044.66 um; mean 127.04 um (Table 4)",
            "assessment":"maximum discrepancy accompanies the count discrepancy; mean is close",
            "action":"retain workbook values with discrepancy flag; paper summary remains contextual",
        },
        {
            "source_id":"M3-RLD-004","sample_id":"all Sellafield samples","field":"permeability unit",
            "machine_readable_artifact":"CSV header omits unit; values 0.0416-6.040","source_paper":"40-6040 mD (Table 2)",
            "assessment":"archive values are Darcy-scale while the paper reports mD",
            "action":"audit overlay reports 41.6-6040 mD; future ingestion should record the paper-supported unit without changing raw values",
        },
        {
            "source_id":"M3-025","sample_id":"all Atlantis samples","field":"P- and S-wave velocity unit",
            "machine_readable_artifact":"PANGAEA header says m/s; values 1.67-6.71","source_paper":"velocity magnitudes are physically km/s-scale",
            "assessment":"source-table unit/magnitude inconsistency",
            "action":"retain source values and flag; do not convert until provenance is explicitly reconciled",
        },
    ]


def build_lipnice() -> list[dict]:
    samples = {row["source_sample_id"]: row for row in csv.DictReader((FIRST / "samples.csv").open()) if row["source_id"] == "M3-001"}
    rows = []
    for sample, source_row in sorted(samples.items()):
        cls, description, geometry = LIPNICE_CLASS[sample]
        rows.append({"sample_id":"M3-001:"+sample,"source_sample_id":sample,"borehole":"MEL-5","depth_context":source_row["collection_context"],"facies":source_row["sample_state"],"audited_specimen_class":cls,"source_description":description,"dominant_void_context":geometry,"matrix_reference_eligible":"yes" if cls in {"matrix_representative","matrix_after_surface_removal"} else "no","source":"Stanek & Geraud 2019 section 3.3 and Figure 3"})
    return rows


def benchmark_rows() -> list[dict]:
    return [
        {"benchmark_group":"natural soils","physical_datasets":14,"reported_distribution_components":14,"mean_pore_diameter_min_um":0.11,"mean_pore_diameter_max_um":178.4,"comparison_note":"broad soil range; laboratory/remoulded soils kept separate"},
        {"benchmark_group":"remoulded soils","physical_datasets":25,"reported_distribution_components":25,"mean_pore_diameter_min_um":0.16,"mean_pore_diameter_max_um":233.0,"comparison_note":"laboratory/remoulded benchmark, not natural-site replication"},
        {"benchmark_group":"carbonates","physical_datasets":23,"reported_distribution_components":35,"mean_pore_diameter_min_um":0.37,"mean_pore_diameter_max_um":31.5,"comparison_note":"multiple fitted modes; current 61.75 um-voxel carbonate PNM is biased to much larger resolved bodies/throats"},
        {"benchmark_group":"sandstones","physical_datasets":17,"reported_distribution_components":23,"mean_pore_diameter_min_um":0.019,"mean_pore_diameter_max_um":3.648,"comparison_note":"many submicrometre modes; current CT/PNM object populations omit much of this fine-pore domain"},
        {"benchmark_group":"shales","physical_datasets":4,"reported_distribution_components":8,"mean_pore_diameter_min_um":0.004,"mean_pore_diameter_max_um":0.112,"comparison_note":"nanometre/submicrometre fitted modes; W23 modelled curve is not a direct observed body distribution"},
        {"benchmark_group":"crystalline rocks","physical_datasets":0,"reported_distribution_components":0,"mean_pore_diameter_min_um":"","mean_pore_diameter_max_um":"","comparison_note":"not represented in Supplementary Table S2; benchmark cannot validate granite, basalt, gabbro or serpentinite directly"},
    ]


def make_plots(source_rows: list[dict], lith_rows: list[dict], geometry_rows: list[dict], porosity_rows: list[dict]) -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 13, "axes.labelsize": 11, "legend.fontsize": 9, "svg.fonttype": "none"})

    # Evidence depth: the log object axis is deliberately separate from replication counts.
    labels = [r["source_id"] for r in source_rows]
    x = np.arange(len(labels)); width = .25
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x-width, [r["distinct_reported_geological_locations_or_formations"] for r in source_rows], width, label="reported natural locations/formations")
    ax.bar(x, [r["physical_specimens_or_cases"] for r in source_rows], width, label="physical specimens/cases")
    ax.bar(x+width, [r["geometry_measurement_records"] for r in source_rows], width, label="size measurements")
    ax.set_ylabel("Count (independent evidence units)"); ax.set_xticks(x, labels, rotation=35, ha="right")
    ax2 = ax.twinx(); ax2.plot(x, [r["geometry_observations_bins_or_objects"] for r in source_rows], "ko--", label="objects/bins")
    ax2.set_yscale("log"); ax2.set_ylabel("Extracted objects or distribution bins (log scale)")
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax.legend(h1+h2,l1+l2,loc="upper left",frameon=False)
    ax.set_title("M3 geological evidence depth: replication is not object count")
    ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig(PLOTS/"geological_evidence_depth.svg"); plt.close(fig)

    # Coordinate-supported map; regional-only and laboratory records are named in the caption/report, not given invented points.
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.set_xlim(-180,180); ax.set_ylim(-70,85); ax.set_xticks(np.arange(-180,181,60)); ax.set_yticks(np.arange(-60,81,30))
    ax.grid(color="#ccd4dc", linewidth=.7); ax.axhline(0,color="#9aa7b2",linewidth=.8)
    colors={"M3-001":"#8c564b","M3-RLD-004":"#d62728","M3-025":"#1f77b4"}
    for name, source, lat, lon, support, state in SITES:
        ax.scatter(lon,lat,s=45,color=colors[source],edgecolor="white",linewidth=.7,zorder=3)
    ax.annotate("Lipnice MEL-5",(15.410324,49.620716),xytext=(8,7),textcoords="offset points")
    ax.annotate("Sellafield BH13B",(-3.47205018,54.38815261),xytext=(-85,8),textcoords="offset points")
    ax.annotate("Atlantis Massif\n(5 boreholes)",(-42.11,30.145),xytext=(-85,-35),textcoords="offset points")
    ax.set_xlabel("Longitude (degrees)"); ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Coordinate-supported natural sampling coverage")
    ax.text(.01,.02,"Only source-supported point locations are plotted. Region-only and unknown-origin sources are not assigned coordinates.",transform=ax.transAxes,fontsize=9)
    fig.tight_layout(); fig.savefig(PLOTS/"global_sampling_map.svg"); plt.close(fig)

    # Porosity context: concise source/type ranges for legibility; sample rows
    # remain available in porosity_audit.csv.
    selected={"MIP_connected_total","total","connected","CT_total","CT_image","CT_total_porosity","CT_connected_porosity","wet_dry_bulk"}
    grouped_porosity=defaultdict(list)
    for row in porosity_rows:
        if row["porosity_type"] in selected:
            grouped_porosity[(row["source_id"],row["porosity_type"])].append(float(row["porosity_percent"]))
    plot_rows=[]
    for key,values in sorted(grouped_porosity.items()):
        plot_rows.append((key[0],key[1],min(values),float(np.median(values)),max(values),len(values)))
    fig, ax = plt.subplots(figsize=(10, 5.8))
    source_order=list(dict.fromkeys(r[0] for r in plot_rows)); color_map=dict(zip(source_order,plt.cm.tab10.colors))
    for i,(source,kind,lo,med,hi,n) in enumerate(plot_rows):
        ax.plot([lo,hi],[i,i],color=color_map[source],lw=2.5)
        ax.scatter(med,i,color=color_map[source],s=45,zorder=3)
    ax.set_yticks(range(len(plot_rows)),[f"{source} · {kind} · n={n}" for source,kind,lo,med,hi,n in plot_rows],fontsize=8.5)
    ax.set_xlabel("Source-reported porosity (%)"); ax.set_title("Porosity context: total, connected, CT-resolved, and bulk values remain distinct")
    ax.grid(axis="x",alpha=.25); fig.tight_layout(); fig.savefig(PLOTS/"porosity_context.svg"); plt.close(fig)

    # Source/geometry summaries of sample medians; the range gives
    # between-sample variation without shrinking 57 labels beyond mobile use.
    eligible=[r for r in geometry_rows if r["quantity_name"] != "PORE-SIZE"]
    geometry_groups=defaultdict(list)
    for row in eligible:
        key=(row["source_id"],row["lithology"],row["geometry_class_native"],row["native_unit"],row["weighting_basis"])
        geometry_groups[key].append(float(row["median_um"]))
    display=[]
    for key,values in sorted(geometry_groups.items()):
        display.append((key,min(values),float(np.median(values)),max(values),len(values)))
    fig, ax = plt.subplots(figsize=(11, 6.8))
    geom_colors={"pore_body":"#2a9d8f","pore_throat":"#e76f51","matrix_pore":"#6a4c93"}
    for i,(key,lo,med,hi,n) in enumerate(display):
        geometry=key[2]
        ax.plot([lo,hi],[i,i],color=geom_colors.get(geometry,"#555"),lw=2.5)
        ax.scatter(med,i,color=geom_colors.get(geometry,"#555"),s=40,zorder=3)
    ax.set_xscale("log"); ax.set_xlabel("Source length converted to µm (radius, diameter, or MIP entry size as labelled)")
    def convention(key):
        if key[0] == "M3-001": return "entry equivalent"
        if "radius" in key[3].lower(): return "radius"
        if "diameter" in key[3].lower(): return "diameter"
        return "source length"
    ax.set_yticks(range(len(display)),[f"{key[0]} · {key[1]} · {key[2]} · n={n}\n{convention(key)} · {key[4]}" for key,lo,med,hi,n in display],fontsize=8)
    ax.set_title("Native pore-geometry summaries (equal-sample median and sample range)")
    ax.grid(axis="x",which="both",alpha=.25); fig.tight_layout(); fig.savefig(PLOTS/"sample_geometry_summaries.svg"); plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    geometry_rows, groups, measurement_counts, lithology_measurement_counts = read_geometry()
    source_rows, lith_rows = build_coverage(measurement_counts, lithology_measurement_counts)
    porosity_rows = build_porosity()
    lipnice_rows = build_lipnice()
    sites_rows = [{"site_or_borehole":x[0],"source_id":x[1],"latitude":x[2],"longitude":x[3],"coordinate_support":x[4],"material_class":x[5]} for x in SITES]
    write_csv(OUT/"coverage_by_source.csv", source_rows)
    write_csv(OUT/"coverage_by_lithology.csv", lith_rows)
    write_csv(OUT/"sample_geometry_summary.csv", geometry_rows)
    write_csv(OUT/"porosity_audit.csv", porosity_rows)
    write_csv(OUT/"lipnice_specimen_classification.csv", lipnice_rows)
    write_csv(OUT/"geographic_sites.csv", sites_rows)
    write_csv(OUT/"park_santamarina_benchmark_summary.csv", benchmark_rows())
    write_csv(OUT/"mip_porosity_aware_overlap.csv", build_mip_porosity_overlap(groups))
    write_csv(OUT/"connectivity_summary.csv", build_connectivity_summary())
    write_csv(OUT/"source_discrepancies.csv", source_discrepancies())
    make_plots(source_rows, lith_rows, geometry_rows, porosity_rows)
    manifest = {
        "status": "scientific audit overlay; source data and prior analysis unchanged",
        "independent_publications": len(SOURCE_META),
        "source_rows": len(source_rows), "lithology_rows": len(lith_rows),
        "sample_geometry_summary_rows": len(geometry_rows), "porosity_rows": len(porosity_rows),
        "coordinate_supported_points": len(SITES),
        "raw_geometry_rows_audited": sum(int(r["geometry_observations_bins_or_objects"]) for r in source_rows),
        "park_santamarina_si_sha256": "638c29fada973653315c681d3fb6b689ef977ca1fe4b5a6c12fc27873e6e3e07",
    }
    (OUT/"audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,sort_keys=True))


if __name__ == "__main__":
    main()
