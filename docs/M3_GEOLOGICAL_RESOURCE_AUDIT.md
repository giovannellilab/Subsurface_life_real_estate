# M3 geological resource scientific audit

Status: **audit for scientific review; not published** (2026-09-28).

This audit re-reads the source papers and deposits behind Reference Lithology
Dataset v1. It does not add lithology datasets or extend the pore × microbe
model. The audit is an overlay: native third-party measurements remain
unchanged, and all row-level audit outputs remain local and gitignored under
`data/processed/m3_geological_resource_audit_v1/`.

## Evidence hierarchy

The current resource contains **eight independent scientific publications/data
releases**, not 2.5 million independent geological observations. Evidence is
counted at five distinct levels:

1. independent publication/dataset;
2. reported geological locality, formation, or borehole;
3. physical specimen or explicitly different experimental case;
4. measurement on that specimen;
5. extracted object, network edge, model row, or distribution bin.

Objects and bins describe within-specimen distributions. They do not increase
geological replication. Multiple lithologies in one publication are retained as
separate materials but do not become independent publications.

### Exact coverage by lithology

| Lithology | Independent sources | Reported natural locations/formations | Physical specimens/cases | Geometry measurements | Geometry objects/bins | Connectivity/transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Basalt/volcanic | 1 | 1 regional quarry provenance | 1 | 1 | 66,495 | source whole-core porosity context only |
| Carbonate | 1 | 1 regional South China Sea setting | 5 | 10 | 43,159 | CT porosity and paper-reported coordination summaries |
| Granite | 1 | 1 locality and one borehole | 21 | 21 | 1,365 bins | MIP connected porosity from the same measurements |
| Mafic crystalline | 1 | 1 Atlantis Massif locality; 2 boreholes | 4 | 0 size measurements | 0 | bulk porosity plus pressure-series transport |
| Mudstone/shale | 1 | formation/site not securely documented in the local deposit | 2 | 4 | 10,799 model/class rows | 237 source model-parameter rows |
| Sandstone | 3 | 2 securely reported natural settings; Fontainebleau/Berea origins unspecified | 11 | 22 | 2,390,795 | coordination, total/effective porosity, permeability |
| Serpentinised ultramafic | 1 | 1 Atlantis Massif locality; 3 boreholes | 4 | 0 size measurements | 0 | bulk porosity plus pressure-series transport |
| Unconsolidated sand | 1 | 0 natural sites: laboratory pack | 1 | 2 | 4,102 | explicit topology, coordination, porosity, permeability, formation factor |

The Atlantis lithologies share one publication and one geological massif. The
five IODP boreholes are retained explicitly rather than counted as five
independent regional localities. Fontainebleau/Berea and Ottawa F42 are useful
reference materials, but their data releases do not support plotting a natural
sample coordinate. The South China Sea and Port Fairy sources give regional
provenance but not a defensible precise sample coordinate.

### Exact coverage by source

| Source | Geological unit/site | Specimens/cases | Geometry rows | Audit interpretation |
| --- | --- | ---: | ---: | --- |
| M3-001, Lipnice MIP | Lipnice granite, MEL-5 borehole, Melechov pluton | 21 | 1,365 bins | one deliberately heterogeneous borehole suite, not 21 granite localities |
| M3-002, Fontainebleau/Berea PNM | reference sandstones; collection localities unreported | 3 | 219,641 objects | one Fontainebleau dry specimen, one Berea dry specimen, one saturated Berea case |
| M3-RLD-003, South China Sea PNM | Nansha Islands carbonate sequence | 5 carbonate + 1 sandstone | 46,131 objects | one regional study; 61.75 µm carbonate and 30.45 µm sandstone voxels |
| M3-005, Port Fairy basalt | Bambstone Bluestone quarry, regional provenance | 1 | 66,495 objects | unreacted ungrooved laboratory-cut half-core; resolved bodies only |
| M3-RLD-004, Wilmslow PNM | Sellafield BH13B, one borehole | 7 | 2,168,182 objects | seven depths from one formation/borehole; all-object tables mix connected and disconnected objects |
| M3-023, Harvard shale | W23 and J24 marine shale | 2 | 10,799 rows | CTSTA classes plus model curves; not direct body/throat object measurements |
| M3-024, F42A | Ottawa F42 laboratory sand pack | 1 | 4,102 objects | one artificial pack, 1,246 nodes and 2,856 throat edges |
| M3-025, Atlantis Massif | five IODP boreholes at one massif | 8 | 0 size rows | four serpentinite/serpentinised ultramafic and four gabbroic cores; transport-only |

