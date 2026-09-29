# Data provenance

Status: Milestone 1 acquired a 100-record BacDive type-strain sample and its
SPARQL candidate index on 2026-09-14. Embedded LPSN content is preserved as
BacDive-delivered content. The independently downloaded full LPSN GSS CSV is
now the primary validation source; see [LPSN provenance](provenance/lpsn.md).
The local CSV is immutable and no API credentials are required.
See [BacDive source record](provenance/bacdive.md),
[raw inventory](provenance/bacdive_milestone1.json), and
[source assessment](SOURCE_ASSESSMENT.md).

The completed full-census run is separately preserved at
`data/raw/bacdive/census_2026-09-14/`, with selection manifest
`data/interim/census_2026-09-14/acquisition.json` and derived output directory
`data/processed/census_2026-09-14/`. It used only public BacDive v2 responses
and the immutable local LPSN CSV. See [full-census provenance](provenance/bacdive_census_2026-09-14.md)
and [the report](FULL_CENSUS_REPORT.md).

Scientific QC v1 is a derived, versioned overlay at
`data/processed/census_2026-09-14/scientific_qc_v1/`. Its input hash is recorded
in `scientific_qc_summary.json`; it never changes a raw cache entry or a
normalized source column. Each manual correction names its observation, source
identifier, source value, outcome, confidence, and reason. See
[Scientific QC v1](SCIENTIFIC_QC_V1_REPORT.md).

## Source records

For every external source, create a version-controlled record at
`docs/provenance/<source_id>.md` when acquisition begins. Assign a stable source
identifier and link it from derived dataset documentation and
[THIRD_PARTY_DATA.md](../THIRD_PARTY_DATA.md). Record:

- Full citation, creators or provider, title, and DOI or other persistent identifier.
- Source URL, exact download URL or query, source release/version, and access time
  in UTC using ISO 8601.
- Acquisition method, command or script, parameters, and selected scope. Exclude
  credentials and personal access tokens.
- Each raw artifact's relative path, original filename, byte size, format, and
  SHA-256 checksum.
- License or terms URL, applicable terms/version, required attribution,
  redistribution constraints, and any permission evidence.
- Known limitations, corrections, and relationships to other source versions.

When a source provides no version or explicit reuse terms, record that fact;
do not infer a version or assume permission to redistribute.

## Immutable originals

Preserve acquired bytes in `data/raw/<source_id>/<acquisition_id>/` and never
modify or overwrite them. Corrections and new downloads require distinct
acquisition identifiers and records. Keep archives as received and extract
working copies into `data/interim/`. Verify checksums before processing.
Git ignore rules prevent accidental tracking; they do not enforce immutability.

## Derived artifacts and runs

For each processing run, record its identifier, UTC execution time, input source
and acquisition identifiers, input checksums, code revision and any uncommitted
changes, environment versions, exact commands, parameters, and random seeds
where relevant. Record transformation and QC decisions, exclusions with reasons,
and output paths and checksums. Keep a traceable chain from processed records
back to original source records, including page/table/figure or row identifiers
where needed.

Store compact run records under `docs/provenance/`; keep large artifacts in the
ignored data directories or documented external storage. Record stable retrieval
locations and instructions so another researcher can obtain the same inputs.
Do not put credentials or restricted source content into committed records.

## Implemented cache and processing behavior

Each request is keyed by SHA-256 of Accept header + newline + exact URL. The
response bytes and metadata are published together through a staged directory
rename; successful entries are never replaced. Cache hits verify bytes/checksum
before returning. A interrupted transfer is retried on the next invocation;
resumption is at request/batch granularity, not HTTP byte-range granularity.
Only unpublished temporary staging files may be cleaned up automatically.

The acquisition manifest fixes the selection/index and batch keys. Reusing a
manifest path with different content is refused. REST batches contain at most
100 IDs, pagination is followed, and missing/unexpected IDs are reported rather
than silently accepted as complete coverage. Discovery probes that returned an
empty type index and the actual type-flag literals are retained in the inventory,
but do not enter the processed morphology table.

Offline processing verifies the index and response checksums, retains every
returned record, and rejects duplicate source IDs across response pages for
inspection. Output paths inside raw storage are refused. JSONL and QC outputs
are deterministic for fixed inputs/code. Each execution creates a separate UTC
receipt containing a copy of the processing manifest, including source-code
hashes and Git working-tree state. Since this work is uncommitted, code hashes
are essential alongside the Git revision. See `processing_manifest.json` and
`run_receipts/` under the processed output directory.

## Local LPSN snapshot

