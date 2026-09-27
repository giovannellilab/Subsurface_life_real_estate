"""Build the sanitized static Living Research Report from tracked source and local figures."""
from __future__ import annotations
import argparse
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
    "pore_microbe_size_distributions.svg": ROOT / "data/processed/reference_lithology_dataset_v1/analysis/plots/pore_microbe_size_distributions.svg",
    "pore_microbe_compatibility_landscape.svg": ROOT / "data/processed/reference_lithology_dataset_v1/analysis/plots/pore_microbe_compatibility_landscape.svg",
}


def deployment_timestamp() -> str:
    now = datetime.now(ZoneInfo("Europe/Rome"))
    return f"{now.day} {now.strftime('%b %Y · %H:%M %Z')}"


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
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
        shutil.copy2(source, assets / name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    build(parser.parse_args().output_dir)
