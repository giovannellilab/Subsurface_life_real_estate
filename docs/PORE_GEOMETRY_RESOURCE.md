# M3 pore-geometry resource

Status: **first controlled ingestion complete; scientific review pending**
(2026-09-26). This remains a bounded source census, not an exhaustive review.
The first pass ingested two compact tabular records (Lipnice MIP and
Fontainebleau/Berea CT/PNM), without publishing their raw files or coupling
them to microbial data. See the [first-ingestion provenance record](provenance/m3_first_ingestion_2026-09-26.md).

The finite [Reference Lithology Panel v1](M3_REFERENCE_LITHOLOGY_PANEL_V1.md)
now records eight lithological endmembers and their explicit inclusion or
exclusion decisions. Only granite MIP entry/throat-equivalent bins and
sandstone PNM throat records currently support the first local geometric-fit
calculation. The calculation remains sample-level, preserves method-specific
weighting, and is not a universal pore-size distribution or accessibility model.

## Reference Lithology Dataset v1

The broader, deliberately method-labelled
[Reference Lithology Dataset v1](M3_REFERENCE_LITHOLOGY_DATASET_V1.md) extends
the two initial sources with a South China Sea carbonate pore network, an
unreacted basalt pore-body table, and UKGEOS Wilmslow Sandstone pore networks
with connected-porosity and permeability summaries. It holds pore bodies,
throats/entry equivalents, and connectivity metrics as distinct source-specific
quantities. Its microbial comparison uses a separate analytical comparison
diameter: `2 × radius` only where a source explicitly reports radius, retained
source diameter/entry-equivalent dimensions where supplied, and no conversion
for unresolved semantics. Pore-body accommodation and throat/entry nominal
transit remain separate; the constriction-specific `C(k)` pilot remains a
separate, narrower analysis.

### Targeted lithology-gap acquisition and ingestion

A small 2026-09-27 acquisition pass secured local-only, gitignored quantitative
artifacts for three remaining coverage gaps: Harvard marine-shale pore-size and
connectivity-workflow tables (CC0), an F42A laboratory-packed quartz-sand
micro-CT/PNM archive (CC-BY-4.0), and natural Atlantis Massif
serpentinised-ultramafic/gabbro bulk-porosity plus pressure-dependent
permeability/resistivity tables (CC-BY-3.0). They are now ingested into the
local Reference Lithology Dataset v1 with source-specific limits. Harvard
`PORE-SIZE` remains an uncalibrated CTSTA connected-pore-cluster class rather
than a body/throat/radius/diameter field; only the companion W23 curve with an
explicit `R/nm` label appears in the native-size display. F42A retains separate
network pore and throat tables, coordination, and topology for its 9.996 µm
resolved/extracted window. Atlantis Massif remains connectivity/transport-only,
never a size distribution. The Chogani & Plümper YODA serpentinite and Utrecht/
EPOS gabbro–serpentinite–greenschist microscopy data remain source-endpoint
blocked; no figure values were digitised. See
[the targeted acquisition record](provenance/m3_gap_acquisition_2026-09-27.md).

The tracked catalogue is
[`data/catalogues/m3_pore_geometry_source_catalogue.csv`](../data/catalogues/m3_pore_geometry_source_catalogue.csv).
Run `python3 scripts/validate_pore_catalogue.py` to validate its structural
invariants without network access.

## Scientific contract

M3 represents matrix pores, pore throats/entry constrictions, grain-boundary
pores, and microcracks. It deliberately does **not** set a pore/fracture size
cutoff: geometry and spatial context, rather than an arbitrary diameter,
distinguish in-scope microcracks from large-scale fracture geometry in M4. A
source may contain a macroscopic fracture; M3 retains only its matrix-adjacent
pore-network or microcrack observations and documents that selection.

`Pore size` is not a harmonized measurement. MIP reports a capillarity-modelled
entry/throat-equivalent size under mercury intrusion conditions, not a direct
pore-body diameter. CT and nano-CT describe only segmented voids above their
resolution and depend on segmentation; pore-network definitions travel with the
extraction algorithm. Adsorption, NMR, FIB-SEM, TEM, and microscopy have
different contrast mechanisms, assumptions, and size windows. Values from
different methods must not be pooled merely because they share a unit.

## Source census and coverage

Counts are candidate records, not independent specimens; multi-lithology
records contribute to each listed class.

