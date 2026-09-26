# Scientific QC v1: species-level width harmonization

Snapshot: `census_2026-09-14`; QC overlay: `scientific_qc_v1`. This report
uses the existing immutable raw cache and normalized census. It adds analytical
tables only. It does not modify a raw API response, a normalized source field,
or a nomenclatural source record.

## Analytical layers

Four layers remain separate in every output:

1. **Raw source value** is the original BacDive JSON value and unit.
2. **Normalized source value** is the project’s unit conversion of that raw
   value, with no claim that the source unit is correct.
3. **Verified/corrected analytical value** exists only in `correction_overlay.csv`
   when a named source supports it; it never replaces either earlier layer.
4. **Species-level canonical value** is a single non-averaged observation only
   when the selection rule has a unique best-priority numerical result.

## Why 5,779 width strains become 4,647 ECDF observations

There are 5,849 normalized-width observations from 5,779 strains. The prior
ECDF is observation-level, so its correct denominator is observations, not
strains. It includes 4,647 observations from 4,624 strains. It excludes 1,202
normalized-width observations from 1,166 strains when one or more provisional
morphology classes indicate pleomorphism, filament/branch/stalk/appendage,
aggregate/chain, spore-associated measurement, conflicting observations, or
ambiguous/unparsable morphology. The exact row-level rationale is in
`analysis_eligibility_exclusions.csv`.

This subset is now called **analysis-eligible**, not “clean.” Eligibility means
only that the stored numerical width can be summarized without adding a geometry
assumption. It is not a source-verification result and does not certify that a
value represents a vegetative-cell cross section.

## Suspect-value verification overlay

The review table covers 1,288 observations flagged for nm/mm units, widths below
0.1 µm or above 5 µm, lengths above 50 µm, width exceeding length, pre-existing
scale flags, or complex morphology paired with a dimension. Two observations
have high-confidence unit corrections from original species descriptions:

| Species / BacDive ID | Immutable source | Verified analytical overlay | Outcome |
| --- | --- | --- | --- |
| *Croceitalea marina* / 140751 | 0.4–0.6 nm wide | 0.4–0.6 µm wide | `corrected_unit` |
| *Nioella aestuarii* / 141099 | 0.8–1.0 mm wide | 0.8–1.0 µm wide | `corrected_unit` |

The former is stated in the *C. marina* protologue, DOI
[10.1099/ijsem.0.002298](https://doi.org/10.1099/ijsem.0.002298).
The latter is stated in the *N. aestuarii* protologue, DOI
[10.1099/ijsem.0.002442](https://doi.org/10.1099/ijsem.0.002442). The table
records the accessible full-text-copy URL used to read each source value.

The remaining 1,286 records are explicitly `unresolved`; this includes
*Flavobacterium lutivivi* and *Virgibacillus pantothenticus*. Their source
references and source-normalized values are retained, but no correction is
justified by an independently verified source value in this milestone. This is
the largest remaining source-data uncertainty.

## Taxonomy and reporting bias

The harmonized taxonomy table has one row per 22,122 type strain. It uses the
BacDive-delivered embedded LPSN hierarchy for 21,970 strains and preserves the
original BacDive hierarchy beside it; 152 records use an original-taxonomy
fallback. Species identity uses the local LPSN exact-name match or linked current
name where available. This consolidates old/new phylum pairs such as
Proteobacteria/Pseudomonadota without overwriting the source fields.

After harmonization, morphology coverage still varies by phylum (18 groups with
at least 50 strains: χ²=526.64, df=17, Cramér’s V=0.154; p=4.57e-101). The
effect is substantially smaller than the unharmonized-label result, but remains
a source-coverage association, not a biological inference. Coverage is 177/762
for Archaea and 10,387/21,262 for Bacteria. The publication-year result is
exploratory only: it uses the first year in an LPSN author string, which is not
verified as the species-description year, so it must not be interpreted as a
vintage effect.

## Canonical species values and sensitivity

The table contains 21,667 harmonized species groups. A non-averaged canonical
analysis-eligible width is available for 4,557 species; 4,452 of these have the
strict `validated_name_and_type` LPSN status used for the principal distribution.
A value is selected only
if the highest available provenance category has one numerical candidate, or
multiple candidates with identical numerical values. Priority is: manually
verified primary description, likely primary description identified from a
cited title containing the species and `sp. nov.`, then structured BacDive
morphology with a cited source. Ties with different values remain unresolved.

Using canonical species values with high-confidence corrections and strict
LPSN name-and-type support:

| Width definition | N species | Median (µm) | 5th–95th percentile (µm) | ≤0.5 µm | ≤1 µm |
| --- | ---: | ---: | ---: | ---: | ---: |
| Minimum | 4,452 | 0.55 | 0.25–1.168 | 48.88% | 93.31% |
| Midpoint | 4,452 | 0.60 | 0.30–1.25 | 36.81% | 90.61% |
| Maximum | 4,452 | 0.70 | 0.35–1.40 | 31.58% | 87.15% |

Species weighting and strict nomenclature support change the reported-width-minimum
median by 0.00 µm from the analysis-eligible observation result (0.55 µm). The two high-confidence
corrections also change that median by 0.00 µm; they reduce the extreme upper
tail, from 800 to 500 µm. The likely-primary-description subset (n=1,627) has a
0.50 µm width-minimum median and 1.0 µm 95th percentile. These sensitivity
results support the limited descriptive statement that 1 µm is near the upper
part of these source-conditioned canonical width distributions. They do not
establish a universal microbial width, pore accessibility, or representativeness
across undocumented taxa.

## Morphology classes

The output reports both raw-shape categories and provisional morphology classes.
Rod-shaped rows dominate structured values (9,853 rows; 3,970 analysis-eligible
widths), followed by coccoid/spherical rows (1,160; 290). Filamentous,
pleomorphic, branched, stalked/appendaged, aggregate/chain, spore-associated,
and conflicting observations are retained but require separate geometry treatment
before any pore-transit analysis. No volume, equivalent diameter, or geometric
accessibility quantity is calculated here.

## Outputs and reproduction

All products are under `data/processed/census_2026-09-14/scientific_qc_v1/`:
the eligibility exclusions, suspect verification table, correction overlay,
harmonized taxonomy, canonical species table, species ECDF data and plot,
distributions, sensitivity summaries, morphology classes, and reporting-bias
tables. Regenerate them offline after the original census processing:

```sh
.venv/bin/python scripts/scientific_qc.py
.venv/bin/python -m unittest discover -s tests -v
```

The original normalized inputs and the raw cache are immutable. A future review
should add new source-verified records as a new overlay version rather than
editing `scientific_qc_v1` or a source field.
