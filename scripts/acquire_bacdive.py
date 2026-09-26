"""Run with Python from the repository root; no installation required."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from subsurface_life_real_estate.acquisition import acquire


def main():
    p = argparse.ArgumentParser(description='Acquire immutable BacDive v2 type-strain responses')
    p.add_argument('--raw-dir', default='data/raw/bacdive/milestone1')
    p.add_argument('--manifest', default='data/interim/milestone1/acquisition.json')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--sample-size', type=int, default=100)
    group.add_argument('--all', action='store_true', help='Fetch all IDs in cached type-strain index')
    a = p.parse_args()
    acquire(a.raw_dir, a.manifest, None if a.all else a.sample_size)


if __name__ == '__main__':
    main()
