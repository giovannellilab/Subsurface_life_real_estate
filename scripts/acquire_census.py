"""Full v2-only acquisition, resumable from immutable local responses."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from subsurface_life_real_estate.census_acquisition import census_acquire

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir', default='data/raw/bacdive/census_2026-09-14')
    p.add_argument('--manifest', default='data/interim/census_2026-09-14/acquisition.json')
    p.add_argument('--lpsn-csv', default='data/raw/lpsn/lpsn_gss_2026-09-14.csv')
    p.add_argument('--lpsn-provenance', default='docs/provenance/lpsn_gss_2026-09-14.json')
    p.add_argument('--delay', type=float, default=0.5)
    a = p.parse_args()
    if a.delay < 0.5:
        p.error('Use at least 0.5 seconds between sequential requests')
    census_acquire(a.raw_dir, a.manifest, a.lpsn_csv, a.lpsn_provenance, a.delay)
