# Full BacDive type-strain morphology census

Snapshot date: **2026-09-14**. This report describes reproducible source
coverage and parsed source values. It does not estimate cell volume, infer cell
diameter, or make a claim about biological representativeness.

## Population and traceability

The completed v2 retrieval indexed 101,320 records: 96,656 from the culture
collection search and 4,664 additional IDs discovered through all 4,614 genera
in the local LPSN GSS file. Of the returned records, 22,122 have the exact
BacDive field `type strain: "yes"`; these are the processing population. The
other returned records are 77,878 `"no"` and 1,320 missing/null. No selected ID
was missing or unexpected.

This is an operational full census for the documented searches and access date,
not an assertion of an atomic or universally complete BacDive snapshot. The
immutable raw cache, each request's SHA-256 checksum, retrieval metadata, and
selection manifest are described in [the census provenance record](provenance/bacdive_census_2026-09-14.md).

## Processing and nomenclature checks

Processing kept 25,883 rows: 14,352 structured morphology observations and
11,531 explicit missing-observation placeholders. It found 21,985 original
BacDive species-label groups. One hundred seventeen groups contain multiple
BacDive type-strain records, contributing 137 records beyond the first group
member; this index reports them and does not collapse or average them.

The source domain field reports 21,262 Bacteria, 762 Archaea, and 98 unreported
or other values. LPSN GSS validation records 21,201 name-and-type supported
strains, 83 name-supported strains with type confirmation unresolved, 217 status
review cases, 597 unmatched names, and 24 ambiguous name matches. BacDive/LPSN
disagreements remain visible: 1,188 embedded-name discrepancies, 4,961 deposits
linked to other LPSN taxa, and 84 no-overlap type-deposit cases. These are
cross-database review signals, not automatic corrections.

## Morphology and dimension coverage

At the strain level, 9,816 records have shape, 5,897 have normalized length,
5,779 have normalized width, and 5,600 have both normalized axes in one source
observation. There are 2,729 strains with more than one observation. Nine rows
have parsing failures, 3,300 rows need ambiguity/unit review, and 21 rows meet
the existing extreme-value review trigger. All remain in the processed tables.

The conservative exploratory subset includes a parsed dimension only when its
observation has no provisional complex, conflicting, or ambiguous morphology
class. It remains observation-level: it neither averages repeat reports nor
selects a species representative. The subset contains 4,647 width and 4,735
length observations.

| Reported value (all prokaryote clean observations) | N | Median (µm) | 5th–95th percentile (µm) | Minimum–maximum (µm) |
| --- | ---: | ---: | ---: | ---: |
| Width minimum | 4,647 | 0.55 | 0.25–1.20 | 0.0003–800 |
| Width maximum | 4,647 | 0.70 | 0.35–1.40 | 0.0004–1,000 |
| Width midpoint | 4,647 | 0.60 | 0.30–1.25 | 0.00035–900 |
| Length minimum | 4,735 | 1.50 | 0.60–5.00 | 0.10–2,000 |
| Length maximum | 4,735 | 2.10 | 0.90–8.00 | 0.20–8,000 |
| Length midpoint | 4,735 | 1.95 | 0.80–6.00 | 0.20–5,000 |

For reported minimum width, 4.80%, 14.20%, 49.00%, 93.14%, and 99.33% of the
clean observation rows are at or below 0.2, 0.3, 0.5, 1, and 2 µm, respectively.
The complete threshold table and empirical CDF are in
`data/processed/census_2026-09-14/analysis/exploratory_distributions.json` and
`width_ecdf.csv`; [the plot](../data/processed/census_2026-09-14/analysis/plots/width_ecdf.png)
is locally generated and ignored by Git. The distribution JSON also gives the
same summaries for every original BacDive phylum with at least 50 included
observations; these are descriptive source-label strata, not reconciled taxonomy.

## Coverage bias and outlier review

Morphology availability differs strongly across original BacDive phylum labels
(22 groups of at least 50 strains; chi-square 6,158.40, 21 degrees of freedom,
Cramer's V 0.528; p is below floating-point reporting precision). All expected
cell frequencies are at least 24.42. This association measures source coverage,
not a biological effect. Old and newer phylum labels coexist in source records:
for example, morphology coverage is 68.5% for `Proteobacteria` (n=5,978) and
4.7% for `Pseudomonadota` (n=2,427). Such taxonomy-version differences make the
unreconciled source labels unsuitable for a biological comparison.

`outlier_review.csv` retains the 50 smallest and 50 largest values for each of
the four bounds, with raw strings, source references, morphology classes, QC
flags, and scale-review flags. Examples include nanometre-labelled dimensions
for *Flavobacterium lutivivi* and millimetre-labelled axes for *Nioella aestuarii*
and *Virgibacillus pantothenticus*. These records are flagged for human review,
not converted, deleted, or silently repaired.

## Outputs and reproducibility

The analysis directory contains a species analytical index, taxonomy-coverage
table, chi-square result, class counts, distributions, empirical CDF, outlier
review table, and two plots. Regenerate after installing the optional analysis
extra:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[analysis]'
.venv/bin/python scripts/acquire_census.py
.venv/bin/python scripts/process_bacdive.py \
  --manifest data/interim/census_2026-09-14/acquisition.json \
  --output-dir data/processed/census_2026-09-14
.venv/bin/python scripts/analyze_census.py
```

Acquisition uses neither LPSN credentials nor the LPSN API. The API remains an
optional future update route; a new external snapshot must receive new raw and
manifest paths.
