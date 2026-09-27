"""Create publication-oriented, source-weighted M3 pore × microbe figures.

The figures are visual summaries only.  They do not pool geological objects
across sources, harmonise method weighting, or infer accessibility.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "data/interim/matplotlib"))

import matplotlib.pyplot as plt
import numpy as np

GEOMETRY = ROOT / "data/processed/reference_lithology_dataset_v1/geometry_values.csv"
MICROBES = ROOT / "data/processed/census_2026-09-14/scientific_qc_v1/species_analytical_table.csv"
OUT = ROOT / "data/processed/reference_lithology_dataset_v1/analysis/plots"
WIDTH_COLUMN = "corrected_width_midpoint_um"
LOG_BINS = np.logspace(-3, 5, 57)
GRID = np.logspace(-3, 5, 240)

SOURCE_LABELS = {
    ("M3-001", "granite"): "Lipnice granite — MIP entry",
    ("M3-002", "sandstone"): "Fontainebleau/Berea — CT/PNM (0.74 µm)",
    ("M3-RLD-003", "carbonate"): "South China Sea carbonate — PNM (window unreported)",
    ("M3-RLD-003", "sandstone"): "South China Sea sandstone — PNM (window unreported)",
    ("M3-005", "basalt_volcanic"): "Unreacted basalt — CT (14.99 µm)",
    ("M3-RLD-004", "sandstone"): "Wilmslow sandstone — PNM (window unreported)",
    ("M3-023", "mudstone_shale"): "W23 shale — modelled pore cluster",
    ("M3-024", "unconsolidated_sand"): "F42A quartz sand — CT/PNM (9.996 µm)",
}
COLORS = {
    "granite": "#5b6c99", "sandstone": "#d06f4c", "carbonate": "#287271",
    "basalt_volcanic": "#7f3c8d", "mudstone_shale": "#3c78a8",
    "unconsolidated_sand": "#9a7d0a",
}


def microbial_widths() -> np.ndarray:
    values = []
    with MICROBES.open() as handle:
        for row in csv.DictReader(handle):
            if (row["canonical_selection_status"] == "canonical" and
                    row["canonical_nomenclature_validation_status"] == "validated_name_and_type"):
                values.append(float(row[WIDTH_COLUMN]))
    return np.asarray(sorted(values))


def geological_groups() -> dict[tuple[str, str, str], dict[str, tuple[np.ndarray, np.ndarray]]]:
    grouped: dict[tuple[str, str, str], dict[str, list[list[float]]]] = defaultdict(lambda: defaultdict(lambda: [[], []]))
    with GEOMETRY.open() as handle:
        for row in csv.DictReader(handle):
            if not row["comparison_diameter_um"] or "source_missing_weight" in row["qc_flags"]:
                continue
            role = row["comparison_role"]
            if role not in {"pore_body_accommodation", "modelled_matrix_pore_cluster_accommodation", "throat_entry_nominal_transit"}:
                continue
            key = (row["source_id"], row["lithology"], role)
            grouped[key][row["sample_id"]][0].append(float(row["comparison_diameter_um"]))
            grouped[key][row["sample_id"]][1].append(float(row["weight_raw"]))
    return {key: {sample: (np.asarray(items[0]), np.asarray(items[1])) for sample, items in samples.items()} for key, samples in grouped.items()}


def source_curve(samples: dict[str, tuple[np.ndarray, np.ndarray]], grid: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    curves = []
    for dimensions, weights in samples.values():
        order = np.argsort(dimensions)
        dimensions, weights = dimensions[order], weights[order]
        cumulative = np.cumsum(weights) / weights.sum()
        curves.append(1 - np.interp(grid, dimensions, cumulative, left=0, right=1))
    values = np.asarray(curves)
    return np.median(values, axis=0), np.min(values, axis=0), np.max(values, axis=0)


def source_histogram(samples: dict[str, tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    # Equal-sample mean prevents the largest extracted network dominating.
    rows = []
    for dimensions, weights in samples.values():
        rows.append(np.histogram(dimensions, bins=LOG_BINS, weights=weights / weights.sum())[0])
    return np.mean(rows, axis=0)


def microbial_guides(axis: plt.Axes, widths: np.ndarray) -> None:
    p5, median, p95 = np.quantile(widths, [0.05, 0.5, 0.95])
    axis.axvspan(p5, p95, color="#222222", alpha=0.08, zorder=0)
    axis.axvline(median, color="#222222", lw=1.4, ls="--", zorder=1)


def plot_size_distributions(widths: np.ndarray, groups: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.1), sharex=True)
    micro_hist = np.histogram(widths, bins=LOG_BINS, weights=np.ones_like(widths) / len(widths))[0]
    for axis, roles, title in [
        (axes[0], {"pore_body_accommodation", "modelled_matrix_pore_cluster_accommodation"}, "Accommodation: pore body / pore cluster"),
        (axes[1], {"throat_entry_nominal_transit"}, "Nominal transit: throat / entry constriction"),
    ]:
        axis.stairs(micro_hist, LOG_BINS, color="#202020", lw=2.2, label="Cultured species width (midpoint)")
        for (source, lithology, role), samples in sorted(groups.items()):
            if role not in roles:
                continue
            axis.stairs(source_histogram(samples), LOG_BINS, color=COLORS[lithology], lw=1.55,
                        label=SOURCE_LABELS[(source, lithology)])
        microbial_guides(axis, widths)
        axis.set_xscale("log")
        axis.set_ylim(bottom=0)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel("Comparison diameter / microbial width (µm; log scale)")
        axis.grid(axis="y", alpha=0.2)
        axis.legend(fontsize=7, frameon=False, loc="upper right")
    axes[0].set_ylabel("Within-source weighted fraction per log bin")
    fig.suptitle("Pore × microbe size distributions: source weighting retained", x=0.06, ha="left", fontsize=15, fontweight="bold")
    fig.text(0.06, 0.01, "Grey band = cultured midpoint-width 5th–95th percentile; dashed line = median. Geological lines are not pooled or cross-method ranked.", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(OUT / "pore_microbe_size_distributions.svg", format="svg")
    plt.close(fig)


def plot_compatibility_landscape(widths: np.ndarray, groups: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.1), sharex=True, sharey=True)
    for axis, roles, title in [
        (axes[0], {"pore_body_accommodation", "modelled_matrix_pore_cluster_accommodation"}, "Accommodation landscape"),
        (axes[1], {"throat_entry_nominal_transit"}, "Nominal transit landscape"),
    ]:
        for (source, lithology, role), samples in sorted(groups.items()):
            if role not in roles:
                continue
            median, low, high = source_curve(samples, GRID)
            color = COLORS[lithology]
            label = SOURCE_LABELS[(source, lithology)]
            axis.plot(GRID, median, color=color, lw=1.7, label=label)
            if len(samples) > 1:
                axis.fill_between(GRID, low, high, color=color, alpha=0.12)
        microbial_guides(axis, widths)
        axis.set_xscale("log")
        axis.set_ylim(0, 1.02)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel("Cultured microbial width threshold (µm; log scale)")
        axis.grid(alpha=0.2)
        axis.legend(fontsize=7, frameon=False, loc="upper right")
    axes[0].set_ylabel("Within-source P(comparison diameter ≥ width)")
    fig.suptitle("Compatibility landscape: measured size larger than microbial width", x=0.06, ha="left", fontsize=15, fontweight="bold")
    fig.text(0.06, 0.01, "Lines are equal-sample medians; shaded envelopes show sample range. This is geometry only—not connectivity, accessibility, or habitability.", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(OUT / "pore_microbe_compatibility_landscape.svg", format="svg")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    widths, groups = microbial_widths(), geological_groups()
    plot_size_distributions(widths, groups)
    plot_compatibility_landscape(widths, groups)
    print(f"OK: {len(widths)} cultured species; {len(groups)} source/lithology/role groups")


if __name__ == "__main__":
    main()
