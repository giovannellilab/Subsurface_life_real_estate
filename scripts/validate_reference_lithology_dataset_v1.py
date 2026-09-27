"""Basic structural and semantic checks for Reference Lithology Dataset v1."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/reference_lithology_dataset_v1'; ANALYSIS=DATA/'analysis'
def read(path):
 with path.open() as h:return list(csv.DictReader(h))
def main():
 registry=read(DATA/'reference_lithology_dataset_v1.csv'); values=read(DATA/'geometry_values.csv'); conn=read(DATA/'connectivity_metrics.csv')
 attrs=read(DATA/'source_measurement_attributes.csv'); edges=read(DATA/'network_edges.csv')
 assert {'granite','sandstone','carbonate','basalt_volcanic','mudstone_shale','unconsolidated_sand','serpentinized_ultramafic','mafic_crystalline'} <= {r['lithology'] for r in registry}
 assert {'pore_body','pore_throat'} <= {r['geometry_class'] for r in registry}
 assert all((not r['size_um'] and 'normalized_size_unavailable' in r['qc_flags']) or ('source_missing_weight' in r['qc_flags']) or (float(r['size_um'])>0 and float(r['weight_raw'])>=0) for r in values)
 assert all(r['native_size_definition'] and r['size_unit_raw'] and r['weighting_basis'] for r in values)
 assert all((not r['comparison_diameter_um'] and not r['comparison_dimension'] and not r['comparison_derivation'] and not r['comparison_role']) or (float(r['comparison_diameter_um'])>0 and r['comparison_dimension'] and r['comparison_derivation'] and r['comparison_role']) for r in values)
 assert all(r['comparison_role'] in {'','pore_body_accommodation','throat_entry_nominal_transit','modelled_matrix_pore_cluster_accommodation'} for r in values)
 assert all(r['value_normalized'] and r['definition'] for r in conn)
 assert {'total_porosity','connected_porosity','permeability'} <= {r['metric_name'] for r in conn}
 overlap=read(ANALYSIS/'comparison_diameter_overlap_sample_level.csv'); summary=read(ANALYSIS/'comparison_diameter_overlap_lithology_method_summary.csv')
 assert all(0<=float(r['comparison_diameter_overlap_at_k_1'])<=1 for r in overlap)
 assert all(r['geometry_class'] in {'pore_body','pore_throat','matrix_pore'} for r in overlap)
 assert all(r['comparison_role'] for r in overlap)
 assert all('not accessibility' in r['interpretation'] for r in overlap)
 assert len(summary)>=12
 assert any(r['source_id']=='M3-023' and not r['size_um'] for r in values)
 assert any(r['source_id']=='M3-023' and r['comparison_role']=='modelled_matrix_pore_cluster_accommodation' for r in values)
 assert not any(r['source_id']=='M3-023' and r['size_unit_raw']!='nm radius' and r['comparison_diameter_um'] for r in values)
 assert any(r['source_id']=='M3-024' and r['geometry_class']=='pore_body' for r in values)
 assert any(r['source_id']=='M3-024' and r['geometry_class']=='pore_throat' for r in values)
 assert all(float(r['comparison_diameter_um']) == 2*float(r['size_um']) for r in values if r['source_id']=='M3-024')
 assert all(float(r['comparison_diameter_um']) == float(r['size_um']) for r in values if r['source_id']=='M3-001')
 assert len(edges)==2856
 assert any(r['source_id']=='M3-025' for r in conn)
 assert not any(r['source_id']=='M3-025' for r in values)
 assert len(attrs)>10000
 assert not (ANALYSIS/'native_size_nominal_fit_sample_level.csv').exists()
 assert not (ANALYSIS/'native_size_nominal_fit_lithology_method_summary.csv').exists()
 print(f'OK: {len(registry)} registry rows; {len(values)} native geometry rows; {len(conn)} connectivity metrics; {len(attrs)} source attributes; {len(edges)} edges; {len(overlap)} comparison-diameter overlap rows')
if __name__=='__main__':main()
