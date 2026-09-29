"""Build the sanitized static Living Research Report from tracked source and local figures."""
from __future__ import annotations
import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "lipnice_mip_intrusion.svg": ROOT / "data/processed/m3_first_ingestion/analysis/plots/lipnice_mip_intrusion.svg",
    "m3_compatibility_clearance_curves.svg": ROOT / "data/processed/m3_transit_comparison_v1/plots/compatibility_clearance_curves.svg",
    "reference_native_size_distributions.svg": ROOT / "data/processed/reference_lithology_dataset_v1/analysis/plots/reference_native_size_distributions.svg",
    "reference_microbial_width_ecdfs.svg": ROOT / "data/processed/reference_lithology_dataset_v1/analysis/plots/microbial_width_ecdfs_reference_v1.svg",
    "geological_evidence_depth.svg": ROOT / "data/processed/m3_geological_resource_audit_v1/plots/geological_evidence_depth.svg",
    "global_sampling_map.svg": ROOT / "data/processed/m3_geological_resource_audit_v1/plots/global_sampling_map.svg",
    "porosity_context.svg": ROOT / "data/processed/m3_geological_resource_audit_v1/plots/porosity_context.svg",
    "sample_geometry_summaries.svg": ROOT / "data/processed/m3_geological_resource_audit_v1/plots/sample_geometry_summaries.svg",
    "literature_atlas_global_map.svg": ROOT / "data/processed/m3_literature_lithology_atlas_v1/plots/literature_atlas_global_map.svg",
    "literature_porosity_envelopes.svg": ROOT / "data/processed/m3_literature_lithology_atlas_v1/plots/literature_porosity_envelopes.svg",
    "literature_void_class_envelopes.svg": ROOT / "data/processed/m3_literature_lithology_atlas_v1/plots/literature_void_class_envelopes.svg",
    "m3_porosity_against_literature_envelopes.svg": ROOT / "data/processed/m3_literature_lithology_atlas_v1/plots/m3_porosity_against_literature_envelopes.svg",
    "literature_quantitative_measurement_depth.svg": ROOT / "data/processed/m3_literature_measurements_v1/plots/literature_quantitative_measurement_depth.svg",
    "literature_published_porosity.svg": ROOT / "data/processed/m3_literature_measurements_v1/plots/literature_published_porosity.svg",
    "literature_published_void_sizes.svg": ROOT / "data/processed/m3_literature_measurements_v1/plots/literature_published_void_sizes.svg",
    "m1_species_width_distributions.svg": ROOT / "data/processed/m1_geometry_resource_v1/plots/m1_species_width_distributions.svg",
    "m1_species_length_distribution.svg": ROOT / "data/processed/m1_geometry_resource_v1/plots/m1_species_length_distribution.svg",
    "m1_simple_cell_equivalent_volume.svg": ROOT / "data/processed/m1_geometry_resource_v1/plots/m1_simple_cell_equivalent_volume.svg",
}
SECTION_IDS = ("question", "microbes", "geology", "results", "milestones", "methods", "limitations", "references")
FROZEN_MILESTONES = ("M1", "M2", "M3", "M4", "M5", "M6")
IMG_SRC = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)


def deployment_timestamp() -> str:
    now = datetime.now(ZoneInfo("Europe/Rome"))
    return f"{now.day} {now.strftime('%b %Y · %H:%M %Z')}"


def validate_source_html(html: str) -> None:
    """Keep the Living Report structurally cumulative, not a latest-result stub."""
    missing_sections = [section for section in SECTION_IDS if f'id="{section}"' not in html]
    if missing_sections:
        raise ValueError(f"Living Report is missing frozen major section(s): {', '.join(missing_sections)}")
    missing_milestones = [milestone for milestone in FROZEN_MILESTONES if not re.search(rf">{milestone}<", html)]
    if missing_milestones:
        raise ValueError(f"Living Report is missing frozen roadmap milestone(s): {', '.join(missing_milestones)}")


def validate_built_images(output: Path, html: str) -> None:
    """Fail on stale/missing local image paths before a report can be deployed."""
    for src in IMG_SRC.findall(html):
        if not src.startswith("assets/") or "/" in src.removeprefix("assets/"):
            raise ValueError(f"Living Report contains stale or non-public local image path: {src}")
        name = src.removeprefix("assets/")
        if name not in ASSETS:
            raise ValueError(f"Living Report image is not allowlisted: {src}")
        if not (output / src).is_file():
            raise FileNotFoundError(f"Living Report image was referenced but not copied: {src}")


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    validate_source_html(html)
    html = html.replace("{{DEPLOYMENT_TIMESTAMP}}", deployment_timestamp())
    if "{{DEPLOYMENT_TIMESTAMP}}" in html:
        raise ValueError("Unresolved deployment timestamp placeholder")
    (output / "index.html").write_text(html, encoding="utf-8")
    shutil.copy2(ROOT / "site/styles.css", output / "styles.css")
    (output / ".nojekyll").write_bytes(b"")
    assets = output / "assets"; assets.mkdir(exist_ok=True)
    for name, source in ASSETS.items():
        if not source.is_file():
            raise FileNotFoundError(f"Required local derived figure is absent: {source}")
        target = assets / name
        shutil.copy2(source, target)
        # Matplotlib SVGs can carry trailing whitespace.  Normalise only the
        # copied public derivative so gh-pages diff validation remains useful.
        if target.suffix == ".svg":
            target.write_text("\n".join(line.rstrip() for line in target.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    validate_built_images(output, html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    build(parser.parse_args().output_dir)
