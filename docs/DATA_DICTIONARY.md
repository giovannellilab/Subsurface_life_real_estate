# Data dictionary

Schema version: **2** (LPSN-enriched processing; version 1 remains the explicit BacDive-only mode), Milestone 1. No representative cell diameter or derived
cell geometry is calculated. Canonical output is UTF-8 `observations.jsonl`;
`observations.csv` is a convenience view of the same rows. CSV nested values are
JSON-encoded, and scalar nulls are empty fields. Use JSONL to distinguish null,
empty string, and original JSON types. Each raw HTTP response is preserved byte
for byte, so omitted keys remain distinguishable from explicitly null keys.

## Row meaning and relationships

One row represents one BacDive `Morphology.cell morphology` entry. A dictionary
produces one row; an array produces one row per entry in original order, including
identical entries. No averaging, deduplication, or cross-observation dimension
pairing occurs. A strain without observations produces one explicit placeholder
with `observation_present=false`. Such placeholders count toward strain
missingness but not toward actual morphology-observation counts.

`observation_id` is the primary key within a processing snapshot. BacDive ID joins
observations to their strain; `raw_response_path` + checksum + record ID locates
the source; `source_reference_ids` joins observation `@ref` to source `Reference`
entries with `@id`. Observation order is not guaranteed stable across releases;
include raw checksum when comparing snapshots.

## Observation columns

| Field | Type / units | Definition and source |
| --- | --- | --- |
| observation_id | string | `<BacDive-ID>:<zero-based index>` or `<ID>:missing` |
| observation_index | integer / null | Position in original subsection; null for placeholder |
| observation_present | boolean | Whether an entry exists, even if malformed |
| species_name, genus, domain, phylum | string / null | Source taxonomic values; conflicting BacDive/LPSN values become null and are flagged; no taxonomic inference |
| bacdive_id | string | `General.BacDive-ID`, falling back to the API record key if absent |
| type_strain_status | original JSON / null | BacDive `type strain`; only exact `yes` confirms candidate status |
| type_strain_designations | object | Original `strain designation` and `Literature.culture collection no.`; deposit synonyms are not collapsed |
| lpsn_identifier | original JSON / null | Explicit embedded LPSN `id` if supplied; never constructed |
| lpsn_cross_reference | object / null | Complete embedded `LPSN` object, including its reference |
| nomenclature_validation_status | string | CSV validation state (see below); historical BacDive-only mode uses `unverified_bacdive_type_strain_candidate` |
| taxonomy_raw | object | Complete original `Name and taxonomic classification` section |
| cell_shape_raw | original JSON / null | Original `cell shape` value; not harmonized |
| cell_length_raw, cell_width_raw | original JSON / null | Original `cell length` and `cell width`, including inline units and punctuation |
| cell_length_unit_raw, cell_width_unit_raw | original JSON / null | Separate `cell length unit` / `cell width unit`, if present; no documented default is silently applied |
| length_min_um, length_max_um | number / µm / null | Converted bounds of an unambiguous positive length; single value gives equal bounds |
| width_min_um, width_max_um | number / µm / null | Converted width bounds; width is never synthesized from length or shape |
| length_unit_basis, width_unit_basis | string / null | `explicit_inline` or `explicit_field`; null if unit evidence is absent/unresolved |
| source_reference | array | Matching original reference objects; empty when missing/unresolved |
| source_reference_ids | array | Original observation `@ref` values; empty if absent |
| source_database | string | `BacDive`; LPSN-derived content is identified separately |
| source_record_identifier | string | Source strain identifier used to locate the record |
| source_record_doi | string / null | Original versioned `General.doi` when supplied |
| source_url | string | Exact acquisition request URL |
| retrieval_date | ISO 8601 UTC string | Successful HTTP acquisition timestamp, not processing time |
| raw_response_path | string | Repository-relative path for default workflow; may be absolute for custom cache paths |
| raw_response_sha256 | string | SHA-256 of original response bytes |
| morphology_observation_raw | original JSON / null | Entire unmodified observation, or null placeholder |
| morphology_context_raw | object | Entire morphology section, retaining other context and unrecognized keys |
| qc_flag | array of strings | Sorted review/missingness flags; multiple flags can coexist |
| qc_notes | string | Explains retention and context-flag limitations |

Uncertainty and measurement conditions remain in raw observations, morphology
context, and source references when supplied. No precision, measurement method,
uncertainty model, or growth condition is inferred.

## Conversion rules and QC flags

