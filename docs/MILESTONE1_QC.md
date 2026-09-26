# Initial morphology QC report

This is an acquisition/normalization QC summary, not a population distribution estimate.

Selection: `evenly_spaced_sorted_ids` from 20,060 cached SPARQL candidates.
Retrieved 100 strains; 100 have BacDive type-strain status yes.
LPSN CSV name validation: 98 strains; name plus type-deposit support: 98.
Validation states: {'validated_name_and_type': 98, 'nomenclatural_status_review': 1, 'name_unmatched': 1}.
Rows: 119; actual observations: 75; missing-observation placeholders: 44.

| Type-strain coverage | Present | Missing |
| --- | ---: | ---: |
| shape | 52 | 48 |
| length | 28 | 72 |
| width | 26 | 74 |
| normalized_length | 28 | 72 |
| normalized_width | 26 | 74 |
| both_length_width_same_observation | 25 | 75 |
| both_normalized_same_observation | 25 | 75 |
| both_length_width_any_observation | 25 | 75 |

Strains with multiple observations: 17.
Duplicate species/type-strain groups: 0; shared deposit identifiers: 0.
Parsing-failure rows: 0; ambiguous-morphology/unit rows: 13; extreme-measurement rows: 0.
Missing requested IDs: []; unexpected IDs: [].

| Normalized bound (µm) | Observations | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| length_min_um | 29 | 0.2 | 16.5 |
| length_max_um | 29 | 0.75 | 16.5 |
| width_min_um | 26 | 0.1 | 0.9 |
| width_max_um | 26 | 0.2 | 1.1 |

## Interpretation and review

- Counts use distinct BacDive IDs for strain coverage. Bounds count individual observations; they are not independent species samples.
- Separate observations are never averaged or combined to manufacture a length/width pair.
- Missing and ambiguous data remain present. No outliers are removed. Values below 0.05 or above 100 µm trigger review only.
- Complex morphology/context flags require review before using numeric dimensions in any geometric model; no diameter is calculated.
- LPSN CSV checks distinguish name/status support from type-deposit overlap; current-name preferences and all discrepancies are retained without renaming. Culture availability is not established.
- The cached graph index may lag the REST API/portal. Full mode covers that index only.
- See qc.json for raw-value frequencies, normalized bound frequencies, missingness fractions, duplicate groups, and all flag counts; qc_records.csv links each flag to its observation.
