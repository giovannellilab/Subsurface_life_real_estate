"""First local geometric-fit comparison: cultured width vs M3 constrictions.

This intentionally supports only the two local tabular M3 sources. It keeps
their weighting bases separate and produces sample-level results before equal-
sample lithology summaries. It does not estimate accessibility or habitability.
"""
from __future__ import annotations
import bisect, csv, json, math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
M3=ROOT/'data/processed/m3_first_ingestion'; QC=ROOT/'data/processed/census_2026-09-14/scientific_qc_v1'
OUT=ROOT/'data/processed/m3_transit_comparison_v1'; PLOTS=OUT/'plots'
METRICS={'width_minimum':'corrected_width_min_um','width_midpoint':'corrected_width_midpoint_um','width_maximum':'corrected_width_max_um'}

def write(name, fields, rows):
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/name).open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)

def svg(name,title,xlabel,ylabel,series,logx=False):
 PLOTS.mkdir(parents=True,exist_ok=True); W,H,L,B=760,430,78,58
 xs=[x for _,pts,_ in series for x,y in pts if x>0]; ys=[y for _,pts,_ in series for x,y in pts]
 xmin,xmax=(math.log10(min(xs)),math.log10(max(xs))) if logx else (min(xs),max(xs)); ymin,ymax=min(ys),max(ys)
 def xy(x,y):
  x=math.log10(x) if logx else x
  return (L+(x-xmin)/(xmax-xmin or 1)*(W-L-25),H-B-(y-ymin)/(ymax-ymin or 1)*(H-B-60))
 s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="{L}" y="25" font-family="sans-serif" font-size="16">{title}</text><line x1="{L}" y1="{H-B}" x2="{W-25}" y2="{H-B}" stroke="#333"/><line x1="{L}" y1="45" x2="{L}" y2="{H-B}" stroke="#333"/><text x="{W/2}" y="{H-12}" text-anchor="middle" font-family="sans-serif" font-size="12">{xlabel}</text><text x="18" y="{H/2}" transform="rotate(-90 18 {H/2})" text-anchor="middle" font-family="sans-serif" font-size="12">{ylabel}</text>']
 for i,(lab,pts,col) in enumerate(series):
  pts=' '.join(f'{a:.1f},{b:.1f}' for a,b in (xy(x,y) for x,y in pts if x>0)); s += [f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.5"/><text x="{L+8}" y="{48+i*14}" font-family="sans-serif" font-size="11" fill="{col}">{lab}</text>']
 s.append('</svg>'); (PLOTS/name).write_text(''.join(s),encoding='utf-8')

def widths():
 vals={k:[] for k in METRICS}
 with (QC/'species_analytical_table.csv').open() as h:
  for r in csv.DictReader(h):
   if r['canonical_selection_status']=='canonical' and r['canonical_nomenclature_validation_status']=='validated_name_and_type':
    for key,col in METRICS.items(): vals[key].append(float(r[col]))
 for v in vals.values(): v.sort()
 assert all(len(v)==4452 for v in vals.values())
 return vals

def compatible(dimensions, weights, w, k):
 # For each native geological draw, integrate the species ECDF; geological
 # weights are never converted into counts or pooled with other samples.
 return sum(a*(bisect.bisect_right(w,d/k)/len(w)) for d,a in zip(dimensions,weights))/sum(weights)

def main():
 w=widths(); samples={r['sample_id']:r for r in csv.DictReader((M3/'samples.csv').open())}; meas={r['measurement_id']:r for r in csv.DictReader((M3/'measurements.csv').open())}
 panel=[
 ['sandstone','M3-002','Fontainebleau/Berea dry sandstone cases','dry Fontainebleau (Case1FB); dry Berea (Case2B)','micro_CT_plus_PNM','pore_throat EqRadius','2 × EqRadius, derived equivalent diameter','throat-object count','0.74 µm isotropic voxel; 500³-voxel ROI; resolved, segmented connected network','included_resolution_conditioned','only dry cases enter primary transit calculation; thresholded CT/PNM throats are not a complete whole-rock throat population'],
 ['sandstone_state_sensitivity','M3-002','oil/water-saturated Berea case','water-filled pore-space subset (Case3B)','micro_CT_plus_PNM','pore_throat EqRadius','2 × EqRadius, derived equivalent diameter','throat-object count','0.74 µm isotropic voxel; 500³-voxel ROI; resolved water-phase connected network','excluded','experimentally phase-conditioned network; retained in source resource but excluded from natural-state reference'],
 ['mudstone_shale','M3-003','West Trenton mudstone core','core samples','MIP','MIP entry/throat-equivalent','none','incremental intrusion porosity','source-specific','excluded','catalogued primary source not locally acquired after access denial'],
 ['carbonate','M3-004','Estaillades limestone','dry imaging specimen','micro_CT|nano_CT','matrix pore/mixed','none','not yet extracted','3.9676 µm micro-CT; 32 nm nano-CT','excluded','image resources available but no reviewed local constriction table'],
 ['basalt_volcanic','M3-005','basalt core','unreacted and CO2-reacted','micro_CT_plus_PNM','pore_throat','none','source-specific','14.99 µm voxel','excluded','catalogue source includes reaction-state contrast; no local natural reference throat table'],
 ['granite','M3-001','Lipnice granite MEL-5 specimens','fracturing and alteration facies','MIP','MIP entry/throat-equivalent bin','source bin lower edge (primary conservative); geometric midpoint sensitivity','incremental intruded porosity','0.008–309 µm source bins','included','21 local tabular specimen distributions; source reports throat-size bins'],
 ['serpentinite_peridotite','M3-006','serpentinite veins','reaction-front and vein-center','FIB_SEM|TEM','matrix/grain-boundary pore','none','not interoperable','nanoscale fields','excluded','no local quantitative constriction distribution; nanoporosity alone is not transit evidence'],
 ['metamorphic','M3-007','Carrara marble','thermally cracked','micro_CT','microcrack','none','segmentation dependent','2.0 µm voxel','excluded','artificial thermal state and segmentation warning make it unsuitable as natural primary reference'],
 ['unconsolidated_sediment','M3-022','compacting sediments','model/literature synthesis','model_and_literature_synthesis','matrix pore','none','not one distribution','not applicable','excluded','conceptual antecedent, not a primary repository distribution'],
 ]
 pfields=['lithology','source_id','reference_material','sample_state','method','native_geometry_quantity','comparison_dimension','weighting_basis','observational_window_or_resolution','transit_status','selection_or_exclusion_reason']
 write('reference_lithology_panel_v1.csv',pfields,[dict(zip(pfields,x)) for x in panel])
 native=[]; groups=defaultdict(list); granite_midpoint_groups=defaultdict(list)
 # Granite: lower bin edge gives a conservative statement that every value in
 # a bin exceeds the comparison threshold; weights remain intrusion porosity.
 for r in csv.DictReader((M3/'measurement_distribution.csv').open()):
  if r['measurement_id'].endswith(':mip_intrusion'):
   groups[r['measurement_id']].append((float(r['bin_lower_um']),float(r['value_normalized']),'granite','MIP_entry_equivalent_bin_lower_edge','incremental_intruded_porosity'))
   granite_midpoint_groups[r['measurement_id']].append(((float(r['bin_lower_um'])*float(r['bin_upper_um']))**.5,float(r['value_normalized']),'granite','MIP_entry_equivalent_bin_geometric_midpoint','incremental_intruded_porosity'))
 # Sandstone: separate throats only; EqRadius is retained natively and the
 # analytical diameter is explicitly derived as 2× radius.
 for r in csv.DictReader((M3/'network_objects.csv').open()):
  if r['geometry_class']=='pore_throat' and r['measurement_id'] != 'M3-002:Case3B:pore_throat': groups[r['measurement_id']].append((2*float(r['radius_um']),1.0,'sandstone','2_x_source_EqRadius','throat_object_count'))
 native_fields=['sample_id','measurement_id','lithology','method','geometry_class','native_size_definition','comparison_dimension_definition','comparison_dimension_um','weight','weighting_basis','observational_window_or_resolution','comparison_scope']
 curve=[]; c1=[]
 for mid,vals in sorted(groups.items()):
  m=meas[mid]; sid=m['sample_id']; s=samples[sid]; dims=[x[0] for x in vals]; weights=[x[1] for x in vals]; lith=vals[0][2]; ddef=vals[0][3]; basis=vals[0][4]
  scope='resolution_conditioned_resolved_throats' if lith=='sandstone' else 'MIP_binned_entry_equivalent_window'
  for d,a,*_ in vals: native.append(dict(zip(native_fields,[sid,mid,lith,m['method'],m['geometry_class'],m['size_definition_raw'],ddef,d,a,basis,m['resolution_or_detection_limit_raw'],scope])))
  for k_i in range(41):
   k=1+k_i*.05
   for metric,ws in w.items(): curve.append({'sample_id':sid,'measurement_id':mid,'lithology':lith,'clearance_factor_k':f'{k:.2f}','microbial_width_metric':metric,'compatibility_C':f'{compatible(dims,weights,ws,k):.9f}','weighting_basis':basis,'comparison_dimension_definition':ddef,'comparison_scope':scope})
  for metric,ws in w.items(): c1.append({'sample_id':sid,'measurement_id':mid,'lithology':lith,'microbial_width_metric':metric,'C_at_k_1':f'{compatible(dims,weights,ws,1):.9f}','weighting_basis':basis,'comparison_dimension_definition':ddef,'comparison_scope':scope})
 write('native_constriction_values.csv',native_fields,native)
 cfields=list(curve[0]); write('compatibility_curves_sample_level.csv',cfields,curve); write('nominal_fit_k1_sample_level.csv',list(c1[0]),c1)
 # Equal-sample summaries: no object-count pooling.
 summaries=[]
 by=defaultdict(list)
 for r in curve: by[(r['lithology'],r['clearance_factor_k'],r['microbial_width_metric'],r['weighting_basis'],r['comparison_scope'])].append(float(r['compatibility_C']))
 for key,v in sorted(by.items()):
  v.sort(); median=(v[(len(v)-1)//2]+v[len(v)//2])/2
  summaries.append({'lithology':key[0],'clearance_factor_k':key[1],'microbial_width_metric':key[2],'sample_count':len(v),'equal_sample_median_C':f'{median:.9f}','sample_min_C':f'{v[0]:.9f}','sample_max_C':f'{v[-1]:.9f}','weighting_basis':key[3],'comparison_scope':key[4]})
 write('compatibility_curves_lithology_equal_sample.csv',list(summaries[0]),summaries)
 # MIP bins are logarithmically spaced.  The primary calculation uses their
 # lower edge; this companion table quantifies the justified geometric-midpoint
 # alternative without replacing the native bins or primary conservative result.
 sensitivity=[]
 for mid,vals in sorted(granite_midpoint_groups.items()):
  lower=groups[mid]; sid=meas[mid]['sample_id']
  for k_i in range(41):
   k=1+k_i*.05
   for metric,ws in w.items():
    lo=compatible([x[0] for x in lower],[x[1] for x in lower],ws,k); gm=compatible([x[0] for x in vals],[x[1] for x in vals],ws,k)
    sensitivity.append({'sample_id':sid,'measurement_id':mid,'clearance_factor_k':f'{k:.2f}','microbial_width_metric':metric,'C_lower_bin_edge':f'{lo:.9f}','C_geometric_bin_midpoint':f'{gm:.9f}','midpoint_minus_lower':f'{gm-lo:.9f}','weighting_basis':'incremental_intruded_porosity'})
 write('granite_bin_representation_sensitivity.csv',list(sensitivity[0]),sensitivity)
 # compact figures: ECDF-like native distributions and equal-sample C(k).
 ser=[]
 for lith,col in [('granite','#5b6c99'),('sandstone','#d06f4c')]:
  vals=[(float(r['comparison_dimension_um']),float(r['weight'])) for r in native if r['lithology']==lith]; vals.sort(); total=sum(a for _,a in vals); run=0; pts=[]
  for d,a in vals: run+=a; pts.append((d,run/total))
  step=max(1,len(pts)//900); ser.append((lith+' (native weighting)',pts[::step]+[pts[-1]],col))
 svg('native_constriction_distributions.svg','Native constriction distributions (not pooled)','Source-defined comparison dimension (µm; log)','Cumulative native weight',ser,True)
 ser=[]
 for metric,col in [('width_minimum','#287271'),('width_midpoint','#e07a5f'),('width_maximum','#5b6c99')]: ser.append((metric,[(x,(i+1)/len(w[metric])) for i,x in enumerate(w[metric][::5])],col))
 svg('microbial_width_ecdfs.svg','Cultured species canonical width ECDFs (N=4,452)','Width (µm; log)','Species cumulative fraction',ser,True)
 ser=[]
 for lith,col in [('granite','#5b6c99'),('sandstone','#d06f4c')]:
  rows=[r for r in summaries if r['lithology']==lith and r['microbial_width_metric']=='width_midpoint']; ser.append((lith+' midpoint width',[(float(r['clearance_factor_k']),float(r['equal_sample_median_C'])) for r in rows],col))
 svg('compatibility_clearance_curves.svg','Local geometric compatibility: equal-sample median','Clearance factor k','C(k); cultured width midpoint',ser,False)
 (OUT/'analysis_manifest.json').write_text(json.dumps({'microbial_population':'4452 strict LPSN-supported cultured species','k_range':'1.00–3.00 in 0.05 increments','eligible_lithologies':['granite','sandstone'],'sandstone_scope':'Dry Fontainebleau/Berea resolved, segmented CT/PNM throats only; not a complete whole-rock throat population. Case3B is excluded as a water-phase experimental subset.','granite_primary_representation':'lower MIP bin edge; geometric-midpoint sensitivity is emitted separately.','exclusions':'Panel rows document non-eligible endmembers; no source pooling or accessibility inference.'},indent=2)+'\n')
 print(json.dumps({'panel_rows':len(panel),'native_rows':len(native),'sample_curves':len(curve),'k1_rows':len(c1)},sort_keys=True))
if __name__=='__main__': main()