The parser accepts positive decimal single values and ordered ranges using
hyphen, en dash, em dash, or `to`. It accepts explicit µm/μm/um and English
micrometre/micrometer variants, nm (×0.001), and mm (×1000). Optional suffixes
`long`, `wide`, and `in diameter` must agree with the source axis. Missing units
are flagged; no default is inferred from the documentation. Conflicting units
are not resolved. Inequalities, comma notation, ± uncertainty, composite values,
and free-form descriptions retain raw values and null normalized bounds.

| Flag(s) | Meaning / handling |
| --- | --- |
| length_missing, width_missing, shape_missing | No value available; retained |
| length_/width_ + unparsed, malformed | Unsupported syntax or JSON type; normalized bounds null |
| length_/width_ + missing_unit, unknown_unit, conflicting_units | Unit cannot be resolved; bounds null |
| length_/width_ + reversed_range, nonpositive, axis_conflict, numeric_overflow | Invalid/contradictory quantity; bounds null |
| length_/width_ + extreme_review | Positive bounds below 0.05 or above 100 µm; bounds retained, provisional review trigger |
| width_exceeds_length_review | Width minimum exceeds length maximum in the same observation; both retained |
| shape_review | Shape outside conservative simple-shape vocabulary; original shape retained |
| multiple_cell_shapes | Strain observations report distinct raw shape values |
| complex_morphology_context | Morphology context mentions filaments, variable/pleomorphic forms, branches, spores, aggregates, appendages, stalks, chains, clusters, budding, or flagella; no geometric suitability inferred |
| no_cell_morphology | Placeholder for strain without a subsection |
| malformed_observation | Original non-dictionary entry retained for review |
| morphology_reference_missing, morphology_reference_unresolved | Reference missing or not matched to source bibliography |
| database_text_mined | Explicit database observation flag indicates text mining; project does no literature mining |
| nomenclature_unverified | Explicit BacDive-only mode did not run the CSV checks |
| type_strain_not_confirmed, domain_unconfirmed | Candidate's source evidence does not confirm expected status/domain |
| species_/genus_/domain_/phylum_taxonomy_conflict | BacDive and embedded LPSN disagree; normalized field null |
| lpsn_cross_reference_missing | No usable embedded LPSN cross-reference |
| record_id_conflict | API key and internal strain ID disagree |

Numeric bounds in complex-context rows express unit conversion only. They are
not a fit to a simple cell geometry, and are not cleared solely because a strain
can form spores or has flagella. All flagged rows require interpretation before
scientific modeling. No outliers are deleted.

## QC and provenance artifacts

- `qc.json`: distinct-strain coverage and missingness, observation counts, raw
  value frequencies, normalized-bound frequencies/extrema, shape counts,
  duplicate species/deposit relationships (original BacDive species labels, even
  when normalized taxonomy is null), multiple observations, and flag lists.
  Missingness denominator is confirmed BacDive type strains; observation-level
  counts include retained placeholders where explicitly indicated.
- `qc_records.csv`: observation-level flags linked to original responses.
- `QC_REPORT.md`: concise generated report; `docs/MILESTONE1_QC.md` is its review copy.
- `acquisition.json`: selected IDs, exact cached index, selection strategy,
  response keys, and missing/unexpected IDs. This manifest is immutable once written.
- `processing_manifest.json`: input and output checksums, commands, Python/platform,
  source-code hashes, Git revision and working-tree status.
- `run_receipts/*.json`: append-only execution timestamps and copies of processing
  manifests. Receipts vary by execution; data/QC outputs are deterministic.

## Offline LPSN enrichment (schema 2)

Name matching uses the original `taxonomy_raw.species`, not a reconciled name.
Its whitespace is normalized; spelling, capitalization, rank, and synonyms are
not altered. Subspecies names use the explicit `subsp.` component. A unique exact
CSV name selects a record for status evaluation, even if its status is adverse.
Multiple exact records yield an ambiguous result, not an arbitrary selection.
Embedded LPSN names and shared type deposits add candidate evidence only.

Culture-collection numbers from BacDive are split on commas; LPSN type lists on
semicolons. Only whitespace and case are normalized for deposit comparison;
punctuation and leading zeros remain significant. At least one exact normalized
deposit overlap corroborates a relationship. No overlap is inconclusive, not
proof that the strain is not a type. Genus type IDs are never matched as deposits.
Free strain-designation aliases are retained but not used for automatic validation.

