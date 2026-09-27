# M3 pore × microbe proof of concept

Status: first direct, source-specific geometric comparison (2026-09-27).
This analysis uses the cultured, formally described strict-LPSN species baseline
(`N = 4,452`) and keeps canonical width minimum, midpoint, and maximum
separate. It is a local geometric comparison only; it is not accessibility,
habitability, colonizable porosity, or connected habitat.

## Comparison rule

Native geological values remain unchanged in `geometry_values.csv`. A separate
`comparison_diameter_um` is used only here: `2 ×` an explicitly reported source
radius, a source-reported diameter retained unchanged, or the Lipnice MIP
entry/throat-equivalent dimension retained unchanged. Variables with unresolved
semantics and connectivity-only records have no comparison diameter.

The three outputs are deliberately separate:

| Concept | Eligible geometry | Statistic |
| --- | --- | --- |
| Accommodation | pore body; W23 modelled matrix-pore cluster | `P(D_body >= W)` or `P(D_modelled_cluster >= W)` |
| Nominal transit | pore throat; MIP entry/throat equivalent | `P(D_throat_or_entry >= W)` |
| Connectivity/transport | coordination, topology, porosity, permeability, resistivity, formation factor | reported as source context only; never folded into either probability |

Sample values are calculated first. Source-specific lithology summaries give
equal sample weight and report median/minimum/maximum; objects are never pooled
across samples or sources.

## Main midpoint-width patterns

At width midpoint, Lipnice MIP entry/throat nominal transit has an equal-sample
median of 0.386738 across 21 specimens (range 0.236865–0.695122). The W23
modelled shale matrix-pore-cluster accommodation result is 0.458212. These are
the present sources that visibly intersect the cultured microbial-width domain.

Resolved CT/PNM source networks are predominantly larger than the cultured
width baseline: Fontainebleau/Berea throat nominal transit is 0.952526 across
three cases (0.951820–0.993846); F42A sand throat nominal transit is 0.998875;
South China Sea carbonate throat nominal transit is 0.998931 across five
samples; and Wilmslow sandstone throat nominal transit is 0.998306 across seven
samples. Those high values describe their reported, resolved/extracted networks
only, not a complete whole-rock constriction population.

## Resolution and interpretation boundary

Fontainebleau/Berea is conditional on a 0.74 µm voxel, thresholded PNM window;
F42A on 9.996 µm voxels; and basalt pore-body accommodation on 14.99 µm voxels.
The South China Sea and Wilmslow archives do not state a voxel size in the local
machine-readable artifact, so that absence remains explicit. W23 is a modelled
matrix-pore-cluster radius curve, not a direct throat distribution. PANGAEA
serpentinised-ultramafic and mafic crystalline records remain transport-only.

The existing granite/sandstone `C(k)` curves remain the only clearance analysis,
because their entry/throat comparison semantics were independently justified.
