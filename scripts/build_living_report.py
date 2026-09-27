"""Build the sanitized static Living Research Report from tracked source and local figures."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "width_ecdf.png": ROOT / "data/processed/census_2026-09-14/analysis/plots/width_ecdf.png",
    "species_width_ecdfs.png": ROOT / "data/processed/census_2026-09-14/scientific_qc_v1/plots/species_width_ecdfs.png",
    "dimension_density.png": ROOT / "data/processed/census_2026-09-14/analysis/plots/dimension_density.png",
    "lipnice_mip_intrusion.svg": ROOT / "data/processed/m3_first_ingestion/analysis/plots/lipnice_mip_intrusion.svg",
    "sandstone_pnm_radius_ecdf.svg": ROOT / "data/processed/m3_first_ingestion/analysis/plots/sandstone_pnm_radius_ecdf.svg",
}

def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css"):
        shutil.copy2(ROOT / "site" / name, output / name)
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
