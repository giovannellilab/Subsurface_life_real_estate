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
