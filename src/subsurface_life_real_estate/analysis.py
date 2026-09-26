"""Offline exploratory summaries for the full morphology census.

This module deliberately does not derive cell volumes, diameters, or geometric
models.  It reports parsed source dimensions and makes each analytical inclusion
rule explicit in the output metadata.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import math
import os
from pathlib import Path
from statistics import fmean, median, stdev

os.environ.setdefault("MPLCONFIGDIR", "/tmp/subsurface-life-real-estate-mpl")

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency

from .acquisition import digest, json_bytes


DIMENSIONS = {
    "length_min_um": "reported minimum length",
    "length_max_um": "reported maximum length",
    "width_min_um": "reported minimum width",
    "width_max_um": "reported maximum width",
}
THRESHOLDS = (0.2, 0.3, 0.5, 1.0, 2.0, 5.0)
PERCENTILES = (1, 5, 10, 25, 50, 75, 90, 95, 99)
COMPLEX_CLASSES = {
    "pleomorphic",
    "filamentous",
    "branched",
    "stalked_appendaged",
    "aggregate_chain_forming",
    "spore_related_measurement",
    "multiple_conflicting_observations",
    "ambiguous_or_unparsable",
}


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _csv_bytes(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    stream = __import__("io").StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _taxon(row: dict, rank: str) -> str:
    """Use original BacDive taxonomy for coverage, never resolve a disagreement."""
    value = row.get("taxonomy_raw", {}).get(rank)
    return value if isinstance(value, str) and value else "unreported"


def _domain(row: dict) -> str:
    value = row.get("taxonomy_raw", {}).get("domain")
    return value if value in {"Bacteria", "Archaea"} else "unreported"


def _clean_axis(row: dict, dimension: str) -> bool:
    """Numeric observation usable as a reported dimension without geometry assumptions."""
    if row.get(dimension) is None or not row.get("observation_present"):
        return False
    classes = set(row.get("morphology_classes", []))
    return not (classes & COMPLEX_CLASSES)


def _value(row: dict, measure: str) -> float | None:
    if measure in DIMENSIONS:
        return row[measure]
    if measure == "length_midpoint_um":
        lower, upper = row["length_min_um"], row["length_max_um"]
    else:
        lower, upper = row["width_min_um"], row["width_max_um"]
    return None if lower is None or upper is None else (lower + upper) / 2


def _summary(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "minimum": None, "maximum": None, "mean": None,
                "median": None, "standard_deviation": None, "percentiles": {},
                "fractions_at_or_below": {str(x): None for x in THRESHOLDS}}
    array = np.asarray(values, dtype=float)
    return {
        "n": int(array.size),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
        "mean": float(fmean(values)),
        "median": float(median(values)),
        "standard_deviation": float(stdev(values)) if len(values) > 1 else 0.0,
        "percentiles": {str(p): float(np.percentile(array, p)) for p in PERCENTILES},
        "fractions_at_or_below": {str(x): float((array <= x).mean()) for x in THRESHOLDS},
    }


def _cramers_v(table: np.ndarray, statistic: float) -> float | None:
    n = table.sum()
    denominator = n * min(table.shape[0] - 1, table.shape[1] - 1)
    return float(math.sqrt(statistic / denominator)) if denominator else None


def _coverage(strains: dict[str, list[dict]], rank: str = "phylum", minimum: int = 50) -> tuple[list[dict], dict]:
    groups = defaultdict(list)
    for strain_rows in strains.values():
        groups[_taxon(strain_rows[0], rank)].append(strain_rows)
    eligible = {name: rows for name, rows in groups.items() if len(rows) >= minimum}
    other = [rows for name, rows in groups.items() if name not in eligible]
    if other:
        eligible["Other / small groups"] = [item for group in other for item in group]
    output = []
    for group, group_rows in sorted(eligible.items()):
        total = len(group_rows)
        with_any = sum(any(r["observation_present"] for r in record) for record in group_rows)
        with_shape = sum(any(r["cell_shape_raw"] not in (None, "") for r in record) for record in group_rows)
        with_length = sum(any(r["length_min_um"] is not None for r in record) for record in group_rows)
        with_width = sum(any(r["width_min_um"] is not None for r in record) for record in group_rows)
        output.append({"rank": rank, "group": group, "eligible_strains": total,
                       "with_any_morphology": with_any, "with_shape": with_shape,
                       "with_normalized_length": with_length, "with_normalized_width": with_width,
                       "morphology_coverage_fraction": with_any / total,
                       "width_coverage_fraction": with_width / total})
    table = np.array([[r["with_any_morphology"], r["eligible_strains"] - r["with_any_morphology"]] for r in output], dtype=int)
    test = {"rank": rank, "minimum_group_size": minimum, "groups": len(output),
            "interpretation": "Association test for morphology availability by original BacDive taxonomic group; it does not establish biological cause."}
    if table.shape[0] >= 2 and np.all(table.sum(axis=0) > 0):
        result = chi2_contingency(table, correction=False)
        test.update({"chi_square": float(result.statistic), "degrees_of_freedom": int(result.dof),
                     "p_value": float(result.pvalue), "cramers_v": _cramers_v(table, result.statistic),
                     "minimum_expected_frequency": float(result.expected_freq.min()),
                     "expected_frequency_caution": bool((result.expected_freq < 5).any())})
    return output, test


def _species_rows(strains: dict[str, list[dict]]) -> list[dict]:
    groups = defaultdict(list)
    for bacdive_id, record in strains.items():
        name = _taxon(record[0], "species")
        groups[name].append((bacdive_id, record))
    output = []
    for species, members in sorted(groups.items()):
        rows = [row for _, record in members for row in record]
        output.append({
            "species_name_raw_bacdive": species,
            "bacdive_type_strain_record_count": len(members),
            "bacdive_ids": json.dumps(sorted(bid for bid, _ in members), separators=(",", ":")),
            "domain_raw_bacdive_values": json.dumps(sorted({_domain(row) for row in rows}), separators=(",", ":")),
            "phylum_raw_bacdive_values": json.dumps(sorted({_taxon(row, "phylum") for row in rows}), separators=(",", ":")),
            "morphology_observation_count": sum(row["observation_present"] for row in rows),
            "records_with_any_normalized_length": sum(any(row["length_min_um"] is not None for row in record) for _, record in members),
            "records_with_any_normalized_width": sum(any(row["width_min_um"] is not None for row in record) for _, record in members),
            "lpsn_validation_states": json.dumps(sorted({row.get("nomenclature_validation_status", "unavailable") for row in rows}), separators=(",", ":")),
            "note": "Species-level index only. It does not average or select morphology observations.",
        })
    return output


def _outliers(rows: list[dict], limit: int = 50) -> list[dict]:
    result = []
    for measure in DIMENSIONS:
        values = [row for row in rows if row.get(measure) is not None]
        for direction, selected in (("smallest", sorted(values, key=lambda r: (r[measure], int(r["bacdive_id"])))[:limit]),
                                    ("largest", sorted(values, key=lambda r: (-r[measure], int(r["bacdive_id"])))[:limit])):
            for rank, row in enumerate(selected, 1):
                review = set(row["qc_flag"]) | set(row.get("morphology_classes", []))
                value = row[measure]
                if value < 0.1:
                    review.add("below_0_1_um_review")
                if measure.startswith("width") and value > 100:
                    review.add("large_width_over_100_um_review")
                if measure.startswith("length") and value > 100:
                    review.add("extreme_length_over_100_um_review")
                other_axis = row["length_max_um"] if measure.startswith("width") else row["width_max_um"]
                if other_axis is not None and min(value, other_axis) > 0 and max(value, other_axis) / min(value, other_axis) >= 100:
                    review.add("possible_unit_or_scale_discrepancy_review")
                result.append({
                    "measure": measure, "tail": direction, "tail_rank": rank,
                    "species_name_raw_bacdive": _taxon(row, "species"), "bacdive_id": row["bacdive_id"],
                    "lpsn_status": row.get("lpsn_csv_status_raw"), "cell_shape_raw": row["cell_shape_raw"],
                    "cell_length_raw": row["cell_length_raw"], "cell_width_raw": row["cell_width_raw"],
                    "normalized_value_um": value, "source_reference": json.dumps(row["source_reference"], ensure_ascii=False),
                    "morphology_classes": json.dumps(row.get("morphology_classes", [])),
                    "qc_flags": json.dumps(row["qc_flag"]),
                    "review_flags": json.dumps(sorted(review)),
                })
    return result


def _ecdf(rows: list[dict]) -> list[dict]:
    values = sorted(row["width_min_um"] for row in rows if _clean_axis(row, "width_min_um"))
    return [{"width_um": value, "observation_rank": rank, "ecdf": rank / len(values),
             "conditioning_population": "parsed width observations without provisional complex/conflicting/ambiguous morphology classes"}
            for rank, value in enumerate(values, 1)]


def _plot_coverage(coverage: list[dict], path: Path) -> None:
    labels = [row["group"] for row in coverage]
    values = [row["morphology_coverage_fraction"] for row in coverage]
    fig, axis = plt.subplots(figsize=(max(8, len(labels) * 0.45), 5))
    axis.bar(range(len(labels)), values, color="#3f7cac")
    axis.set_ylim(0, 1)
    axis.set_ylabel("Fraction with any structured morphology")
    axis.set_xticks(range(len(labels)), labels, rotation=60, ha="right")
    axis.set_title("Morphology reporting coverage by original BacDive phylum")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_ecdf(ecdf: list[dict], path: Path) -> None:
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.step([r["width_um"] for r in ecdf], [r["ecdf"] for r in ecdf], where="post", color="#3f7cac")
    axis.set_xscale("log")
    axis.set_xlabel("Reported minimum width (µm; logarithmic scale)")
    axis.set_ylabel("Empirical cumulative fraction")
    axis.set_title("ECDF of clean reported cell widths")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def analyze(observations_path: str | Path, output_dir: str | Path) -> dict:
    """Write deterministic exploratory products from processed observation JSONL."""
    rows = _jsonl(Path(observations_path))
    strains = defaultdict(list)
    for row in rows:
        strains[row["bacdive_id"]].append(row)
    species = _species_rows(strains)
    multiple_species = [row for row in species if row["bacdive_type_strain_record_count"] > 1]
    coverage, bias = _coverage(strains)
    measures = {**DIMENSIONS, "length_midpoint_um": "length midpoint", "width_midpoint_um": "width midpoint"}
    distribution = {}
    for measure, label in measures.items():
        axis = "length" if measure.startswith("length") else "width"
        selected = [row for row in rows if _clean_axis(row, f"{axis}_min_um") and _value(row, measure) is not None]
        phyla = defaultdict(list)
        for row in selected:
            phyla[_taxon(row, "phylum")].append(_value(row, measure))
        distribution[measure] = {"label": label, "clean_rule": "Parsed dimension with no provisional complex, conflicting, or ambiguous morphology class; values remain source-observation level.",
                                 "all_prokaryotes": _summary([_value(row, measure) for row in selected]),
                                 "Bacteria": _summary([_value(row, measure) for row in selected if _domain(row) == "Bacteria"]),
                                 "Archaea": _summary([_value(row, measure) for row in selected if _domain(row) == "Archaea"]),
                                 "major_original_bacdive_phyla": {
                                     phylum: _summary(values) for phylum, values in sorted(phyla.items())
                                     if len(values) >= 50
                                 }}
    ecdf = _ecdf(rows)
    classes = Counter(label for row in rows for label in row.get("morphology_classes", []))
    outputs = {
        "species_analytical_index.csv": _csv_bytes(species),
        "taxonomic_coverage.csv": _csv_bytes(coverage),
        "outlier_review.csv": _csv_bytes(_outliers(rows)),
        "width_ecdf.csv": _csv_bytes(ecdf),
        "exploratory_distributions.json": json_bytes(distribution),
        "morphology_qc.json": json_bytes({"observation_class_counts": dict(sorted(classes.items())),
                                             "clean_width_observations": len(ecdf),
                                             "clean_width_rule": distribution["width_min_um"]["clean_rule"]}),
        "taxonomic_bias.json": json_bytes(bias),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, body in outputs.items():
        _write(output / name, body)
    plots = output / "plots"
    plots.mkdir(exist_ok=True)
    _plot_coverage(coverage, plots / "phylum_morphology_coverage.png")
    _plot_ecdf(ecdf, plots / "width_ecdf.png")
    summary = {"observation_rows": len(rows), "strain_count": len(strains),
               "species_group_count": len(species),
               "species_groups_with_multiple_bacdive_type_strain_records": len(multiple_species),
               "additional_records_in_multiple_record_species_groups": sum(
                   row["bacdive_type_strain_record_count"] - 1 for row in multiple_species),
               "distribution": distribution,
               "taxonomic_bias": bias, "clean_width_ecdf_n": len(ecdf),
               "source_observations_sha256": digest(Path(observations_path).read_bytes()),
               "outputs_sha256": {name: digest(body) for name, body in outputs.items()}}
    _write(output / "analysis_summary.json", json_bytes(summary))
    return summary
