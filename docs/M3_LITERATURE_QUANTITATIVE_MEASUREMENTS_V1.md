# M3 Literature Quantitative Measurements v1

Status: **scientific-review draft; uncommitted** (2026-09-29).

This resource turns the bounded Literature Lithology Atlas v1 into a
reviewable long-form collection of explicit, published numerical observations.
It complements the detailed M3 source ingestions; it does not copy their
row-level third-party objects, raw images, or distributions.

## What is counted

The parent atlas contains 40 independent source records, 49 context rows and
34 mapped natural settings. Eight sources are detailed-M3 exemplars and are
excluded from this table to avoid double counting. Thus, outside detailed M3,
the selected atlas has **32 source records** and **36 context rows** (31 when
the separate Park & Santamarina context rows are excluded). Context rows are
source/sample-group descriptions, not automatically measurements.

The long-form table has **345 measurement rows** and **365 explicit numeric
values**. A row is one reported scalar, source-reported range, threshold,
distribution parameter, or individual table value. It is never an individual
pore unless the source itself reports one. Reported ranges remain one row,
not fabricated endpoint observations.

| Provenance layer | Sources contributing numerical rows | Rows | Numeric values | Meaning |
| --- | ---: | ---: | ---: | --- |
| Park & Santamarina benchmark | 1 | 214 | 214 | mean and standard deviation for 107 fitted pore-scale components in 83 named S2 groups |
| Other already selected literature | 16 | 131 | 151 | source table/text/range/threshold observations, including 44 Kilauea core specimens measured two ways |
| **Total** | **17** | **345** | **365** | no detailed-M3 row-level data copied |

Park & Santamarina's S2 components are explicitly labelled `fitted pore-scale
distribution` and **unresolved geometry**. They are useful cross-study
benchmark parameters, but are neither automatically pore bodies nor throats,
and neither their components nor their fitted parameters are independent
physical pores or specimens.

## Table and semantics

[`literature_quantitative_measurements_v1.csv`](../data/catalogues/literature_quantitative_measurements_v1.csv)
has one source-faithful measurement row. It retains source, lithology, state,
natural setting and location precision; sample/group and parent-component IDs;
measurement family; geometry class; statistic; scalar/range/auxiliary value;
unit; native definition; method; weighting; observation window; depth/stress
context; and an exact table/figure/text locator.

`literature_quantitative_coverage_v1.csv` reports evidence depth by lithology.
Its source, natural-setting and conservative-specimen fields exclude detailed
M3. The separate Park columns retain the benchmark rather than treating it as
new field replication. A specimen represented in a paper is not counted as an
individually extracted measurement unless a specimen-level number was actually
transcribed.

Void classes are not harmonized. `fitted pore-scale distribution`, matrix pore,
pore body, throat/entry constriction, crack/fracture, vesicle/vug and bulk
accessible porosity remain separate labels. The existing state-and-void-class
reference envelopes remain sanity checks, not measurements or priors.

## Bounded extraction decisions

The selected-source set was used first; no new literature source was added.
The only additional retrieval was the small, already selected USGS Professional
Paper 1123-B. Its correct author is **Gordon R. Johnson (1980)** (the atlas
source record was corrected from an erroneous Helz attribution). Table 1 adds
44 Kilauea Iki core specimens with separate helium-accessible and
water-accessible porosity at 0.99–43.03 m depth. These are bulk accessibility
measurements in vesicle/crack-dominated basalt, not pore-size observations.

Several selected reviews, narrative papers, continuous logs and papers with no
recoverable small numerical table remain context/envelope evidence only. That
is a documented gap, not a zero. In particular, direct scalar depth remains
thin for fresh granite, gabbro and several metamorphic classes; detailed M3
exemplars remain the better within-sample geometry evidence for their own
materials.

## Derived review figures

The build script writes local, gitignored figures only:

- `data/processed/m3_literature_measurements_v1/plots/literature_quantitative_measurement_depth.svg`
- `data/processed/m3_literature_measurements_v1/plots/literature_published_porosity.svg`
- `data/processed/m3_literature_measurements_v1/plots/literature_published_void_sizes.svg`

They display published summaries by lithology, not a pooled universal pore-size
distribution. Squares identify Park S2 fitted components; circles identify
other selected literature; lines are one source-reported range. The atlas map
continues to contain one point per independent natural setting and excludes
laboratory packs from the natural-site layer.

## Reproduction and validation

```bash
MPLCONFIGDIR=/tmp/mpl-m3 .venv/bin/python scripts/build_literature_lithology_atlas.py
MPLCONFIGDIR=/tmp/mpl-m3 .venv/bin/python scripts/build_literature_measurements_v1.py
.venv/bin/python scripts/validate_literature_lithology_atlas.py
.venv/bin/python scripts/validate_literature_measurements_v1.py
```

The validator verifies the 107 Park mean/standard-deviation pairs, 83 named S2
groups, non-overlapping detailed-M3 scope, numeric/range consistency, source
locators and coverage totals. It cannot turn source-defined fitted scales into
directly comparable pore geometries.
