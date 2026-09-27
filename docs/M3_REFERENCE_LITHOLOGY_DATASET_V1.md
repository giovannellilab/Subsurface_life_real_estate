# Reference Lithology Dataset v1

Status: **representative first-order dataset for scientific review** (2026-09-27).
This version deliberately broadens the earlier constriction-only pilot without
claiming that all methods measure the same physical population. It preserves
source method, geometry role, native size convention, weighting, sample state,
and observation window. It is not a universal pore-size distribution.

## Included data

| Lithology | Dataset and samples | Pore-body data | Throat/constriction data | Connectivity retained | Important window/state |
| --- | --- | --- | --- | --- | --- |
| Granite | Lipnice MEL-5, 21 specimens; [PANGAEA.898001](https://doi.org/10.1594/PANGAEA.898001) | No | MIP entry/throat-equivalent bins, incremental intrusion-porosity weighted | No direct graph metric | 0.008–309 µm source bin window; facies/depth remain sample context |
| Sandstone | Fontainebleau/Berea, 3 cases; [Zenodo.1184144](https://doi.org/10.5281/zenodo.1184144) | EqRadius objects | EqRadius objects | Pore coordination number | 0.74 µm voxel, filtered/manual-threshold hybrid PNM; Case3B is oil/water saturated |
| Sandstone | Wilmslow Sandstone Formation, 7 samples; [UKGEOS Figshare](https://doi.org/10.17637/rh.12707840) | EqRadius objects | EqRadius objects | total porosity, effective/connected porosity, permeability (source unit unreported) | micro-CT/PerGeos; archive does not state voxel size; all-object tables include connected and disconnected objects |
| Carbonate | South China Sea carbonate REV A–E; [Mendeley Data](https://doi.org/10.17632/t8rj6b6gwn.1) | pore radius and volume | throat radius, length, and volume | no coordination field | micro-CT/maximum-ball network; workbook does not report voxel size |
| Basalt/volcanic | unreacted ungrooved basalt; [Mendeley Data](https://doi.org/10.17632/n72yhbppkj.1) | EqDiameter objects | No usable baseline throat table retained | no baseline connectivity table retained | 14.99 µm micro-CT voxel; manually thresholded, resolved pores only; laboratory core preparation retained as state |
| Mudstone/shale | W23 and J24 marine shale; [Harvard Dataverse](https://doi.org/10.7910/DVN/WBSHKX) and its [analysis companion](https://doi.org/10.7910/DVN/D1LDSO) | native CTSTA connected-pore-cluster classes; W23 additionally has a modelled multiscale cluster-radius curve | No | source `L(R/rmax)` model parameter only | CTSTA image resolution is not supplied. `PORE-SIZE` is neither labelled body nor throat, and has no physical unit. W23's companion curve labels `R/nm`; J24's does not, so only W23 can appear on the physical native-size display. |
| Unconsolidated sediment/sand | F42A Ottawa quartz sand pack; [Figshare](https://doi.org/10.6084/m9.figshare.1189259.v1) | Statoil network pore radius, volume, and shape factor | Statoil throat radius, channel/total lengths, volume, and shape factor | per-pore coordination, explicit edge topology, image/network permeability and formation factor | laboratory-packed sand; 9.996 µm voxel, 300<sup>3</sup>-voxel image; source network is resolution/extraction conditioned |
| Serpentinised ultramafic | Atlantis Massif harzburgite/dunite cores; [PANGAEA.873535](https://doi.pangaea.de/10.1594/PANGAEA.873535) | No | No | bulk porosity, pressure-dependent permeability, resistivity, velocities | natural drilled cores; connectivity/transport-only, with no reported pore-size window |
| Mafic crystalline | Atlantis Massif gabbro/olivine gabbro cores; [PANGAEA.873535](https://doi.pangaea.de/10.1594/PANGAEA.873535) | No | No | bulk porosity, pressure-dependent permeability, resistivity, velocities | natural drilled cores; connectivity/transport-only, with no reported pore-size window |

All original downloaded artifacts are immutable and gitignored under
`data/raw/m3_acquisitions/`; checksums and locators are in local
`source_provenance.csv`. The selected outputs are in
`data/processed/reference_lithology_dataset_v1/` and remain local-only.

## Remaining gaps and eligibility boundaries

The new shale, sand, ultramafic, and mafic records close important coverage
gaps but do not provide harmonised measurements. The Harvard native
`PORE-SIZE` variable is a CTSTA connected-pore-cluster size class: its
`FRACTION` column is the supplied cluster-size-weighted percentage (verified
against `PORE-SIZE × NUMBERS`), not a body/throat distribution or a physical
length. `RADIUS^2` remains an auxiliary source column with unresolved unit and
convention. The W23 companion model labels `R/nm` and `V/nm3`, so it is retained
as a **modelled matrix-pore-cluster radius** curve in the native-size comparison;
J24 is retained but excluded from that physical-size display because its `R`
unit is absent. Neither is a constriction dataset.

The F42A pore and throat records are defensible source-network distributions,
but only for the 9.996 µm-voxel segmented/extracted network; they do not claim
the unresolved fine-pore population. PANGAEA transport measurements are
connectivity-relevant only and are never converted to a size distribution. A
natural, interoperable serpentinite pore-size table and natural metamorphic
pore/throat data remain gaps: the Chogani & Plümper YODA source and Utrecht/
EPOS gabbro–serpentinite–greenschist microscopy routes are endpoint-blocked,
and Carrara marble is a thermal-crack experiment. No figure-derived values were
substituted.

## First-order microbial comparison

The comparison uses 4,452 strict-LPSN-supported cultured species and retains
canonical width minimum, midpoint, and maximum separately. For each sample,
geometry class, method and weighting basis it calculates the descriptive value
`P(D_comparison >= W)`, using a separate, provenance-tracked analytical
`comparison_diameter_um` field. Explicit source radii use `2 × radius`; source
diameters and Lipnice MIP entry/throat-equivalent dimensions are retained; and
unresolved semantics receive no comparison value. Native source values are not
replaced. Pore bodies, throats/entry equivalents, and matrix-pore clusters have
separate roles, so this must not be called accessibility, habitability, or a
cross-method lithology ranking.

The stricter prior `C(k)` calculation is retained only for the explicitly
defined Lipnice MIP entry-equivalent and dry Fontainebleau/Berea throat
comparison dimensions. It is not extended automatically to body-radius or
heterogeneous-method data.

Lithology-method summaries give equal sample weight. They never concatenate all
objects across samples or sources; the large UKGEOS networks cannot dominate
smaller samples. The plotting layer uses fixed log bins only for display; the
comparison-diameter overlap is calculated on individual processed values.

Newly eligible comparison groups are the W23 modelled shale matrix-pore-cluster
diameter (`2R`) and F42A pore-body/throat comparison diameters (`2 × radius`).
Raw CTSTA shale classes, the ununit-labelled J24 model curve, and PANGAEA
transport-only records are not plotted as physical sizes. Pore-body and W23
results are local accommodation only; throat/MIP entry results are nominal local
transit fit only. The F42A result remains resolution-conditioned rather than a
clearance calculation; the existing `C(k)` pilot remains limited to its
separately justified granite and sandstone constriction dimensions.

## Interpretation boundaries

The data demonstrate broad method-conditioned size coverage, not a complete
whole-rock void inventory. CT values are resolution-, segmentation-, and
network-extraction-conditioned. The comparison dimension makes radius/diameter
handling explicit, but cannot establish cell transit without an explicitly
justified constriction dimension. Connectivity metrics are source-specific and
are reported alongside, not folded into the overlap.