| Lithological class | Candidates | Ready quantitative starting point | Principal representation | Immediate gap |
| --- | ---: | --- | --- | --- |
| Siliciclastic sandstone | 3 | Fontainebleau/Berea CSV pore networks | bodies and throats; micro-CT + PNM | benchmark and state diversity |
| Mudstone | 2 | West Trenton USGS MIP | throat-equivalent distributions | paired 3-D body/throat data |
| Carbonate | 5 | Estaillades micro-/nano-CT | multiscale matrix pores | processed numeric networks and natural-state diversity |
| Volcanic | 5 | basalt CT/PNM CSV | bodies, throats, connected paths | fresh natural matrix series at fine resolution |
| Plutonic crystalline | 3 | Lipnice granite PANGAEA | throats; MIP | paired 3-D matrix pores and microcracks |
| Ultramafic/serpentinized | 1 | serpentinite TEM/FIB-SEM publication | nanoscale matrix/grain-boundary pores | interoperable tables and cell-scale bridge |
| Metamorphic | 2 | Carrara micro-XRCT candidate | microcracks | natural, non-artificial matrix pore/throat datasets |
| Unconsolidated sediment | 1 | conceptual/data antecedent only | sediment pore-size framework | selected primary repository distributions |

Methods represented are MIP (granite, mudstone), micro-CT and extracted
networks (sandstone, basalt, carbonate), paired micro-/nano-CT (Estaillades),
FIB-SEM/TEM (serpentinite), and micro-XRCT (marble). The catalogue labels seven
records `A` (public quantitative artifacts ready for controlled acquisition),
seven `B` (valuable but needing a small eligibility/metadata check), and eight
`C` (context, discovery, or deliberately deferred). `A` does not mean
scientifically comparable.

## Minimal M3 data model

The model is deliberately long-form and method-aware. A `sample` identifies a
physical specimen; a `measurement` is one method/run/derived observation on it.
A numeric distribution is linked as a tabular artifact or long-form bins, never
as a universal `pore_size` column.

### `samples.csv`

| Field | Meaning |
| --- | --- |
| `sample_id` | Stable project identifier; never a source identifier alone. |
| `source_id`, `source_sample_id` | Link to catalogue/provenance and original specimen label. |
| `lithology_class`, `lithology_description_raw` | Controlled broad class plus preserved source description. |
| `sample_state` | Fresh/altered/weathered/reacted/deformed/serpentinized etc.; never a new lithology. |
| `collection_context` | Formation, location, depth, core/hand specimen context where supplied. |
| `material_scale_context` | Matrix, matrix adjacent to fracture, vein, or mixed; supports the M3/M4 boundary. |

### `measurements.csv`

| Field | Meaning |
| --- | --- |
| `measurement_id`, `sample_id` | Stable measurement key and sample join. |
| `method`, `method_variant_raw` | Controlled method family and unmodified source label. |
| `geometry_class` | `pore_body`, `pore_throat`, `matrix_pore`, `grain_boundary_pore`, `microcrack`, or `mixed_or_unresolved`; separate rows for multiple classes. |
| `quantity_name_raw`, `quantity_role` | Source quantity and role: `body`, `throat_or_entry_equivalent`, `void_fraction`, `connectivity`, `microcrack_geometry`, or `unresolved`. |
| `size_definition_raw` | Inscribed sphere, equivalent radius, local thickness, MIP entry equivalent, etc.; never inferred. |
| `value_unit`, `distribution_reference` | Unit and source table/file/column/bin or image-derived output. |
| `resolution_or_detection_limit_raw` | Voxel/pixel size, stated window, or limit; null if unreported. |
| `segmentation_or_model_raw` | Thresholding, network extractor, Washburn assumptions, etc., when supplied. |
| `connectivity_definition_raw` | Connected-porosity rule, coordination, percolation direction, or null. |
| `provenance_locator` | DOI/version plus file, sheet, table, figure, row/column, or processing output. |
| `qc_flags`, `comparability_group` | Explicit cautions and a grouping that prevents unreviewed pooling. |

`measurement_id + geometry_class + quantity_role` is unique within one
processing snapshot. `measurement_distribution.csv` holds linked bins with
bin bounds, values, value type (count/frequency/cumulative volume/etc.), and
original units. Images and raw files remain outside version control.

The first network-table ingestion also demonstrated a useful source-specific
object table: `network_objects.csv` retains one PNM object per row, with
`EqRadius`, area, volume, channel length, and coordination in their original
units and dedicated normalized columns. This is not a universal pore-size
table: body and throat records remain separate, and `EqRadius` remains radius.

## First ingestion snapshot