| Added field | Type / meaning |
| --- | --- |
| lpsn_csv_record_no | string/null; unique exact original-name CSV match; distinct from the unchanged embedded `lpsn_identifier` |
| lpsn_csv_name | string/null; name composed from source name components |
| lpsn_csv_status_raw | string/null; original composite status |
| lpsn_validly_published_icnp | true/null; explicit ICNP-valid publication token present / not established; can be true for an illegitimate name |
| lpsn_current_correct_name | boolean/null; explicit correct-name marker present / absent, or no unique record |
| lpsn_type_deposit_match | boolean/null; overlap / no overlap, or evidence unavailable |
| lpsn_matching_deposit_keys | array; matching case/whitespace-normalized identifiers |
| lpsn_csv_address | string/null; original LPSN taxon-page address |
| lpsn_csv_record_lnk | string/null; original current-name record link, including empty string when source is blank |
| lpsn_linked_name, lpsn_linked_row_raw | string/object/null; linked row's name and full original record, without automatic name replacement |
| lpsn_csv_row_raw | object/null; full unique original-name match, preserving all CSV columns |
| lpsn_csv_record_ordinal | integer/null; 1-based CSV data-record position excluding header (not physical line number) |
| lpsn_csv_path, lpsn_csv_sha256 | strings; immutable local source and verified checksum |
| lpsn_download_date | date string; date registered in source provenance, not morphology retrieval date |
| lpsn_candidate_record_nos | array of strings; every exact original-name, embedded-name, or deposit candidate |
| lpsn_validation_flags | array of strings; strain-level review flags also included in `qc_flag` |

Validation states:

- `validated_name_and_type`: unique exact original name, explicit ICNP-valid
  publication, no detected adverse status, deposit overlap, and BacDive type=yes.
- `validated_name_type_unconfirmed`: same name/status evidence but type support
  is not confirmed. This does not validate a strain's type relationship.
- `nomenclatural_status_review`: unique name with missing explicit ICNP status
  or adverse status (illegitimate, rejected, spelling/correction issue, or in
  need of replacement). Explicit publication validity remains separately visible.
- `name_unmatched` / `name_ambiguous`: no exact name / multiple exact name records.

Synonyms can be validly published and supported; they receive
`lpsn_not_current_correct_name` and preserve the linked name without adopting it.
The state is an operational evidence assessment, not a universal biological
eligibility decision or inference of current culture availability.

Review flags are `lpsn_name_unmatched`, `lpsn_name_ambiguous`,
`lpsn_nomenclatural_status_review`, `lpsn_not_current_correct_name`,
`lpsn_type_deposit_missing`, `lpsn_type_deposit_no_overlap`,
`lpsn_record_link_unresolved`, `lpsn_bacdive_embedded_name_disagreement`, and
`lpsn_deposit_other_taxa`. The last flag indicates additional names sharing
collection identifiers; these may be synonyms or related ranks, not errors.
No existing taxonomy/morphology flag or source value is silently resolved.

`lpsn_validation.csv` has one row per BacDive ID with all enrichment fields.
`lpsn_candidates.jsonl` has one row per BacDive/LPSN candidate pair, preserving
match reasons, CSV ordinal, and full raw CSV row. This table is joined through
BacDive ID and LPSN record number; its source is the pinned CSV in the processing
manifest. `lpsn_registry_qc.json` describes the full export: ranks, status tokens,
repeated names, and unresolved record links. Unknown extra columns are retained;
malformed rows, duplicate IDs, or missing required headers stop processing.

QC now counts name-supported strains separately from name-and-type-supported
strains, and reports validation states and flags with a distinct-strain
denominator. Morphology counts and values remain unchanged. The GSS file has no
domain/phylum or direct BacDive-ID fields, so it does not resolve those gaps.

## Full-census review and exploratory outputs

Schema version 3 adds a strain-level provisional morphology classification after
normalization. `morphology_classes` is a sorted array and
`morphology_classification_basis` records that classes come only from structured
observation text plus within-strain shape or disjoint-range differences. The
classes are `straightforward_numerical_morphology`,
`numerical_but_incomplete_morphology`, `numerical_complex_morphology`,
`ambiguous_or_unparsable`, `multiple_observations`,
`multiple_conflicting_observations`, `pleomorphic`, `filamentous`, `branched`,
`stalked_appendaged`, `aggregate_chain_forming`, and
`spore_related_measurement`. They are review labels, not biological assertions
or geometry-model choices. A spore capability mentioned only in broader strain
context does not make a measurement spore-related.

`analysis/` contains strictly derived products. `species_analytical_index.csv`
groups original BacDive species labels and lists record IDs and evidence states;
it does not choose, average, or deduplicate morphology observations.
`taxonomic_coverage.csv` reports distinct type-strain coverage by original
BacDive phylum, retaining source taxonomy rather than reconciling it.
`exploratory_distributions.json` reports observation-level raw bounds and their
midpoints by source domain and each original BacDive phylum with at least 50
included observations. `width_ecdf.csv` gives the rank and empirical CDF of
the reported minimum width. `outlier_review.csv` is a tail-review table with raw
values, references, QC flags, and non-destructive scale flags. `taxonomic_bias.json`
records the descriptive association test and `morphology_qc.json` records class
counts. Plots are views of those tables.

