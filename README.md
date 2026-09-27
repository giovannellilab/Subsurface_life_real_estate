# Subsurface Life Real Estate

A data-driven framework for quantifying microbial cell dimensions, pore and fracture geometry, and the physical limits of subsurface habitability.

## Scope

This project develops an empirical framework linking microbial cell geometry to pore-throat size, pore connectivity, fracture aperture, and other physical constraints on microbial occupation and transport in the terrestrial subsurface.

The initial objectives are to:

1. Build an empirical dataset of microbial cell dimensions from formally described prokaryotes.
2. Compile pore-size, pore-throat, and fracture-aperture distributions across major rock and sediment types.
3. Quantify geometric accessibility of subsurface environments to microbial cells.
4. Extend existing pore-size approaches developed for sediments to consolidated and fractured rocks.

## Status

Milestone 1: the full 2026-09-14 operational BacDive v2 census has been
acquired, normalized, quality-controlled, and summarized offline. It contains
22,122 returned records with exact source `type strain: "yes"`, selected from a
101,320-record union of the culture index and LPSN-genus searches. The local
LPSN GSS CSV provides offline nomenclature and type-deposit evidence. This is
source coverage, not a representative distribution of all prokaryotes; see the
[full census report](docs/FULL_CENSUS_REPORT.md).

Milestone 3: a targeted pore-geometry reconnaissance and first controlled
ingestion are complete pending scientific review. The census identifies 22
candidate sources across siliciclastic, mudstone, carbonate, volcanic, plutonic
crystalline, ultramafic/serpentinized, and metamorphic space. The first pass
retains method-specific Lipnice MIP and Fontainebleau/Berea CT/PNM derived
tables locally; it does not publish raw geological files or pool distributions.
Seven additional source records remain acquisition-ready candidates. See the
[M3 pore-geometry resource](docs/PORE_GEOMETRY_RESOURCE.md).

## License

Software is released under the Apache License 2.0.

Licensing and provenance of datasets are documented separately.

## Reproduce the full census

Python 3.11+ is required. Acquisition and processing use the standard library;
the optional `analysis` extra supplies numerical summaries and plots. The default
processing command requires the
unmodified `data/raw/lpsn/lpsn_gss_2026-09-14.csv` and its pinned provenance at
`docs/provenance/lpsn_gss_2026-09-14.json`. It verifies the checksum and reads the
CSV locally; neither credentials nor LPSN network access are required.
Run these commands from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[analysis]'
.venv/bin/python scripts/acquire_census.py
.venv/bin/python scripts/process_bacdive.py \
  --manifest data/interim/census_2026-09-14/acquisition.json \
  --output-dir data/processed/census_2026-09-14
.venv/bin/python scripts/analyze_census.py
.venv/bin/python scripts/scientific_qc.py
.venv/bin/python -m unittest discover -s tests -v
```

Initial acquisition requires public BacDive v2 access. Repeating the command
resumes from checksum-verified cache entries. Processing and analysis are
offline. Raw responses and retrieval metadata live in
`data/raw/bacdive/census_2026-09-14/<request-hash>/`; the immutable selection
manifest is `data/interim/census_2026-09-14/acquisition.json`.

Normalized long-form JSONL/CSV, QC JSON/CSV, a Markdown report, processing
provenance, execution receipts, distributions, empirical CDF, taxonomic coverage,
outlier review, and plots are written under `data/processed/census_2026-09-14/`.
Reprocessing regenerates derived tables, never acquired raw data. Each strain
without morphology receives a missing-observation placeholder. Ambiguous values
and multiple observations are retained; dimensions are never imputed or averaged.

To reproduce the historical 100-record workflow or fetch all candidates in its
cached SPARQL index, use separate manifests and output directories:

```sh
python3 scripts/acquire_bacdive.py --all --manifest data/interim/milestone1_all/acquisition.json
python3 scripts/process_bacdive.py --manifest data/interim/milestone1_all/acquisition.json --output-dir data/processed/milestone1_all
```

The full-census population is operational: the culture-index search is combined
with all genus queries from the pinned local LPSN snapshot. The source does not
promise an atomic global database snapshot, so this workflow does not claim
unqualified coverage of every BacDive or prokaryote record. For a later snapshot,
give acquisition a new `--raw-dir` and `--manifest`, then point processing and
analysis at new derived-output paths. Never delete or overwrite an earlier
snapshot. A cache integrity error stops processing; preserve the affected cache
for investigation and use a new snapshot to reacquire.

The ID-spaced sample is deterministic and is not a random or balanced biological
sample. BacDive type status is a candidate filter, not independent proof of formal
nomenclatural eligibility. The initial workflow retains LPSN cross-references
embedded in BacDive alongside validation from the independently downloaded CSV.
Exact names and culture-collection identifiers are compared; synonyms and
conflicting evidence are recorded without replacing source names. The GSS export
has no domain/phylum or direct BacDive-ID column. API access is an optional future
update mechanism; the pipeline does not access credentials or scrape taxon pages.

The new LPSN outputs are `lpsn_validation.csv` (one row per strain),
`lpsn_candidates.jsonl` (all candidate evidence), and `lpsn_registry_qc.json`
(full-export schema/QC). They accompany the updated observations and QC report.

To explicitly select the snapshot:

```sh
python3 scripts/process_bacdive.py --lpsn-csv data/raw/lpsn/lpsn_gss_2026-09-14.csv --lpsn-provenance docs/provenance/lpsn_gss_2026-09-14.json
```

For a future downloaded export, register its provenance and checksum separately,
then pass those two paths. Do not overwrite the current raw snapshot. Historical
BacDive-only processing remains available through `--without-lpsn`, with a separate
`--output-dir`; it explicitly leaves nomenclature unverified.

## Project documentation

- [Source assessment](docs/SOURCE_ASSESSMENT.md): interfaces, terms, observed fields,
  coverage discrepancies, and references.
- [Data dictionary](docs/DATA_DICTIONARY.md): schema, conversions, and QC flags.
- [Data provenance](docs/DATA_PROVENANCE.md): immutable inputs and reproducible runs.
- [M3 pore-geometry resource](docs/PORE_GEOMETRY_RESOURCE.md): source census,
  method-aware schema, initial coverage, gaps, and first ingestion.
- [M3 first-ingestion report](docs/M3_FIRST_INGESTION_REPORT.md): source-level
  descriptive results, schema outcome, deferred artifacts, and review limits.
- [Full census report](docs/FULL_CENSUS_REPORT.md): population, QC, coverage,
  distributions, and review limits.
- [Scientific QC v1 report](docs/SCIENTIFIC_QC_V1_REPORT.md): immutable
  verification overlays, harmonized taxonomy, species weighting, and sensitivity.
- [Initial QC report](docs/MILESTONE1_QC.md): historical 100-record sample.
- [Scientific review](docs/SCIENTIFIC_REVIEW.md): unresolved eligibility, taxonomy,
  morphology, coverage, and reuse questions.
- [Third-party data](THIRD_PARTY_DATA.md): attribution and source-specific terms.
- [Contributing](CONTRIBUTING.md): setup and development conventions.

All acquired and processed data are Git-ignored. Compact provenance and review
reports are kept in `docs/`. Apache 2.0 applies to software; external data retain
their own terms.
