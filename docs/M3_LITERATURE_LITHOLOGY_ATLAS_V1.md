# Literature Lithology Atlas v1

Status: **scientific review draft; uncommitted and unpublished** (2026-09-28).

The Literature Lithology Atlas is a compact external-reality layer for the M3
geological resource. It does not replace the detailed M3 distributions and it
does not harmonise unlike methods into a universal pore-size distribution.
Instead, it records what a bounded set of papers, reviews, published tables and
small supplements say about the porosity and characteristic void scales of the
nine high-level lithologies relevant to this project.

The atlas deliberately distinguishes:

- an independent publication or dataset;
- an independent natural geological setting;
- a physical specimen or experimental case;
- a measurement on a specimen;
- a pore, throat, crack, fracture, vug, vesicle, network object or fitted bin.

Review rows and Park & Santamarina benchmark rows strengthen the envelopes but
are not counted as new site-level specimens. Repeated geometry rows for the
same specimen are counted once. Counts with an unspecified source sample size
are excluded from the specimen minimum.

## Evidence coverage

The first bounded release contains **40 independent literature records**. Each
target lithology is supported by five records; multi-lithology papers are one
publication, not multiple independent sources. The map contains **34 unique
natural settings**. Atlantis Massif is one setting that supports both mafic and
ultramafic evidence, so the per-lithology setting counts sum to 35.

| Lithology | Literature sources | Mapped natural settings | Documented primary specimens, conservative minimum | Park & Santamarina groups, separate benchmark |
| --- | ---: | ---: | ---: | ---: |
| Unconsolidated sand/sediment | 5 | 2 | 9 | 39 |
| Sandstone | 5 | 3 | 69 | 17 |
| Mudstone/shale | 5 | 5 | 96 | 4 |
| Carbonate | 5 | 3 | 5 | 23 |
| Basalt/volcanic rock | 5 | 5 | 11 | 0 |
| Granite/granitoid | 5 | 3 | 22 | 0 |
| Gabbro/mafic crystalline | 5 | 3 | 33 | 0 |
| Serpentinite/ultramafic | 5 | 7 | 15 | 0 |
| Metamorphic rock | 5 | 4 | 12 | 0 |
| **Total** | **40 unique records** | **34 unique settings** | **272 minimum** | **83 groups** |

The minimum is intentionally conservative. It excludes continuous borehole
logs, review populations, repeated studies of the same physical material,
unknown sample counts and Park & Santamarina groups that may overlap papers
already represented elsewhere in the atlas. It is therefore not the total
number of specimens that exist in the cited literature.

## Quantitative anchors by lithology

### Unconsolidated sand and sediment

Park & Santamarina Supplementary Table S2 spans fitted mean pore diameters of
0.11–178.4 µm in 14 natural soils and 0.16–233 µm in 25 remoulded soils. These
are method- and source-dependent fitted distributions, not a single sediment
population. Three undisturbed Alameda beach cores have porosity 37.1–40.3% and
mean grain coordination 7.71–8.31, while a pluviated sample of the same sand
has porosity 38.5% and coordination 7.45. F42A remains a useful laboratory
network standard (33% CT porosity) but is not natural depositional replication.

### Sandstone

The literature makes the CT selection problem explicit. Park & Santamarina's
17 intact sandstone groups have fitted mean diameters of 0.019–3.648 µm. In 15
Chang-7 tight-sandstone samples, total porosity is 1.20–13.98%, direct pore
observations span roughly 0.05–100 µm, and MIP median throat radii span
0.006–0.910 µm (study mean 0.127 µm). By contrast, the current CT networks
retain resolved EqRadius populations at or above their voxel/segmentation
windows. Wilmslow porosity (9.77–26.42%, connected 8.89–26.31%) is plausible,
but its all-object files mix connected and disconnected objects.

### Mudstone and shale

The shale matrix is predominantly nano- to submicrometre scale. Park &
Santamarina report fitted mean diameters of 0.004–0.112 µm for North Sea,
Mancos, Bakken and Woodford shales. Kuila & Prasad identify characteristic
approximately 3 nm illite–smectite-associated pores while warning that gas
adsorption and MIP cover different windows. West Trenton is the strongest
site-level breadth anchor: 94 MIP specimens from seven boreholes to about 35 m;
most porosities fall between 1% and 10%, but the full range spans about two
orders of magnitude. The paper reports that only about 0.1% porosity is in its
largest entry-size class.