Machine-readable details are in `coverage_by_source.csv` and
`coverage_by_lithology.csv`. They also give connectivity rows, auxiliary object
attributes, and explicit network edges separately.

## Pore-geometry classification audit

### Lipnice granite

Staněk and Géraud selected 21 specimens from the single 150 m MEL-5 core to
represent alteration and fracture variability. Only seven are reasonable
matrix-reference specimens for a first comparison: fresh specimen 11; matrix
specimens 1_2, 2_2, 3_2, and 7_3; and 4_2/10_2 after the superficial fracture
material was ground away. Even these matrices contain grain-boundary,
intragranular, cleavage, and alteration-associated cracks.

The other 14 specimens explicitly include non-altered fractured rock, sealed or
partially open fractures, clay- or iron-oxide-rich fracture surfaces, a porous
fracture surface, cavity-rich altered matrix, and fault gouge. Their MIP values
must not be summarized as generic granite matrix pores. The exact specimen
assignment is in `lipnice_specimen_classification.csv`.

The MIP size variable is a source-defined entry/throat equivalent. The paper
defines it as the diameter of an idealized pipe pore or the half-size of the
smaller dimension of a crack pore under the Washburn model. It is therefore not
a direct pore-body diameter or a direct crack-aperture measurement. Intrusion
weights sum to source-defined total connected porosity.

### Sedimentary and volcanic image-derived networks

- Fontainebleau/Berea objects remain pore bodies and pore throats in the
  **resolved connected phase**. They are conditioned on 0.74 µm voxels,
  filtering, manual thresholding, and network extraction.
- South China Sea bodies and throats are maximum-ball network objects. The
  source paper supplies voxel sizes that the current registry omitted:
  **61.75 µm** for carbonates A–E and **30.45 µm** for sandstone S.
- Wilmslow bodies and throats are valid PerGeos object classes, but the ingested
  `all_*` files explicitly mix connected and disconnected objects. Their voxel
  sizes are **2.6860–2.8409 µm**, not unknown. An all-object throat statistic is
  not a connected transit-path statistic.
- F42A bodies and throats are valid Statoil-format network objects, but they
  describe a laboratory pack resolved at **9.996 µm**.
- The basalt table is an equivalent-**diameter** body distribution for the
  unreacted ungrooved half-core at **14.99 µm** voxels. The ingested table does
  not describe the artificial groove or reacted fracture, and it contains no
  throat distribution.

### Harvard shale and Atlantis crystalline rocks

W23/J24 `PORE-SIZE` is a source CTSTA connected-pore-cluster class whose native
class number has no physical unit. W23's companion `R/nm` curve is a **modelled
multiscale pore-cluster/domain radius distribution**. The paper describes
clusters connected through finite microfractures. It must be relabelled from
“matrix pore body” to a modelled cluster-domain result with microfracture
connectivity. `2R` is a valid analytical diameter conversion, but the result is
not a directly observed pore-body accommodation distribution and never a throat
transit distribution. J24 remains excluded from physical-size comparison
because its model table omits the `R` unit.

Atlantis Massif measurements contain no pore-size distribution. They remain
bulk porosity and pressure-dependent permeability/resistivity/elastic context
for natural serpentinite and gabbroic cores.

