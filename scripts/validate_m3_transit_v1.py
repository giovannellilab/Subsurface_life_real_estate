"""Structural/semantic checks for the local M3 transit comparison."""
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data/processed/m3_transit_comparison_v1'
def read(n):
 with (OUT/n).open() as h:return list(csv.DictReader(h))
def main():
 panel=read('reference_lithology_panel_v1.csv'); native=read('native_constriction_values.csv'); curves=read('compatibility_curves_sample_level.csv')
 assert {r['lithology'] for r in panel if r['transit_status'].startswith('included')}=={'granite','sandstone'}
 assert all(float(r['comparison_dimension_um'])>0 and float(r['weight'])>=0 for r in native)
 assert {r['geometry_class'] for r in native}=={'pore_throat'}
 assert {r['weighting_basis'] for r in native}=={'incremental_intruded_porosity','throat_object_count'}
 assert all(r['comparison_scope'] for r in native)
 assert all(r['comparison_scope']=='resolution_conditioned_resolved_throats' for r in native if r['lithology']=='sandstone')
 assert all(0<=float(r['compatibility_C'])<=1 and 1<=float(r['clearance_factor_k'])<=3 for r in curves)
 assert {r['microbial_width_metric'] for r in curves}=={'width_minimum','width_midpoint','width_maximum'}
 assert len({r['sample_id'] for r in curves if r['lithology']=='granite'})==21
 assert len({r['sample_id'] for r in curves if r['lithology']=='sandstone'})==2
 assert 'M3-002:Case3B' not in {r['sample_id'] for r in curves}
 sensitivity=read('granite_bin_representation_sensitivity.csv')
 assert len(sensitivity)==21*41*3
 assert all(float(r['C_geometric_bin_midpoint']) >= float(r['C_lower_bin_edge']) for r in sensitivity)
 print(f'OK: {len(panel)} panel rows; {len(native)} native throat/entry rows; {len(curves)} sample-metric compatibility rows')
if __name__=='__main__':main()
