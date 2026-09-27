"""Describe native sizes and explicit comparison diameters for Dataset v1."""
from __future__ import annotations

import bisect
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/reference_lithology_dataset_v1'
QC=ROOT/'data/processed/census_2026-09-14/scientific_qc_v1'
OUT=ROOT/'data/processed/reference_lithology_dataset_v1/analysis'; PLOTS=OUT/'plots'
METRICS={'width_minimum':'corrected_width_min_um','width_midpoint':'corrected_width_midpoint_um','width_maximum':'corrected_width_max_um'}
LO,HI,N=-3,5,80

def write(name, fields, rows):
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/name).open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)

def widths():
 vals={k:[] for k in METRICS}
 with (QC/'species_analytical_table.csv').open() as h:
  for r in csv.DictReader(h):
   if r['canonical_selection_status']=='canonical' and r['canonical_nomenclature_validation_status']=='validated_name_and_type':
    for k,c in METRICS.items():vals[k].append(float(r[c]))
 for x in vals.values():x.sort()
 return vals

def svg(name,title,xlabel,ylabel,series,logx=True):
 PLOTS.mkdir(parents=True,exist_ok=True);W,H,L,B=790,450,78,60
 xs=[x for _,p,_ in series for x,y in p if x>0];ys=[y for _,p,_ in series for x,y in p]
 xmin,xmax=(math.log10(min(xs)),math.log10(max(xs))) if logx else (min(xs),max(xs));ymin,ymax=min(ys),max(ys)
 def xy(x,y):
  x=math.log10(x) if logx else x
  return L+(x-xmin)/(xmax-xmin or 1)*(W-L-25),H-B-(y-ymin)/(ymax-ymin or 1)*(H-B-62)
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="{L}" y="24" font-family="sans-serif" font-size="16">{title}</text><line x1="{L}" y1="{H-B}" x2="{W-25}" y2="{H-B}" stroke="#333"/><line x1="{L}" y1="43" x2="{L}" y2="{H-B}" stroke="#333"/><text x="{W/2}" y="{H-12}" text-anchor="middle" font-family="sans-serif" font-size="12">{xlabel}</text><text x="18" y="{H/2}" transform="rotate(-90 18 {H/2})" text-anchor="middle" font-family="sans-serif" font-size="12">{ylabel}</text>']
 for i,(label,points,color) in enumerate(series):
  points=' '.join(f'{x:.1f},{y:.1f}' for x,y in (xy(x,y) for x,y in points if x>0))
  out.extend([f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.5"/>',f'<text x="{L+5}" y="{46+i*13}" font-family="sans-serif" font-size="10" fill="{color}">{label}</text>'])
 out.append('</svg>');(PLOTS/name).write_text(''.join(out),encoding='utf-8')

def main():
 w=widths()
 native_totals=defaultdict(float); native_hist=defaultdict(lambda:[0.0]*N)
 comparison_totals=defaultdict(float); numer=defaultdict(lambda:defaultdict(float)); comparison_hist=defaultdict(lambda:[0.0]*N)
 for r in csv.DictReader((DATA/'geometry_values.csv').open()):
  # Some source-native classes are deliberately non-physical (for example
  # Harvard CTSTA PORE-SIZE); preserve them in geometry_values but do not
  # manufacture a micrometre value for a cross-domain display.
  if not r['size_um']:
   continue
  if 'source_missing_weight' in r['qc_flags']:
   continue
  native_d=float(r['size_um']); weight=float(r['weight_raw']); native_key=(r['dataset_id'],r['source_id'],r['sample_id'],r['measurement_id'],r['lithology'],r['method'],r['geometry_class'],r['quantity_name'],r['native_size_definition'],r['weighting_basis'],r['observation_window_or_resolution'])
  native_totals[native_key]+=weight
  b=max(0,min(N-1,int((math.log10(native_d)-LO)/(HI-LO)*N)));native_hist[native_key][b]+=weight
  if not r['comparison_diameter_um']:
   continue
  d=float(r['comparison_diameter_um'])
  comparison_key=(r['dataset_id'],r['source_id'],r['sample_id'],r['measurement_id'],r['lithology'],r['method'],r['geometry_class'],r['quantity_name'],r['native_size_definition'],r['comparison_dimension'],r['comparison_derivation'],r['comparison_role'],r['weighting_basis'],r['observation_window_or_resolution'])
  comparison_totals[comparison_key]+=weight
  for metric,vals in w.items():numer[comparison_key][metric]+=weight*bisect.bisect_right(vals,d)/len(vals)
  b=max(0,min(N-1,int((math.log10(d)-LO)/(HI-LO)*N)));comparison_hist[comparison_key][b]+=weight
 sample=[]
 for key,total in sorted(comparison_totals.items()):
  dataset,source,sid,mid,lith,method,geometry,quantity,definition,dimension,derivation,role,basis,window=key
  for metric in METRICS:
   concept='P(D_body >= cultured species width); local accommodation only' if role=='pore_body_accommodation' else 'P(D_throat_or_entry >= cultured species width); nominal local transit fit only' if role=='throat_entry_nominal_transit' else 'P(D_modelled_matrix_pore_cluster >= cultured species width); modelled accommodation only'
   sample.append({'dataset_id':dataset,'source_id':source,'sample_id':sid,'measurement_id':mid,'lithology':lith,'method':method,'geometry_class':geometry,'quantity_name':quantity,'native_size_definition':definition,'comparison_dimension':dimension,'comparison_derivation':derivation,'comparison_role':role,'weighting_basis':basis,'observation_window_or_resolution':window,'microbial_width_metric':metric,'comparison_diameter_overlap_at_k_1':f'{numer[key][metric]/total:.9f}','interpretation':concept+'; not accessibility, habitability, connectivity, or a cross-method ranking'})
 write('comparison_diameter_overlap_sample_level.csv',list(sample[0]),sample)
 grouped=defaultdict(list)
 for r in sample: grouped[(r['dataset_id'],r['source_id'],r['lithology'],r['method'],r['geometry_class'],r['quantity_name'],r['native_size_definition'],r['comparison_dimension'],r['comparison_derivation'],r['comparison_role'],r['weighting_basis'],r['microbial_width_metric'])].append(float(r['comparison_diameter_overlap_at_k_1']))
 summary=[]
 for key,x in sorted(grouped.items()):
  x.sort(); med=(x[(len(x)-1)//2]+x[len(x)//2])/2
  summary.append({'dataset_id':key[0],'source_id':key[1],'lithology':key[2],'method':key[3],'geometry_class':key[4],'quantity_name':key[5],'native_size_definition':key[6],'comparison_dimension':key[7],'comparison_derivation':key[8],'comparison_role':key[9],'weighting_basis':key[10],'microbial_width_metric':key[11],'sample_count':len(x),'equal_sample_median_comparison_diameter_overlap':f'{med:.9f}','sample_min':f'{x[0]:.9f}','sample_max':f'{x[-1]:.9f}','interpretation':'Source-specific, method-labelled comparison-diameter overlap; not a harmonised lithology ranking or accessibility estimate'})
 write('comparison_diameter_overlap_lithology_method_summary.csv',list(summary[0]),summary)
 # Each sample contributes one normalized histogram; group rows are equal-sample
 # summaries, avoiding domination by the largest extracted network.
 bygroup=defaultdict(list)
 for key,bins in native_hist.items():
  total=native_totals[key]; g=(key[0],key[1],key[4],key[5],key[6],key[7],key[9],key[10]);bygroup[g].append([x/total for x in bins])
 distributions=[]
 for g,items in sorted(bygroup.items()):
  for b in range(N):
   low=10**(LO+b*(HI-LO)/N);high=10**(LO+(b+1)*(HI-LO)/N)
   distributions.append({'dataset_id':g[0],'source_id':g[1],'lithology':g[2],'method':g[3],'geometry_class':g[4],'quantity_name':g[5],'weighting_basis':g[6],'observation_window_or_resolution':g[7],'size_bin_lower_um':f'{low:.9g}','size_bin_upper_um':f'{high:.9g}','equal_sample_mean_native_weight':f'{sum(x[b] for x in items)/len(items):.9g}','sample_count':len(items),'binning_note':'log10 bins for display; native units/definitions retained in input table'})
 write('native_size_distribution_lithology_method.csv',list(distributions[0]),distributions)
 colors={'granite':'#5b6c99','sandstone':'#d06f4c','carbonate':'#287271','basalt_volcanic':'#7f3c8d','mudstone_shale':'#3c78a8','unconsolidated_sand':'#9a7d0a'}
 ser=[]
 for g,items in sorted(bygroup.items()):
  if g[4] not in {'pore_body','pore_throat','matrix_pore'}:continue
  run=0;pts=[]
  for b in range(N):
   run+=sum(x[b] for x in items)/len(items);pts.append((10**(LO+(b+.5)*(HI-LO)/N),run))
  lab=f'{g[2]} | {g[4]} | {g[1]}'
  ser.append((lab,pts,colors.get(g[2],'#555555')))
 svg('reference_native_size_distributions.svg','Reference Lithology Dataset v1: native size distributions','Native reported size (µm; log; radius/diameter as labelled)','Equal-sample cumulative native weight',ser)
 ser=[]
 for metric,color in [('width_minimum','#287271'),('width_midpoint','#e07a5f'),('width_maximum','#5b6c99')]:ser.append((metric,[(x,(i+1)/len(w[metric])) for i,x in enumerate(w[metric][::5])],color))
 svg('microbial_width_ecdfs_reference_v1.svg','Cultured species widths (N=4,452)','Width (µm; log)','Species cumulative fraction',ser)
 comparison_groups=defaultdict(list)
 for key,bins in comparison_hist.items():
  total=comparison_totals[key]; g=(key[0],key[1],key[4],key[5],key[6],key[9],key[11],key[12],key[13]);comparison_groups[g].append([x/total for x in bins])
 ser=[]
 for g,items in sorted(comparison_groups.items()):
  run=0;pts=[]
  for b in range(N):
   run+=sum(x[b] for x in items)/len(items);pts.append((10**(LO+(b+.5)*(HI-LO)/N),run))
  lab=f'{g[2]} | {g[5]} | {g[4]} | {g[1]}'
  ser.append((lab,pts,colors.get(g[2],'#555555')))
 svg('comparison_diameter_distributions.svg','Comparison-diameter distributions','Comparison diameter (µm; log; explicit analytical field)','Equal-sample cumulative source weight',ser)
 ser=[]
 for index,r in enumerate(summary, start=1):
  if r['microbial_width_metric']=='width_midpoint':
   ser.append((f"{r['lithology']} | {r['comparison_role']} | {r['source_id']}",[(index,float(r['equal_sample_median_comparison_diameter_overlap']))],colors.get(r['lithology'],'#555555')))
 svg('comparison_diameter_overlap_midpoint.svg','Comparison-diameter overlap with cultured midpoint width','Method-labelled group (point positions arbitrary)','P(comparison diameter ≥ microbial width)',ser,False)
 for legacy in ('native_size_nominal_fit_sample_level.csv','native_size_nominal_fit_lithology_method_summary.csv','plots/native_size_nominal_fit_midpoint.svg'):
  (OUT/legacy).unlink(missing_ok=True)
 (OUT/'analysis_manifest.json').write_text(json.dumps({'microbial_population':'4452 strict LPSN-supported cultured species','analysis':'Comparison-diameter overlap at k=1, separately by geometry/method/weighting. Radius sources use an explicit 2 × radius analytical field; source diameters and MIP entry/throat-equivalent dimensions are retained. Native-size plots remain separate. Existing C(k) remains a separate constriction-specific analysis.','display_binning':'80 fixed log10 bins from 0.001 to 100000 µm; statistics use individual processed source values.'},indent=2)+'\n')
 print(json.dumps({'sample_overlap_rows':len(sample),'summary_rows':len(summary),'distribution_rows':len(distributions)},sort_keys=True))
if __name__=='__main__':main()