## Pore-size summaries

`sample_geometry_summary.csv` reports, for each physical sample and geometry
class, count, minimum, p5, p25, median, arithmetic mean, geometric mean, p75,
p95, maximum, and weighting basis. The numerical dimension is the **native
reported length in micrometres**: radius, diameter, or MIP entry size remains
labelled and is never silently pooled.

Selected sample-level ranges illustrate the measurement windows:

| Source / geometry | Weighting | Sample medians (native µm) | Sample p5–p95 examples / range | Interpretation |
| --- | --- | ---: | --- | --- |
| Lipnice MIP entry equivalent | incremental intruded porosity | 0.11–3.2 | individual p5 0.016–0.11; p95 74–240 | connected entry/crack-equivalent distribution; state strongly varies |
| Fontainebleau/Berea body EqRadius | object count | 2.74–4.54 | Case1 p5–p95 0.459–18.27 | resolved bodies only |
| Fontainebleau/Berea throat EqRadius | object count | 1.29–3.80 | Case2 p5–p95 0.358–3.50 | resolved connected throats only |
| South China Sea carbonate body radius | object count | 108–139 | source medians; 61.75 µm voxels | strongly lower-censored body population |
| South China Sea carbonate throat radius | object count | 54.3–97.0 | source medians; 61.75 µm voxels | strongly lower-censored network throats |
| Wilmslow body EqRadius | object count, connected + disconnected | 2.10–16.06 | p5 often 1.666 µm | resolution/segmentation floor is visible |
| Wilmslow throat EqRadius | object count, connected + disconnected | 5.85–11.62 | sample p5 1.08–1.80 | not a connected-path-only distribution |
| Basalt body EqDiameter | object count | 54.42 | p5–p95 18.61–319.82 | resolved bodies, not matrix micropore inventory |
| F42A body / throat radius | object count | 46.48 / 26.75 | body 5.71–91.39; throat 11.00–50.98 | laboratory pack, resolution-conditioned |
| W23 modelled cluster radius | modelled volume | 0.181 | p5–p95 0.000248–60 | model-domain weighting, not observed object count |

Arithmetic means are often much larger than medians because distributions are
strongly right-skewed. Geometric means are provided where all sizes and weights
are positive. Object-count distributions must not be read as pore-volume
distributions.

One deposit inconsistency was found: the South China Sea workbook contains
4,336 nonblank throat rows for carbonate A, whereas paper Table 4 reports 4,395
throats; the workbook maximum/mean are 667.501/123.104 µm whereas Table 4 gives
1044.66/127.04 µm. The ingestion faithfully reflects the workbook. The missing
59 rows are not imputed, and that sample's throat result is flagged.

## Porosity and connectivity audit

Porosity is not interchangeable across MIP, CT segmentation, saturation, and
wet/dry bulk measurements. The audit therefore retains type and measurement
scope.

| Source | Porosity result | Interpretation / flag |
| --- | --- | --- |
| Lipnice | connected MIP porosity 0.50–6.53%; median 2.01% | fresh specimen 11 is 0.50%; high values occur in altered, cavity-, fracture-, surface-, or gouge-bearing specimens |
| Fontainebleau dry | total 3.8%, connected resolved 3.0% | 0.74 µm image/segmentation conditioned |
| Berea dry | total 19.9%, connected resolved 19.6% | near-complete resolved connectivity; one physical dry case |
| Berea saturated | water-phase 15.8%, connected water phase 15.4% | not the dry whole-rock total |
| South China Sea | whole-image CT porosity 1.06% (sandstone S) and 7.35–23.41% (carbonates); REV2 0.83–23.99% | large REV/site heterogeneity; severe voxel censoring of finer pores |
| Port Fairy basalt | 9.75% segmented whole study core; 12% saturation on a separate bulk core | context only: neither value is the exact isolated half-core object table; discrepancy shows unresolved pore volume |
| Wilmslow | total 9.77–26.42%; connected 8.89–26.31% | most CT-resolved porosity connected; seven depths in one borehole |
| F42A pack | image porosity 33.0% | laboratory pack; not natural sediment porosity replication |
| Atlantis ultramafic | bulk 2.6–12.8% | natural cores; high values are serpentinisation/fracture-sensitive and no pore-size attribution is available |
| Atlantis mafic | bulk 0.9–2.9% | natural gabbroic cores; no size distribution |
| Harvard shale | no defensible absolute porosity recovered from the deposited model tables | do not scale the modelled W23 distribution to whole-rock compatible porosity |

