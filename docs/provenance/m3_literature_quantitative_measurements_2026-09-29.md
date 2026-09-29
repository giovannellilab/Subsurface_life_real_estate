# M3 literature quantitative measurements v1 — provenance

Date: 2026-09-29 (Europe/Rome).

## Scope

This pass re-used the 40-record Literature Lithology Atlas v1. It did not add
a literature source, retrieve a CT/image volume, or copy a detailed M3
row-level dataset. The long-form output excludes the eight source IDs already
represented by detailed M3 ingestions.

Inputs were the tracked atlas source, observation, location and coverage
catalogues plus the local, gitignored Park & Santamarina Supplementary Table
S2 PDF already acquired for the prior audit. Park values were transcribed as
mean and standard-deviation parameters for source-labelled fitted
pore-diameter components; groups/components are retained and not interpreted
as individual pores or specimens.

## One bounded source-table recovery

The existing LIT-020 source record was rechecked using the small USGS document:

- Johnson, G. R. (1980), *Porosity and density of Kilauea Volcano basalts,
  Hawaii*, USGS Professional Paper 1123-B, Table 1.
- Temporary public retrieval: `https://pubs.usgs.gov/pp/1123a-d/report.pdf`.
- Downloaded only to `/tmp/johnson_1980.pdf`, 6,692,739 bytes; SHA-256
  `23a0edbe5226e6f7dbe49aaa0660c58c0d1e87233c93d9fb80e960b744db2b20`.
- The file is not copied into the repository and is not a public report asset.

The source register had incorrectly attributed this paper to Helz; its correct
author is Gordon R. Johnson. Table 1's 44 Kilauea Iki core rows (0.99–43.03 m)
were entered as paired but distinct helium-accessible and water-accessible
bulk-porosity values. They are not pore-size or throat observations.

## Outputs and safety

- `data/catalogues/literature_quantitative_measurements_v1.csv`: safe,
  long-form source measurements and exact locators.
- `data/catalogues/literature_quantitative_coverage_v1.csv`: evidence-depth
  counts by lithology.
- `data/processed/m3_literature_measurements_v1/`: local, ignored aggregate
  SVG figures only.

The report-builder allowlist copies only the aggregate SVG figures. It does not
copy catalogues, PDFs, raw datasets, caches, credentials, or row-level
processed third-party objects.

## Reproduction

```bash
MPLCONFIGDIR=/tmp/mpl-m3 .venv/bin/python scripts/build_literature_lithology_atlas.py
MPLCONFIGDIR=/tmp/mpl-m3 .venv/bin/python scripts/build_literature_measurements_v1.py
.venv/bin/python scripts/validate_literature_measurements_v1.py
```