The clean analytical rule is: retain a parsed axis from an observation only when
its classes contain none of `pleomorphic`, `filamentous`, `branched`,
`stalked_appendaged`, `aggregate_chain_forming`, `spore_related_measurement`,
`multiple_conflicting_observations`, or `ambiguous_or_unparsable`. The rule does
not remove values merely because they are numerically extreme. Each result states
this rule and remains source-observation level.

## Scientific QC v1 overlay

`scientific_qc_v1/` is a new derived milestone directory. Its
`analysis_eligibility_exclusions.csv` has one row for every normalized-width
observation not used by the earlier ECDF, with exact blocking morphology classes.
`suspect_value_verification.csv` has one row for every scale, unit, order, or
complex-morphology review trigger. `correction_overlay.csv` is a strict subset:
it contains only manually source-verified analytical corrections and preserves
the source-normalized columns beside corrected values.

`harmonized_taxonomy.csv` stores original BacDive taxonomy, local-LPSN name
evidence, embedded-LPSN hierarchy, chosen harmonized hierarchy, source, and
flags. The local GSS CSV has no hierarchy, so phylum through genus derive from
the already preserved BacDive-delivered LPSN cross-reference when present; the
original hierarchy is a flagged fallback. `species_analytical_table.csv` has one
row per accepted/harmonized species group. It never averages observations. Its
canonical row is present only for a unique highest-priority numerical candidate,
with a selection reason and provenance category.

`species_width_ecdf.csv` contains three species-weighted curves (minimum,
midpoint, maximum) for uncorrected, high-confidence-corrected,
strict-LPSN-name-and-type-supported, and likely-primary-description variants.
`species_width_distributions.json` provides all requested
summary statistics, including separate Bacteria and Archaea summaries.
`sensitivity_analysis.json` compares the observation-level analysis-eligible
minimum-width distribution with the three species-level variants.
`reporting_bias.json` and `harmonized_taxonomy_coverage.csv` are descriptive
source-coverage diagnostics. The publication-year field is explicitly low
confidence: it is the first four-digit year in the matched LPSN author string,
not a verified species-description year.

## M3 pore-geometry resource (reconnaissance schema)

M3 uses a separate schema version from the microbial observations above. The
tracked source catalogue is a metadata-only census, not an observation table:
`data/catalogues/m3_pore_geometry_source_catalogue.csv`. Its key fields are
`source_id`, lithology and sample-state fields, `geometry_class`, `method`,
resolution/window, quantitative-artifact description, access/terms, readiness,
and a scope note. `geometry_class` is restricted to `pore_body`,
`pore_throat`, `matrix_pore`, `grain_boundary_pore`, `microcrack`, and
`mixed_or_unresolved`; pipe-separated values describe source coverage only and
must become separate measurement rows after ingestion.

The implemented M3 tables are `samples.csv`, `measurements.csv`, and
`measurement_distribution.csv`, defined in `docs/PORE_GEOMETRY_RESOURCE.md`.
The first PNM source also uses `network_objects.csv`: one source-network object
per row with geometry class, source-supplied `EqRadius`, area, volume, channel
length, and coordination where present. Radius is not transformed in those
native records, and body and throat rows are never mixed.

Reference Lithology Dataset v1 uses local-only `geometry_values.csv`, whose
native fields remain source-preserving. Its separate analytical fields
`comparison_dimension`, `comparison_diameter_um`, `comparison_derivation`, and
`comparison_role` are populated only for an explicit source radius (`2 ×
radius`), a source diameter retained unchanged, or a documented MIP
entry/throat-equivalent dimension. Roles are `pore_body_accommodation`,
`throat_entry_nominal_transit`, and
`modelled_matrix_pore_cluster_accommodation`; unresolved size semantics and
connectivity-only records remain blank. These fields are for microbial-size
comparison only and do not create a universal pore-size variable.
There is intentionally no universal `pore_size` field. Preserve the source
quantity, its method/definition, resolution or detection limit, segmentation or
model, and a locator to the original file/table/column/bin. `sample_state` is a
distinct field, so fresh, altered, weathered, reacted, deformed, and
serpentinized material cannot become separate lithology classes. Native pore
values are not normalized or pooled; the explicitly limited comparison-diameter
overlay is the sole analytical coupling to microbial width during M3.
