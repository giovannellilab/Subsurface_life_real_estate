"""Create safe, descriptive M1 width, length, and simple-cell-volume figures.

The inputs are the existing Scientific QC v1 canonical species table.  This
script never edits source dimensions or uses volume for pore-throat transit.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/census_2026-09-14/scientific_qc_v1/species_analytical_table.csv"
OUT = ROOT / "data/processed/m1_geometry_resource_v1"
PLOTS = OUT / "plots"


def midpoint(row: dict, axis: str) -> float | None:
    low = row[f"corrected_{axis}_min_um"] or row[f"source_{axis}_min_um"]
    high = row[f"corrected_{axis}_max_um"] or row[f"source_{axis}_max_um"]
    if not low or not high:
        return None
    return (float(low) + float(high)) / 2


def stats(values: list[float]) -> dict:
    array = np.asarray(values, dtype=float)
    return {
        "n": len(array), "minimum": float(array.min()), "p5": float(np.percentile(array, 5)),
        "p25": float(np.percentile(array, 25)), "median": float(np.median(array)),
        "p75": float(np.percentile(array, 75)), "p95": float(np.percentile(array, 95)),
        "maximum": float(array.max()),
    }


def density(ax, values: list[float], label: str, color: str, bins: np.ndarray) -> None:
    counts, edges = np.histogram(values, bins=bins)
    width = np.diff(np.log10(edges))
    density_values = counts / counts.sum() / width
    ax.stairs(density_values, edges, label=label, color=color, linewidth=2.1)


def save_figure(path: Path, title: str, xlabel: str, ylabel: str) -> plt.Axes:
    fig, ax = plt.subplots(figsize=(10.4, 5.7))
    ax.set_xscale("log")
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(axis="x", which="both", alpha=.25)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return ax


def main() -> None:
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    strict = [r for r in rows if r["canonical_selection_status"] == "canonical" and r["canonical_nomenclature_validation_status"] == "validated_name_and_type"]
    if len(strict) != 4452:
        raise ValueError(f"Expected 4,452 strict canonical species, found {len(strict)}")

    widths = {metric: [
        float(r[f"corrected_width_{metric}_um"] or r[f"source_width_{metric}_um"])
        for r in strict
    ] for metric in ("min", "midpoint", "max")}
    lengths = [value for r in strict if (value := midpoint(r, "length")) is not None]

    volume_rows = []
    excluded = {"missing_one_or_both_axes": 0, "complex_or_unresolved_shape": 0, "length_shorter_than_width": 0}
    for row in strict:
        d, length = midpoint(row, "width"), midpoint(row, "length")
        if d is None or length is None:
            excluded["missing_one_or_both_axes"] += 1
            continue
        shape = row["shape_category"]
        if shape == "coccoid_or_spherical":
            volume_rows.append(("sphere", np.pi * d ** 3 / 6))
        elif shape == "rod":
            if length < d:
                excluded["length_shorter_than_width"] += 1
                continue
            # L is the reported total end-to-end length: cylinder length L-d,
            # plus two hemispheres with combined sphere volume.
            volume_rows.append(("spherocylinder", np.pi * (d / 2) ** 2 * (length - d) + np.pi * d ** 3 / 6))
        else:
            excluded["complex_or_unresolved_shape"] += 1
    volumes = [v for _, v in volume_rows]
    if not volumes:
        raise ValueError("No simple-cell volumes available")

    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 14, "axes.labelsize": 12, "svg.fonttype": "none"})
    width_bins = np.logspace(-4, 3, 70)
    fig, ax = plt.subplots(figsize=(10.4, 5.7))
    for metric, label, color in (
        ("min", "canonical minimum width", "#527da3"),
        ("midpoint", "canonical midpoint width (primary)", "#a34f28"),
        ("max", "canonical maximum width", "#5b8d58"),
    ):
        density(ax, widths[metric], label, color, width_bins)
    ax.set_xscale("log"); ax.set_xlim(0.01, 100); ax.set_ylim(bottom=0)
    ax.set_title("Cultured species canonical cell-width distributions", pad=12)
    ax.set_xlabel("Cell width (µm; log scale)"); ax.set_ylabel("Species density (per log10 µm)")
    ax.grid(axis="x", which="both", alpha=.25); ax.legend(frameon=False, fontsize=9)
    ax.text(.02, .96, "N = 4,452 strict LPSN-supported species\nMidpoint median 0.60 µm; p5–p95 0.30–1.25 µm", transform=ax.transAxes, va="top", fontsize=9)
    fig.tight_layout(); fig.savefig(PLOTS / "m1_species_width_distributions.svg"); plt.close(fig)

    length_bins = np.logspace(-2, 4, 70)
    fig, ax = plt.subplots(figsize=(10.4, 5.7)); density(ax, lengths, "canonical species length midpoint", "#6e5aa5", length_bins)
    ax.set_xscale("log"); ax.set_xlim(.05, 1e3); ax.set_ylim(bottom=0)
    ax.set_title("Cultured species canonical cell-length distribution", pad=12)
    ax.set_xlabel("Cell length midpoint (µm; log scale)"); ax.set_ylabel("Species density (per log10 µm)")
    ax.grid(axis="x", which="both", alpha=.25); ax.legend(frameon=False)
    ls = stats(lengths); ax.text(.02, .96, f"N = {len(lengths):,} strict canonical species\nMedian {ls['median']:.2f} µm; p5–p95 {ls['p5']:.2f}–{ls['p95']:.2f} µm", transform=ax.transAxes, va="top", fontsize=9)
    fig.tight_layout(); fig.savefig(PLOTS / "m1_species_length_distribution.svg"); plt.close(fig)

    volume_bins = np.logspace(-8, 10, 80)
    fig, ax = plt.subplots(figsize=(10.4, 5.7)); density(ax, volumes, "simple-cell equivalent volume", "#287271", volume_bins)
    ax.set_xscale("log"); ax.set_xlim(1e-5, 1e5); ax.set_ylim(bottom=0)
    ax.set_title("Descriptive equivalent single-cell volume for simple canonical morphologies", pad=12)
    ax.set_xlabel("Estimated single-cell volume (µm³; log scale)"); ax.set_ylabel("Species density (per log10 µm³)")
    ax.grid(axis="x", which="both", alpha=.25); ax.legend(frameon=False)
    vs = stats(volumes); ax.text(.02, .96, f"N = {len(volumes):,}: 3,765 rods + 180 cocci\nMedian {vs['median']:.3g} µm³; p5–p95 {vs['p5']:.3g}–{vs['p95']:.3g} µm³", transform=ax.transAxes, va="top", fontsize=9)
    fig.tight_layout(); fig.savefig(PLOTS / "m1_simple_cell_equivalent_volume.svg"); plt.close(fig)

    payload = {
        "population": "strict LPSN-supported canonical cultured species; source-derived dimensions only",
        "width_min_um": stats(widths["min"]), "width_midpoint_um": stats(widths["midpoint"]), "width_max_um": stats(widths["max"]),
        "length_midpoint_um": stats(lengths),
        "equivalent_volume_um3": {"included": stats(volumes), "by_geometry": {k: sum(1 for g, _ in volume_rows if g == k) for k in ("sphere", "spherocylinder")}, "excluded": excluded,
            "sphere_formula": "pi*d^3/6", "spherocylinder_formula": "pi*(d/2)^2*(L-d) + pi*d^3/6; L is total end-to-end length, d is width midpoint"},
        "caution": "Descriptive occupancy context only; volume is not a pore-throat transit dimension.",
    }
    (OUT / "m1_geometry_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"width_species": len(strict), "length_species": len(lengths), "simple_volume_species": len(volumes), "volume_exclusions": excluded}, sort_keys=True))


if __name__ == "__main__":
    main()