W23 remains a modelled multiscale pore-cluster/domain radius, not an observed
matrix-pore body or throat. J24 still lacks a resolved physical radius unit.

### Carbonate

Carbonate rocks require explicit pore-type labels. Park & Santamarina's 23
groups span fitted mean diameters of 0.37–31.5 µm, while the micritic-limestone
review literature reports common 5–10 µm intercrystalline matrix pores and
secondary micropores below about 64 µm. Moldic pores, interparticle pores,
microvugs and vugs are bodies; they do not imply matching throat sizes.

The South China Sea carbonate porosities (7.35–23.41%) are credible, but the
61.75 µm voxel PNM body/throat radii (sample medians about 108–139 and
54.3–97.0 µm) describe a macropore network, not the complete carbonate pore
system.

### Basalt and volcanic rock

Dense and vesicular basalt are separate states. Fresh Reykjanes basalt has
7.93% open porosity and a bimodal MIP distribution: a crack-associated peak
near 0.1 µm and an equant-pore peak near 100 µm, contributing about one and
seven porosity percentage points, respectively. Kilauea Iki drill-core values
in the displayed USGS table range from 7.32% to 40.8% helium-accessible
porosity and vary sharply with depth/vesicularity. Saar & Manga show that
vesicle-connecting apertures can have radii about an order of magnitude smaller
than mean bubble radii. Mt Etna basalt has 4% connected porosity, a reported
mean MIP throat radius of 0.17 µm, and 65% of its porosity is accessed through
throat radii below 0.5 µm.

The Port Fairy object table is therefore a valid 14.99 µm-voxel resolved
body population, but neither a dense-basalt matrix inventory nor a vesicle-
connectivity distribution.

### Granite and granitoid

The atlas supports a provisional 0.1–2% total/connected porosity envelope for
fresh intact granite and a broader 0.5–15% state envelope for weathered,
altered, fractured or gouge-bearing material. The separation is more important
than the exact boundaries.

Lipnice fresh specimen 11 (0.50% connected MIP porosity) lies in the intact
range. The complete 21-specimen suite (0.50–6.53%) intentionally samples one
borehole's matrix, fractured, altered, fracture-surface, cavity-rich and fault-
gouge states. It is not anomalous once state is retained, but it is not an
intact-granite reference population. Westerly studies reinforce that
microcrack aperture and crack-surface density—not generic “pore size”—are the
relevant crystalline-rock quantities; thermally cracked material is a
laboratory-damage sensitivity.

### Gabbro and mafic crystalline rock

Fresh-to-moderately altered oceanic gabbro is consistently low porosity. The
Atlantis cores span 0.9–2.9%, while Hole 735B core/log interval means are about
1.5–3.4%. Hole 735B also demonstrates why core and borehole evidence must be
kept distinct: corrected log peaks and packer-test permeability are controlled
by fracture zones that core plugs can miss. The provisional intact envelope is
0.1–3%; altered/fractured intervals extend higher.

The existing Atlantis measurements are representative as bulk/transport
context, but they contain no pore-size distribution.

### Serpentinite and ultramafic rock

Two scale regimes coexist. Chogani et al. directly image predominantly
sub-100 nm lizardite/brucite-related pores (many below 10 nm); local FIB volumes
contain 0.2–0.7% porosity, TEM foils 1–3%, and a brucite-rich interface reaches
12 ± 4%. That interface value is local, not whole-rock porosity. Tutolo et al.
independently support intrinsic nanoporous serpentinisation products with
(U)SANS while retaining reaction fractures as a separate structure.

Bulk porosity is state sensitive. Atlantis ultramafic cores span 2.6–12.8%,
with high values linked to fractures/stress release. Dredged low-temperature
serpentinites span 10.5–24.7% without a proportional permeability increase,
showing that bulk and transport porosity differ. Mariana serpentinite mud-
volcano cores reach 37–51%, but are a special mud/saponitic state and must not
define coherent serpentinite matrix.

### Metamorphic rock

Metamorphic rocks cannot be reduced to one class without protolith, fabric and
state. Eight Songliao schist/mylonite specimens average 1.46% and 1.00%
porosity, respectively; more than 60% of schist pore volume is below 0.1 µm,
while mylonite is concentrated mainly from 0.05 to 1 µm. Structural and
weathering microfractures are recorded separately. Rutland quartzite provides
crack-aperture stereology, Himalayan schists provide MIP context, and marble
studies show grain-boundary/thermal microcracks. Thermally damaged marble is a
state sensitivity rather than an intact-matrix baseline.