Two source records (24 samples/cases and 27 method/geometry measurements) are
now available under `data/processed/m3_first_ingestion/`. Lipnice contributes
1,365 non-empty incremental-intrusion bins across 21 granite specimens. The
Fontainebleau/Berea record contributes 46,467 pore-body and 173,174
pore-throat objects across three PNM cases. The [associated source article](https://doi.org/10.3389/feart.2018.00058)
documents 0.74 µm isotropic voxels, a 1024-cubed image reduced to a
500-cubed-voxel ROI, filtering, manual threshold segmentation, and a PerGeos
hybrid skeleton-based PNM. These provenance fields are now recorded in the
processed measurements; their network throats are resolved/segmented objects,
not a complete whole-rock throat population.

The initial coverage is therefore plutonic crystalline × MIP and siliciclastic
sandstone × micro-CT/PNM. It does not yet cover mudstone, carbonate, volcanic,
ultramafic, or metamorphic material with a processed quantitative artifact.
The MIP plot shows incremental intruded porosity by MIP entry-equivalent bin;
the sandstone plot shows source-supplied equivalent radii as separate body and
throat ECDFs. Neither is a cross-method comparison.

## Recommended first-ingestion set

First acquire metadata, licenses, exact files, checksums, and a small
representative quantitative artifact—not bulk imagery. The balanced first set:

1. **Lipnice granite MIP throat distributions** (M3-001): open, tabular
   crystalline constriction endmember.
2. **Fontainebleau/Berea PNM CSVs** (M3-002): paired pore-body and throat
   tables for a transparent sandstone benchmark.
3. **West Trenton mudstone USGS MIP** (M3-003): fine-grained sedimentary
   throat-equivalent endmember.
4. **Estaillades limestone micro-/nano-CT** (M3-004): carbonate multiscale
   architecture, separated by resolution.
5. **Basalt CO2-reaction CT/PNM CSVs** (M3-005): volcanic connectivity and
   state contrast; retain only M3-scale quantities.
6. **Serpentinite YODA publication** (M3-006): ultramafic nanoscale porosity;
   inventory derived tables/metadata before images.
7. **Carrara marble micro-XRCT** (M3-007): labelled metamorphic microcrack
   stress-test, gated on metadata and artificial thermal state.
8. **Microporous-cement natural-rock networks** (M3-009): carbonates and
   cemented sedimentary architecture, after duplicate-sample checking.

## Major gaps and review decisions

- Natural metamorphic matrix pores and throats are sparse; Carrara is an
  artificial-crack method case, not a natural prior.
- Crystalline rocks have throat and microcrack evidence but few paired,
  machine-readable 3-D body–throat distributions.
- Ultramafic evidence emphasizes nanoporosity; molecular transport does not
  establish microbial transit.
- Weathering, reaction, stress, depth, saturation, and alteration remain sample
  state/context, not lithology.
- A formal comparability matrix is needed before any cross-source quantile plot
  or microbial-accessibility calculation.
- For microcracks, aperture versus local minimum aperture versus graph
  constriction remains an M3/M4 interface decision. Large-scale fracture extent
  and connectivity remain M4.

M3 stops at an evidence and schema resource: it makes no inferred cell fit,
accessible porosity, or microbial × pore calculation.

## Literature Lithology Atlas v1

The source census and detailed ingestions are now complemented by a bounded
literature atlas rather than another acquisition sweep. The atlas contains 40
independent literature records (five per target high-level lithology), 49
quantitative/context observation rows, 34 mapped natural settings, 18 compact
state-stratified porosity/overview rows, and 28 reporting-grade
state-and-void-class envelope rows. It explicitly separates publication,
setting, specimen, measurement and object/bin evidence levels.

The atlas is not a harmonised pore-size database. Source-native radius,
diameter, MIP entry, image-object, adsorption-model, crack-aperture, vesicle and
bulk-porosity meanings remain labelled. Review and Park & Santamarina benchmark
rows inform envelopes without being counted as new field specimens. Laboratory
packs remain identifiable and are not placed on the natural-site map.

The scientific synthesis, coverage counts, preliminary envelopes and audit of
the current detailed M3 sources are in
[`M3_LITERATURE_LITHOLOGY_ATLAS_V1.md`](M3_LITERATURE_LITHOLOGY_ATLAS_V1.md).
The canonical tracked tables are:

- `data/catalogues/literature_lithology_atlas_sources_v1.csv`;
- `data/catalogues/literature_lithology_atlas_observations_v1.csv`;
- `data/catalogues/literature_lithology_atlas_locations_v1.csv`;
- `data/catalogues/literature_lithology_atlas_coverage_v1.csv`;
- `data/catalogues/literature_lithology_reference_envelopes_v1.csv`;
- `data/catalogues/literature_lithology_void_envelopes_v1.csv`;
- `data/catalogues/literature_lithology_porosity_summary_v1.csv`;
- `data/catalogues/m3_literature_envelope_audit_v1.csv`.

The quantitative companion,
[`M3_LITERATURE_QUANTITATIVE_MEASUREMENTS_V1.md`](M3_LITERATURE_QUANTITATIVE_MEASUREMENTS_V1.md),
re-expresses explicit published scalars, ranges, thresholds and distribution
parameters from that bounded source set in
`data/catalogues/literature_quantitative_measurements_v1.csv`. It excludes the
detailed M3 sources to avoid duplication and keeps Park & Santamarina fitted
pore-scale components as unresolved source-specific geometry rather than
calling them pore bodies or throats. Its coverage table is
`data/catalogues/literature_quantitative_coverage_v1.csv`.

The atlas changes interpretation, not native data: Lipnice must be stratified
by specimen state; CT/PNM results are resolved-population evidence; W23 is a
model domain rather than an observed body; and crystalline bulk porosity,
intrinsic nanoporosity and fracture transport remain separate quantities.
