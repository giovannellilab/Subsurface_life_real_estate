# Contributing

Preserve the scientific scope in [README.md](README.md). Milestone 1 implements structured BacDive acquisition, conservative normalization,
and QC; see the README for current scope and reproduction commands.

## Local setup

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[analysis]'
python -m unittest discover -s tests -v
```

The base package has no runtime dependencies. The `analysis` extra supplies the
small numerical and plotting stack used only for the full-census summaries.
Setuptools is used only for packaging. Add dependencies only when a concrete task
requires them; document their purpose in the change. Record exact Python and
dependency versions for reproducible runs, and version-control environment lock
files when introduced.

## Repository layout

- `data/raw/`: original acquisition artifacts, immutable after acquisition.
- `data/interim/`: reproducible intermediate transformations and QC outputs.
- `data/processed/`: documented, analysis-ready derived datasets.
- `src/subsurface_life_real_estate/`: reusable acquisition, processing, QC, and
  analysis code as these capabilities are developed.
- `notebooks/`: exploratory work and narratives; move reusable logic into `src/`.
- `tests/`: automated tests using the standard-library `unittest` framework.
- `docs/`: data definitions and provenance conventions.

## Data stewardship

Never edit, overwrite, or clean acquired raw files in place. Store new source
versions as separate artifacts. Compute a SHA-256 checksum upon acquisition and
verify it before processing. Perform every transformation in `interim/` or
`processed/`; retain the raw input unchanged.

Before adding a source, record its provenance following
[DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md) and its reuse terms in
[THIRD_PARTY_DATA.md](THIRD_PARTY_DATA.md). Define fields, units, missing values,
and QC rules in [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).

Data artifacts in all three data directories are ignored by default, regardless
of size. Keep small, non-sensitive provenance records in `docs/provenance/` when
sources are introduced. Use stable external storage for large datasets, with
retrieval instructions and checksums. Do not force-add source data without
reviewing its size and redistribution terms. Small synthetic test fixtures may
live under `tests/fixtures/` when needed.

## Reproducible work and review

Record input identifiers and checksums, code revision (including uncommitted
changes), commands, parameters, random seeds where relevant, environment versions,
and output checksums for each run. Do not rely on notebook execution history:
notebooks should run in order from a fresh kernel and have bulky or sensitive
outputs cleared before review.

For future code, add meaningful tests for behavior, edge cases, and QC failures.
Keep routine tests offline and independent of local datasets. Run the test
command above and `git diff --check` before submitting changes. The offline test suite exercises normalization, acquisition behavior, and
processing reproducibility. Tests use synthetic fixtures, not local source data.

Explain the change, its scientific assumptions, validation, and any limitations
in the review description. Software follows the existing Apache 2.0 license;
external datasets retain their own terms.