## Preliminary reference envelopes

These ranges are **sanity envelopes**, not confidence intervals, universal
constants or pooled distributions. Size bounds are order-of-magnitude domains
supported by the listed source set; radius/diameter and weighting conventions
remain in the observation table.

The compact `body or matrix` and `throat/constriction` columns below are kept
only as a backward-compatible overview. They are **not** permission to pool
matrix pores, pore bodies, grain-boundary pores, microcracks, fractures, vugs
or vesicles. The reporting-grade
`literature_lithology_void_envelopes_v1.csv` has one material state and one
void class per row, and is used for the public void-class figure.

Cross-lithology porosity quartiles are deliberately unavailable for most atlas
classes. Many papers report ranges for unequal sample groups or use different
porosity definitions. The companion porosity summary reports an unweighted
median/quartiles only when at least four independent scalar source groups
support them; otherwise it preserves the state-stratified range and marks the
statistic unavailable rather than manufacturing pseudo-replication.

| Lithology / state | Total porosity (%) | Body or matrix scale (µm) | Throat/constriction scale (µm) | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Natural unconsolidated sediment | 25–60 | 0.1–500 | 0.01–200 | fabric and grain-size mixture dominate |
| Packed/remoulded sediment | 25–50 | 0.1–500 | 0.01–200 | preparation history is part of the result |
| Sandstone, conventional through tight | 1–30 | 0.002–200 | 0.003–10 | clay/intercrystalline, intergranular and dissolution domains coexist |
| Shale/mudstone intact matrix | 0.1–20 | 0.001–1 | 0.002–0.2 | organic/clay/mineral nanopores; fractures excluded |
| Shale/mudstone fractured/weathered | 1–30 | 0.001–10 | 0.002–10 | flow can be fracture dominated |
| Carbonate intact matrix | 0.1–35 | 0.01–100 | 0.01–100 | micrite/interparticle/moldic systems differ |
| Carbonate vuggy/dissolution state | 5–50 | 10–10,000 | 0.1–1,000 | vug body size does not imply throat size |
| Basalt dense/intact | 0.1–10 | 0.05–300 | 0.05–10 | cracks and equant pores separated |
| Basalt vesicular/scoria | 10–70 | 10–10,000 | 0.1–100 | aperture-limited connectivity |
| Granite fresh/intact | 0.1–2 | 0.005–10 | 0.005–10 | chiefly microcrack/grain-boundary space |
| Granite altered/fractured/gouge | 0.5–15 | 0.01–1,000 | 0.01–1,000 | special state, not intact reference |
| Gabbro fresh/intact | 0.1–3 | 0.005–10 | 0.005–10 | transport commonly fracture sensitive |
| Gabbro altered/fractured | 0.5–10 | 0.01–100 | 0.01–100 | logs may see fractures missed by cores |
| Serpentinite intact/moderate | 0.1–5 | 0.001–0.1 | 0.001–0.1 | intrinsic lizardite/brucite nanopores |
| Serpentinite fractured/weathered | 2–25 | 0.001–100 | 0.001–100 | bulk and transport porosity diverge |
| Serpentinite mud-volcano material | 35–55 | not assigned | not assigned | incoherent special material |
| Dense intact metamorphic rock | 0.1–3 | 0.002–1 | 0.002–10 | protolith/fabric must be retained |
| Weathered/foliated/thermally cracked metamorphic rock | 1–20 | 0.01–100 | 0.01–1,000 | crack-dominated special state |

## Geographic coverage

The atlas map includes exact boreholes/sites where supported and explicitly
labelled approximate-locality or regional-centroid points elsewhere. It now
spans North America, Europe, China, India, Australia, Hawaii and several
Atlantic, Pacific and Indian Ocean drilling/dredging regions. It remains
geographically uneven: Africa, South America, continental Antarctica and much
of Asia are absent, and hydrocarbon-reservoir and scientific-drilling settings
are over-represented.

Laboratory F42A and remoulded/packed materials are retained in the observation
table but are not plotted as natural sites. Multi-region reviews are not given
invented single coordinates. The coordinate provenance and precision of every
point are in `literature_lithology_atlas_locations_v1.csv`.

## Audit of the detailed M3 resource