`docs/provenance/lpsn_gss_2026-09-14.json` registers the supplied filename, date
basis, source/download-page URL, reuse terms, size, and SHA-256. Exact download
time and request URL are unknown and explicitly null. Processing verifies the
CSV checksum/size before parsing; original source bytes are never rewritten.
The processing manifest includes the LPSN input and its provenance-file hash.
For a new export, retain both earlier files and register a separate snapshot.

Validation schema 2 adds LPSN evidence to observations and emits one validation
row per strain plus all candidate matches. The original embedded LPSN object,
BacDive taxonomy, morphology, and references remain unchanged. The default CLI
requires this CSV; missing files fail instead of silently falling back to an
unvalidated run. `--without-lpsn` is an explicit historical mode and requires a
separate output directory if LPSN outputs already exist.

## M3 source reconnaissance

M3 began with a metadata-only source census on 2026-09-26. The catalogue and
its methods/readiness labels are tracked at
`data/catalogues/m3_pore_geometry_source_catalogue.csv`; the evidence and
schema rationale are in `PORE_GEOMETRY_RESOURCE.md`; and the reconnaissance
record is `provenance/m3_source_reconnaissance_2026-09-26.md`. The first
controlled acquisition then added PANGAEA.898001 and Zenodo.1184144 v1; its
file-level checksums, local-only raw paths, transformations, and QC notes are
in `provenance/m3_first_ingestion_2026-09-26.md` and the derived run manifest.
The raw artifacts remain gitignored and immutable.

Reference Lithology Dataset v1 subsequently selected three additional public,
quantitative artifacts: South China Sea carbonate PNM statistics, an unreacted
basalt pore-size table, and UKGEOS Wilmslow Sandstone PNM tables. Their local
raw checksums, licenses, source URLs, and source-specific extraction decisions
are recorded in `provenance/m3_reference_lithology_dataset_v1_2026-09-27.md`.
The generated dataset tables remain local-only under
`data/processed/reference_lithology_dataset_v1/`; they retain method and
geometry semantics instead of creating a universal pore-size variable.

A bounded lithology-gap acquisition on 2026-09-27 retained five Harvard primary
artifacts plus three CC0 companion analysis artifacts, one CC-BY F42A
quartz-sand-pack network archive, and one CC-BY PANGAEA Atlantis Massif
gabbro/serpentinised-ultramafic bundle. The source-preserving ingestion retains
Harvard's uncalibrated CTSTA classes separately from its W23 labelled modelled
radius curve, F42A pore/throat network topology and metrics, and PANGAEA bulk
porosity/pressure-dependent transport as connectivity-only. Exact raw paths,
checksums, licenses, direct retrieval locations, transformations, and blocked
Utrecht/YODA routes are in `provenance/m3_gap_acquisition_2026-09-27.md`.

The 2026-09-28 geological-resource audit re-read the source papers and
deposited metadata, separated source/site/specimen/measurement/object counts,
classified fracture and alteration contexts, restored method-specific porosity
and resolution information, and inspected the Park & Santamarina (2020)
supplementary benchmark. Its source-paper inventory, local audit-file checksums,
access limits, and unresolved source discrepancies are recorded in
`provenance/m3_geological_audit_2026-09-28.md`. Audit row tables and derived
figures remain local-only under
`data/processed/m3_geological_resource_audit_v1/`.

The Literature Lithology Atlas v1 then added a bounded external-reality layer:
40 independent papers, datasets, expedition reports and reviews, with five
useful records for each of nine high-level lithologies. Its tracked source,
observation, location, coverage, compact-envelope, void-class-envelope,
porosity-summary and M3-audit tables are under
`data/catalogues/literature_lithology_*_v1.csv` and
`data/catalogues/m3_literature_envelope_audit_v1.csv`. The atlas does not copy
row-level third-party data and does not replace the detailed M3 distributions.
Review/benchmark rows are excluded from the conservative specimen minimum;
map coordinates retain exact/approximate/regional precision labels. Search,
extraction, counting and coordinate rules are recorded in
`provenance/m3_literature_lithology_atlas_2026-09-28.md`. Five generated SVGs
remain local-only under
`data/processed/m3_literature_lithology_atlas_v1/` pending scientific review.

The 2026-09-29 quantitative-measurement pass re-used that bounded source set;
it did not add a literature source or acquire any image volume. Its tracked
long-form table is `data/catalogues/literature_quantitative_measurements_v1.csv`
with corresponding lithology coverage in
`data/catalogues/literature_quantitative_coverage_v1.csv`. The Park &
Santamarina S2 supplement was transcribed as labelled fitted-distribution
parameters, not raw pore observations. A small temporary retrieval of the
already selected USGS Professional Paper 1123-B added its published Kilauea
table; the document itself remains outside the repository. Extraction scope,
source locators, counting rules and validation are recorded in
`docs/M3_LITERATURE_QUANTITATIVE_MEASUREMENTS_V1.md`.
