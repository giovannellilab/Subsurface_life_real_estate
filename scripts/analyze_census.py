"""Generate offline exploratory outputs from a completed full census."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from subsurface_life_real_estate.analysis import analyze


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", default="data/processed/census_2026-09-14/observations.jsonl")
    parser.add_argument("--output-dir", default="data/processed/census_2026-09-14/analysis")
    args = parser.parse_args()
    analyze(args.observations, args.output_dir)