| Detailed source | Atlas assessment | Scientific treatment |
| --- | --- | --- |
| Lipnice granite | special geological state | fresh/matrix subset is plausible; all 21 specimens are one heterogeneous borehole suite |
| Fontainebleau/Berea PNM | strongly resolution-conditioned; large-void biased | valid resolved connected networks, not complete sandstone throat populations |
| South China Sea carbonate PNM | strongly resolution-conditioned; large-void biased; source discrepancy | valid macropore network only; carbonate A throat discrepancy remains open |
| South China Sea sandstone S | strongly resolution-conditioned; large-void biased | one low-porosity, coarse-window macropore example |
| Port Fairy basalt | special state/window; large-void biased | resolved bodies from one half-core; contextual porosity is not table-specific |
| Wilmslow sandstone | porosity broadly representative; resolution-conditioned | retain seven depths; all-object throat files are not connected-path distributions |
| W23/J24 shale | special analytical construct; requires investigation | W23 model curve only; J24 excluded from physical-size inference |
| F42A sand pack | plausible laboratory standard; resolution-conditioned | topology/connectivity standard, not a natural sediment site |
| Atlantis gabbro | broadly representative in bulk porosity | transport/connectivity context only |
| Atlantis serpentinite | plausible for a fracture-sensitive serpentinised state | do not conflate bulk fracture porosity with intrinsic nanopores |

No native row-level M3 data become invalid because of the atlas. The problems
are interpretive: sample state, observation window and geometry class were too
easy to compress into lithology labels. The carbonate A count/maximum mismatch,
J24 unit absence, W23 model semantics and basalt table-specific porosity remain
the main issues that require source-level caution.

## Recommended geological-resource changes

1. Add source, setting, specimen, measurement and object/bin identifiers as a
   visible evidence hierarchy in every geological summary.
2. Make `sample_state` and `void_class` first-class display fields. At minimum,
   distinguish matrix pore, body, throat/entry, grain-boundary pore,
   microcrack, fracture void, vug, vesicle and unresolved/model domain.
3. Put total and effective/connected porosity beside every size distribution
   where the source permits; never imply that a conditional object distribution
   represents a large whole-rock pore volume.
4. Split CT/PNM results into a visibly labelled “resolved population” layer.
   Voxel size and segmentation/network extraction limits belong in figure
   legends, not only methods text.
5. Treat the literature envelopes as audit bands, not as replacement data or
   priors for a universal curve.
6. Keep Lipnice matrix-reference and fracture/alteration subsets separate and
   retain Atlantis mafic and ultramafic transport data as connectivity-only.

## Recommended public-report changes

The Geological Resource section should show, in this order:

1. evidence counts by lithology (source, setting and specimen counts);
2. the global map with precision/state legend;
3. state-stratified porosity envelopes;
4. method-labelled pore-body, throat, crack/fracture and vug/vesicle summaries;
5. a compact audit table for the detailed M3 sources;
6. known geographic, method and state-selection biases.

The headline M3 figures should not place coarse CT object distributions beside
nano/submicrometre MIP/adsorption distributions without an observation-window
band. Park & Santamarina should remain an external benchmark layer. Diagnostic
ECDFs and object-level figures belong in Methods/technical provenance.

## Files

Tracked, reviewable tables:

- `data/catalogues/literature_lithology_atlas_sources_v1.csv`
- `data/catalogues/literature_lithology_atlas_observations_v1.csv`
- `data/catalogues/literature_lithology_atlas_locations_v1.csv`
- `data/catalogues/literature_lithology_atlas_coverage_v1.csv`
- `data/catalogues/literature_lithology_reference_envelopes_v1.csv`
- `data/catalogues/literature_lithology_void_envelopes_v1.csv`
- `data/catalogues/literature_lithology_porosity_summary_v1.csv`
- `data/catalogues/m3_literature_envelope_audit_v1.csv`

Local, gitignored derived figures:

- `data/processed/m3_literature_lithology_atlas_v1/plots/literature_atlas_global_map.svg`
- `data/processed/m3_literature_lithology_atlas_v1/plots/literature_porosity_envelopes.svg`
- `data/processed/m3_literature_lithology_atlas_v1/plots/literature_atlas_evidence_depth.svg`
- `data/processed/m3_literature_lithology_atlas_v1/plots/literature_void_class_envelopes.svg`
- `data/processed/m3_literature_lithology_atlas_v1/plots/m3_porosity_against_literature_envelopes.svg`

The source register gives the persistent identifier/URL and role of all 40
records. Exact table, figure or text provenance is retained on every
observation row. The extraction and counting rules are recorded in
`docs/provenance/m3_literature_lithology_atlas_2026-09-28.md`.