Wilmslow permeability is 40–6040 mD in the paper. The archive CSV omits the
unit and contains Darcy-scale values; the audit reports 41.6–6040 mD while
preserving the raw values. F42A reports 59,000 mD for the voxel image and 61,000
mD for the network, with formation factors 5.8 and 3.6. Atlantis permeability
spans approximately 2×10⁻²² to 3.2×10⁻¹⁵ m² over pressure-dependent
measurements and varies by specimen and pressure; it is not reduced to a single
connectivity class. The PANGAEA velocity header says m/s while its 1.67–6.71
values are physically km/s-scale, so those values remain flagged and are not
converted.

### Porosity-aware Lipnice comparison

For MIP only, the source weights support a whole-specimen quantity: incremental
intruded porosity in entry-equivalent bins large enough for each microbial
width. Integrating over the 4,452 cultured species gives:

| Width distribution | Median normalized conditional overlap | Median whole-specimen intruded porosity above width | Specimen range |
| --- | ---: | ---: | ---: |
| Width minimum | 0.398 | 0.780% | 0.232–4.426% |
| Width midpoint | 0.387 | 0.714% | 0.225–4.342% |
| Width maximum | 0.381 | 0.680% | 0.222–4.281% |

The whole-rock values are much less visually dramatic than normalized overlap:
only a fraction of rock volume is intruded porosity, and the largest values are
often fracture/alteration associated. This is connected MIP-accessible
porosity above a local entry threshold, not cellular accessibility or connected
habitat.

## Geographic coverage

Seven defensible points are mapped: Lipnice MEL-5, Sellafield BH13B (converted
at map scale from published British National Grid reference NY 04506 00184),
and five source-coordinate IODP holes at Atlantis Massif. South China Sea,
Port Fairy, Fontainebleau/Berea, and the shale deposit are shown in the report
as region-only or unknown-coordinate evidence, not assigned invented point
coordinates. F42A is explicitly a laboratory standard.

The map therefore demonstrates a major geographic limitation: the resource is
not a global survey. It is a small collection of eight method-rich studies with
only three securely point-located geological settings.

## Park & Santamarina (2020) benchmark

