"""Offline normalization and QC; no HTTP requests."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from subsurface_life_real_estate.processing import process


def main():
    p = argparse.ArgumentParser(description='Normalize verified cached BacDive records and report QC')
    p.add_argument('--manifest', default='data/interim/milestone1/acquisition.json')
    p.add_argument('--output-dir', default='data/processed/milestone1')
    p.add_argument('--lpsn-csv', default='data/raw/lpsn/lpsn_gss_2026-09-14.csv')
    p.add_argument('--lpsn-provenance', default='docs/provenance/lpsn_gss_2026-09-14.json')
    p.add_argument('--without-lpsn', action='store_true', help='Explicitly run historical BacDive-only processing')
    a = p.parse_args()
    process(a.manifest, a.output_dir, None if a.without_lpsn else a.lpsn_csv,
            None if a.without_lpsn else a.lpsn_provenance)


if __name__ == '__main__':
    main()
