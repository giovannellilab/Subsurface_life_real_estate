# Reference Lithology Panel v1 and first local-fit comparison

Status: **scientific review required** (2026-09-27). This is a finite,
source-qualified panel, not a universal pore-size resource. `C(k)` is local
geometric compatibility through a stated constriction only; it is not
accessibility, connected habitat fraction, colonizable porosity, or habitability.

## Panel decision

The primary quantitative panel contains only two endmembers for which the
existing census has a locally available, natural-state and reviewable
constriction artifact: Lipnice granite (M3-001) and dry Fontainebleau/Berea
sandstone CT/PNM cases (M3-002). The oil/water-saturated Berea case is retained
as source-state sensitivity data, but is excluded from the natural-state
reference. The census rows for mudstone/shale, carbonate, basalt/volcanic,
serpentinite/peridotite, metamorphic rock and unconsolidated sediment remain
explicit exclusions: their available artifacts are inaccessible, image-only,
altered/artificial, conceptual, or do not provide a reviewed constriction
distribution. No weak substitute was ingested merely to fill a lithology.

`reference_lithology_panel_v1.csv` is the authoritative selection table. It
records source, state, method, native quantity, analytical comparison
dimension, observation window, weighting, and exclusion rationale.

## Observational meaning and comparison dimension

For dry Fontainebleau (Case1FB) and dry Berea (Case2B), the source article
reports synchrotron X-ray microtomography with 0.74 µm isotropic voxels,
1024-cubed original images and a 500-cubed-voxel region of interest. Interactive
Top Hat/White Top Hat and Non-Local Means filtering, manual greyscale
thresholding, and PerGeos hybrid skeleton-based network extraction were used.
Only `pore_throat` rows enter the comparison. The source `EqRadius` is retained;
the separate derived analytical dimension is `2 × EqRadius`. Consequently all
sandstone `C(k)` values are conditional on the **resolved, segmented connected
throat network**, not estimates for the complete whole-rock throat population.
No universal sub-voxel cutoff is inferred from the stated voxel size.

For granite, the MIP tabulation supplies incremental intruded-porosity weights
over entry/throat-equivalent source bins (0.008–309 µm). The primary dimension
is the lower bin edge: a conservative representation that does not rename the
MIP result as CT throat geometry. A geometric bin midpoint is additionally
tested because the bins are logarithmic; it remains a sensitivity analysis,
not a replacement of the source values.

## Calculation and weighting

For each physical sample/case and each of the 4,452 strict-LPSN-supported,
cultured-species canonical width vectors (minimum, midpoint and maximum), the
analysis calculates `C(k) = P(D_constriction >= k × W)` for k=1.00–3.00 in
0.05 increments. Granite retains incremental-intruded-porosity weighting;
sandstone retains throat-object-count weighting. Sample distributions are never
pooled. Lithology summaries give equal-sample median, minimum and maximum.

Because MIP entry equivalents and CT/PNM resolved throats have different
observational meanings and weighting bases, values are not a cross-method
lithology ranking. Within-source/sample clearance sensitivity is defensible;
cross-method comparison is descriptive only and conditional on the stated
windows.

## Remaining limits

The sandstone result is especially resolution- and segmentation-conditioned;
the thresholded network may omit unresolved small throats and does not represent
the complete throat population. Granite is MIP entry-equivalent and its
Washburn-model assumptions are not restated in the downloaded table. Neither
method supplies cellular path connectivity, tortuosity, orientation,
deformability, surface attachment, or chemistry. The microbial distribution is
conditional on cultured, formally described species with recorded morphology,
not an environmental or subsurface distribution.
