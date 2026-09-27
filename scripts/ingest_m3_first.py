"""Create source-preserving M3 first-ingestion tables from local raw artifacts.

Raw inputs are deliberately kept under data/raw/ (gitignored).  This script is
small on purpose: it supports the two tabular sources actually acquired for
the first review, rather than pretending to be a general pore-data framework.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/m3_acquisitions"
OUT = ROOT / "data/processed/m3_first_ingestion"
PLOTS = OUT / "analysis/plots"

SAMPLES = [
    "sample_id", "source_id", "source_sample_id", "lithology_class",
    "lithology_description_raw", "sample_state", "collection_context",
    "material_scale_context",
]
MEASUREMENTS = [
    "measurement_id", "sample_id", "method", "method_variant_raw",
    "geometry_class", "quantity_name_raw", "quantity_role",
    "size_definition_raw", "value_unit", "distribution_reference",
    "resolution_or_detection_limit_raw", "segmentation_or_model_raw",
    "connectivity_definition_raw", "provenance_locator", "qc_flags",
    "comparability_group",
]
DIST = [
    "measurement_id", "bin_id", "bin_lower_raw", "bin_upper_raw",
    "bin_unit_raw", "bin_lower_um", "bin_upper_um", "value_raw",
    "value_normalized", "value_unit_raw", "value_type", "weighting_basis",
    "source_column_raw",
]
OBJECTS = [
    "measurement_id", "object_id_raw", "geometry_class", "radius_raw",
    "radius_unit_raw", "radius_um", "volume_raw", "volume_unit_raw",
    "volume_um3", "area_raw", "area_unit_raw", "area_um2",
    "channel_length_raw", "channel_length_unit_raw", "channel_length_um",
    "coordination_number_raw", "source_file", "qc_flags",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader(); writer.writerows(rows)


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pangaea_rows(samples: list[dict], measurements: list[dict], dist: list[dict]) -> list[dict]:
    path = RAW / "pangaea_898001/pangaea_898001.tab"
    lines = path.read_text(encoding="utf-8").splitlines()
    header_at = next(i for i, line in enumerate(lines) if line.startswith("Depth sed [m]"))
    reader = csv.DictReader(lines[header_at:], delimiter="\t")
    output = []
    for row in reader:
        specimen = row["Sample label (specimen name)"]
        if not specimen:
            continue
        sample_id = f"M3-001:{specimen}"
        samples.append({
            "sample_id": sample_id, "source_id": "M3-001", "source_sample_id": specimen,
            "lithology_class": "plutonic_crystalline", "lithology_description_raw": "Lipnice granite",
            "sample_state": row["Facies (granite facies)"],
            "collection_context": f"MEL-5 borehole; depth {row['Depth sed [m]']} m",
            "material_scale_context": "matrix_adjacent_to_fracture_and_alteration_facies",
        })
        measurement_id = f"{sample_id}:mip_intrusion"
        measurements.append({
            "measurement_id": measurement_id, "sample_id": sample_id, "method": "MIP",
            "method_variant_raw": "Mercury intrusion porosimetry",
            "geometry_class": "pore_throat", "quantity_name_raw": "Porosity, incremental, during intrusion",
            "quantity_role": "throat_or_entry_equivalent",
            "size_definition_raw": "MIP entry/throat-equivalent size; source bin labels",
            "value_unit": "%", "distribution_reference": "pangaea_898001.tab: intrusion columns",
            "resolution_or_detection_limit_raw": "0.008–309 µm binned instrumental entry-equivalent range",
            "segmentation_or_model_raw": "Mercury intrusion; Washburn-model assumptions not restated in tabular artifact",
            "connectivity_definition_raw": "not supplied", "provenance_locator": "PANGAEA.898001 tab file; row sample label",
            "qc_flags": "mip_entry_equivalent_not_pore_body;intrusion_only;reintrusion_not_ingested",
            "comparability_group": "MIP_entry_equivalent_intrusion",
        })
        for column, raw in row.items():
            match = re.fullmatch(r"Poros increm intrus \(([^-]+)-([^ ]+) µm\)", column or "")
            if not match or not raw:
                continue
            high, low = map(float, match.groups())
            value = number(raw)
            if value is None:
                continue
            dist.append({
                "measurement_id": measurement_id, "bin_id": f"intrusion:{low:g}-{high:g}",
                "bin_lower_raw": low, "bin_upper_raw": high, "bin_unit_raw": "µm",
                "bin_lower_um": low, "bin_upper_um": high, "value_raw": raw,
                "value_normalized": value, "value_unit_raw": "%", "value_type": "incremental_intrusion_porosity",
                "weighting_basis": "incremental_intruded_porosity", "source_column_raw": column,
            })
    return output


def field(row: dict, name: str) -> str:
    for key, value in row.items():
        if key.replace("�", "µ").strip() == name:
            return value
    return ""


def zenodo_rows(samples: list[dict], measurements: list[dict], objects: list[dict]) -> None:
    directory = RAW / "zenodo_1184144"
    cases = {"Case1FB": ("Fontainebleau sandstone", "case label only; state not supplied in file"),
             "Case2B": ("Berea sandstone", "case label only; state not supplied in file"),
             "Case3B": ("Berea sandstone", "case label only; state not supplied in file")}
    for case, (rock, state) in cases.items():
        sample_id = f"M3-002:{case}"
        samples.append({
            "sample_id": sample_id, "source_id": "M3-002", "source_sample_id": case,
            "lithology_class": "sedimentary_siliciclastic", "lithology_description_raw": rock,
            "sample_state": state, "collection_context": "record-level PNM case; exact specimen metadata not present in CSV",
            "material_scale_context": "matrix_pore_network",
        })
        for suffix, geometry in (("Pores", "pore_body"), ("Throats", "pore_throat")):
            filename = f"{case}{suffix}.csv"; path = directory / filename
            measurement_id = f"{sample_id}:{geometry}"
            measurements.append({
                "measurement_id": measurement_id, "sample_id": sample_id,
                "method": "micro_CT_plus_PNM", "method_variant_raw": "Pore network modeling data",
                "geometry_class": geometry,
                "quantity_name_raw": "EqRadius [µm]" if geometry == "pore_body" else "EqRadius [µm]; ChannelLength [µm]",
                "quantity_role": "body" if geometry == "pore_body" else "throat_or_entry_equivalent",
                "size_definition_raw": "EqRadius as named in source CSV; no conversion to diameter",
                "value_unit": "µm", "distribution_reference": filename,
                "resolution_or_detection_limit_raw": "not supplied in CSV; consult record metadata before cross-source use",
                "segmentation_or_model_raw": "network-extraction settings not supplied in CSV",
                "connectivity_definition_raw": "Coordination Number" if geometry == "pore_body" else "pore-pair edge table",
                "provenance_locator": f"Zenodo 1184144 v1; {filename}",
                "qc_flags": "radius_not_diameter;ct_pnm_window_not_reported_in_csv",
                "comparability_group": "micro_CT_PNM_equivalent_radius",
            })
            header_has_replacement = "�" in path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            with path.open(encoding="utf-8", errors="replace", newline="") as handle:
                raw_reader = csv.reader(handle)
                header = next(raw_reader)
                # Case2's publisher CSV accidentally uses commas inside its
                # unquoted column labels. Its rows are nevertheless a compact,
                # consistently ordered object table; reconstruct only those
                # explicit labels rather than guessing from value magnitudes.
                malformed_case2 = header[:2] in (["#Pore", "ID"], ["#Throat", "ID"])
                if malformed_case2:
                    if geometry == "pore_body":
                        labels = ["#Pore ID", "Volume [µm^3]", "Area [µm^2]", "EqRadius [µm]", "LabelID", "X Coord [µm]", "Y Coord [µm]", "Z Coord [µm]", "Coordination Number"]
                    else:
                        labels = ["#Throat ID", "Area [µm^2]", "EqRadius [µm]", "ChannelLength [µm]", "Pore ID #1", "Pore ID #2"]
                    reader = (dict(zip(labels, values)) for values in raw_reader)
                else:
                    reader = (dict(zip(header, values)) for values in raw_reader)
                for row in reader:
                    radius = field(row, "EqRadius [µm]")
                    obj_id = field(row, "#Pore ID") or field(row, "#Throat ID")
                    objects.append({
                        "measurement_id": measurement_id, "object_id_raw": obj_id,
                        "geometry_class": geometry, "radius_raw": radius, "radius_unit_raw": "µm", "radius_um": number(radius),
                        "volume_raw": field(row, "Volume [µm^3]"), "volume_unit_raw": "µm^3" if geometry == "pore_body" else "",
                        "volume_um3": number(field(row, "Volume [µm^3]")), "area_raw": field(row, "Area [µm^2]"),
                        "area_unit_raw": "µm^2", "area_um2": number(field(row, "Area [µm^2]")),
                        "channel_length_raw": field(row, "ChannelLength [µm]"), "channel_length_unit_raw": "µm" if geometry == "pore_throat" else "",
                        "channel_length_um": number(field(row, "ChannelLength [µm]")),
                        "coordination_number_raw": field(row, "Coordination Number"), "source_file": filename,
                        "qc_flags": ";".join(x for x in (["source_header_contains_replacement_character" if header_has_replacement else "", "source_header_unquoted_commas_reconstructed" if malformed_case2 else ""]) if x),
                    })


def plots(dist: list[dict], objects: list[dict]) -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    def svg(path: Path, title: str, xlabel: str, ylabel: str, series: list[tuple[str, list[tuple[float, float]], str]]) -> None:
        # Tiny dependency-free log-x plotter: source-preserving figures should be
        # reproducible in the base Python environment.
        width, height, left, bottom = 760, 430, 76, 55
        all_x = [x for _, points, _ in series for x, _ in points if x > 0]
        all_y = [y for _, points, _ in series for _, y in points]
        lo, hi = min(map(__import__('math').log10, all_x)), max(map(__import__('math').log10, all_x))
        ymax = max(all_y) or 1
        def xy(x: float, y: float) -> tuple[float, float]:
            return left + (__import__('math').log10(x)-lo)/(hi-lo or 1)*(width-left-25), height-bottom-y/ymax*(height-bottom-55)
        pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                  '<rect width="100%" height="100%" fill="white"/>', f'<text x="{left}" y="25" font-family="sans-serif" font-size="16">{title}</text>',
                  f'<line x1="{left}" y1="{height-bottom}" x2="{width-25}" y2="{height-bottom}" stroke="#333"/><line x1="{left}" y1="45" x2="{left}" y2="{height-bottom}" stroke="#333"/>',
                  f'<text x="{width/2}" y="{height-12}" text-anchor="middle" font-family="sans-serif" font-size="12">{xlabel}</text>',
                  f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="sans-serif" font-size="12">{ylabel}</text>']
        for i, (label, points, color) in enumerate(series):
            coords = ' '.join(f'{a:.1f},{b:.1f}' for a,b in (xy(x,y) for x,y in points if x > 0))
            pieces += [f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.6"/>', f'<text x="{left+10}" y="{48+i*15}" font-family="sans-serif" font-size="11" fill="{color}">{label}</text>']
        pieces.append('</svg>'); path.write_text(''.join(pieces), encoding='utf-8')
    grouped = defaultdict(list)
    for row in dist: grouped[row["measurement_id"]].append(row)
    svg(PLOTS / "lipnice_mip_intrusion.svg", "Lipnice granite: per-specimen MIP intrusion distributions", "MIP entry/throat-equivalent bin centre (µm; log)", "Incremental intruded porosity (%)", [(m, [((float(r['bin_lower_um'])*float(r['bin_upper_um']))**.5, float(r['value_normalized'])) for r in rows], "#287271") for m, rows in sorted(grouped.items())])
    series = []
    for geometry, label, color in (("pore_body", "Pore-body EqRadius", "#287271"), ("pore_throat", "Pore-throat EqRadius", "#e07a5f")):
        values = sorted(float(r["radius_um"]) for r in objects if r["geometry_class"] == geometry and r["radius_um"] not in (None, ""))
        step = max(1, len(values) // 900)
        sampled = [(v, (i+1)/len(values)) for i, v in enumerate(values) if i % step == 0]
        if sampled[-1][0] != values[-1]: sampled.append((values[-1], 1.0))
        series.append((label, sampled, color))
    svg(PLOTS / "sandstone_pnm_radius_ecdf.svg", "Fontainebleau/Berea networks: bodies and throats remain separate", "Equivalent radius as supplied (µm; log)", "Empirical cumulative fraction", series)


def main() -> None:
    if not (RAW / "pangaea_898001/pangaea_898001.tab").is_file():
        raise SystemExit("Raw M3 artifacts are absent; acquire them before processing.")
    OUT.mkdir(parents=True, exist_ok=True)
    samples: list[dict] = []; measurements: list[dict] = []; dist: list[dict] = []; objects: list[dict] = []
    pangaea_rows(samples, measurements, dist); zenodo_rows(samples, measurements, objects)
    write_csv(OUT / "samples.csv", SAMPLES, samples)
    write_csv(OUT / "measurements.csv", MEASUREMENTS, measurements)
    write_csv(OUT / "measurement_distribution.csv", DIST, dist)
    write_csv(OUT / "network_objects.csv", OBJECTS, objects)
    raw_files = sorted(p for p in RAW.rglob("*") if p.is_file())
    manifest = {"run_id": "m3_first_ingestion_2026-09-26", "run_utc": datetime.now(timezone.utc).isoformat(),
                "raw_artifacts": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in raw_files],
                "outputs": {"samples": len(samples), "measurements": len(measurements), "distribution_rows": len(dist), "network_objects": len(objects)},
                "processing": "Source values retained; µm values copied where original units are µm. EqRadius was not converted to diameter."}
    (OUT / "processing_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plots(dist, objects)
    print(json.dumps(manifest["outputs"], sort_keys=True))


if __name__ == "__main__":
    main()