Supplementary Table S2 was inspected from the article SI
([doi:10.1038/s41598-020-78714-3](https://doi.org/10.1038/s41598-020-78714-3)).
It provides an external fitted pore-**diameter** benchmark for 39 soils
(14 natural, 25 remoulded) and 44 intact rocks (23 carbonates, 17 sandstones,
4 shales). It is not pooled into the primary resource.

| Benchmark group | Reported mean pore-diameter range |
| --- | ---: |
| Natural soils | 0.11–178.4 µm |
| Remoulded soils | 0.16–233 µm |
| Carbonates | 0.37–31.5 µm across reported modes |
| Sandstones | 0.019–3.648 µm across reported modes |
| Shales | 0.004–0.112 µm across reported modes |

The comparison diagnoses a clear selection/window bias. Current carbonate CT
body medians are roughly 216–278 µm after radius-to-diameter conversion, far
above the benchmark modes, because the 61.75 µm voxels preferentially resolve
large pores. Current sandstone PNM bodies and throats are also shifted toward
the micrometre-to-tens-of-micrometres range, whereas many benchmark sandstone
modes are nanometre/submicrometre. Near-unity CT/PNM microbial overlap is
therefore expected after lower-tail censoring and cannot be extrapolated to the
complete rock pore system. W23 overlaps the shale benchmark at its fine end but
is a modelled multiscale cluster-domain curve rather than an independent direct
measurement. Supplementary Table S2 contains no crystalline-rock group and
cannot validate granite, basalt, gabbro, or serpentinite.

## Trust, relabelling, and exclusion decisions

**Remain trustworthy within their observation models:** raw/native values;
Lipnice specimen-level MIP bins and connected porosity; Fontainebleau/Berea
resolved connected PNM; Wilmslow source object tables and total/effective
porosity; F42A topology and network metrics; Atlantis bulk/transport series;
and the cultured 4,452-species width baseline.

**Require relabelling or qualification:**

- Lipnice 21-specimen summaries must be “one borehole, mixed
  matrix/fracture/alteration states”; a matrix-only sensitivity uses seven
  explicitly identified specimens.
- W23 becomes “modelled multiscale pore-cluster/domain scale with
  microfracture connectivity,” not “matrix-pore-body accommodation.”
- Wilmslow all-object throat overlap becomes “resolved all-object throat-size
  comparison,” not connected nominal transit.
- All CT/PNM near-unity results become “conditional on the resolved/extracted
  population.” Carbonate and Wilmslow voxel sizes are no longer unknown.
- Basalt porosity is contextual to related source cores, not an exact scale
  factor for the ungrooved-half distribution.

**Exclude from the relevant inference:** J24 from physical-size comparison;
Atlantis transport-only data from size overlap; carbonate A throat rows from
unqualified source-wide summaries until the workbook/paper discrepancy is
resolved; fracture surfaces, open fractures, cavity-rich matrix and gouge from
a “granite matrix” reference; and all disconnected Wilmslow objects from claims
about connected transit.

## Does the pore × microbe conclusion survive?

Only in a narrower form.

- The microbial-scale intersection in Lipnice survives at the specimen level,
  but the all-21 median is not a granite-locality replication estimate. The
  matrix-reference subset has midpoint-width conditional overlap median 0.351
  (range 0.242–0.606), versus 0.433 (0.237–0.695) for the 14 non-reference
  specimens. The porosity-aware all-specimen median is only 0.714% of bulk
  specimen volume.
- Fontainebleau/Berea's high resolved-throat overlap remains numerically
  correct for the segmented connected networks. It is not a complete-rock
  throat population.
- Near-unity F42A, carbonate, basalt, and Wilmslow overlap remains a property of
  coarse resolved object populations. It is not evidence that microbial size
  is unimportant in the unresolved whole rock.
- W23 still shows a modelled scale intersection with cultured cell widths, but
  it no longer supports a direct observed pore-body accommodation claim.

The defensible headline is therefore: **some measured or modelled geological
domains intersect cultured microbial widths, while the present CT/PNM sources
systematically under-observe finer pores; the amount of whole-rock pore space
and its connectivity must be reported separately.**

## Audit products and proposed public figures

The rebuilt report source uses four new local derived figures for review:

- `plots/geological_evidence_depth.svg` — sites, specimens, measurements and
  object/bin counts on deliberately separate axes;
- `plots/global_sampling_map.svg` — only source-supported point locations;
- `plots/porosity_context.svg` — source/type medians and sample ranges for
  total, connected, CT-resolved, MIP and bulk porosity;
- `plots/sample_geometry_summaries.svg` — equal-sample medians and
  between-sample ranges on a labelled log axis, preserving
  radius/diameter/entry-size conventions; full sample p5–p95 values remain in
  the audit table.

The intended public structure is: scientific question and conceptual
framework; microbial geometry resource; geological geometry resource; current
scientific results; milestones/research evolution; methods and technical
provenance; limitations/open questions; references/resources. Existing ECDFs
remain technical figures rather than headline evidence.
