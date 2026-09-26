# Milestone 1 source assessment

Access date: **2026-09-14**. This assessment combines official documentation with
the historical engineering sample under `data/raw/bacdive/milestone1/` and the
completed full v2 census under `data/raw/bacdive/census_2026-09-14/`. See
[provenance inventory](provenance/bacdive_milestone1.json) for exact URLs, times,
byte counts, and SHA-256 hashes. No PDFs or primary-literature text were mined.

## Interfaces and access

**BacDive.** Use the public REST **v2** endpoints: `fetch`, `taxon`,
`culturecollectionno`, `sequence_16s`, and `sequence_genome`. Authentication was
removed in February 2026. Legacy endpoints are frozen at April 2025 content.
Fetch accepts up to 100 semicolon-separated IDs; paginated responses carry
`count`, `next`, `previous`, and `results`. The project uses the standard library,
so the optional BacDive client is unnecessary. These are the current instructions;
older registration guidance should not drive implementation.
[Official API documentation](https://hub.dsmz.de/wiki/bacdive/api/).

The [official SPARQL interface](https://sparql.dsmz.de/bacdive/) exposes a
strain-level type flag and BacDive identifier. The pipeline uses the backend
`https://sparql.dsmz.de/api/bacdive` to discover candidate IDs, then REST v2 for
complete records. The precise selection query is in `acquisition.py` and the
cached request URL. No authoritative requests-per-second quota was found in the
reviewed documentation; the project conservatively makes sequential requests
with a one-second delay, retries transient errors, and respects Retry-After.

**LPSN.** The primary reproducible source is now the full user-supplied GSS CSV
`data/raw/lpsn/lpsn_gss_2026-09-14.csv`; see its
[provenance and checksum](provenance/lpsn.md). It is read locally and checked
against its recorded hash before processing. API login is no longer a milestone
blocker. The [API](https://api.lpsn.dsmz.de/) remains an optional future update
route, with authenticated JSON fetch and search endpoints; no credentials are
accessed by this implementation. No numerical API quota was established.

## Reuse and publication

BacDive declares **CC BY 4.0** and asks commercial users to contact its maintainers.
Preserve attribution and source references, and resolve that additional request
before a downstream commercial release. Images can carry separate rights and
are not downloaded. The current requested citation is Schober et al.,
*BacDive in 2025: the core database for prokaryotic strain data*.
[Official terms and citation](https://bacdive.dsmz.de/about).

LPSN declares **CC BY-SA 4.0** for its data, including API and downloads. It permits
license-compliant commercial use; other arrangements require agreement.
Publications must cite its latest listed reference, and electronic redistribution
must link to the relevant LPSN taxon page. Automated acquisition is allowed only
through the API, official downloads, or explicit permission. Current citation:
Freese et al. (2026), *TYGS and LPSN in 2025*,
[doi:10.1093/nar/gkaf1110](https://doi.org/10.1093/nar/gkaf1110), with access date.
Assess share-alike obligations for combined outputs before redistribution.
[Official copyright and access terms](https://lpsn.dsmz.de/text/copyright).

The software's Apache 2.0 license does not relicense these datasets. Local data
and derived tables remain Git-ignored. These findings record source terms;
they do not establish a new license for the combined dataset.

## Fields and identifiers

The [BacDive field documentation](https://www.api.bacdive.dsmz.de/strain_fields_information)
lists cell shape, length, width, unit fields, and source references. Missing fields
may be omitted, and a subsection can contain one or multiple entries. Real v2
responses use display labels such as `Morphology`, `cell morphology`, `cell length`,
and `@ref`, rather than the documentation's internal names such as `cell_len`.
Observation `@ref` values resolve against the record's `Reference` entries and
`@id`. Reference metadata is retained without retrieving cited publications.

BacDive records contain `General.BacDive-ID`, versioned strain DOIs, type-strain
status, strain designations, and culture-collection deposit numbers. Embedded
`Name and taxonomic classification.LPSN` contains taxonomic names and a reference,
but none of this sample's embedded entries supplies a numeric LPSN record ID.
The project preserves this cross-reference object instead of inventing an ID.

The [LPSN content specification](https://lpsn.dsmz.de/text/lpsn-api) documents
`id`, `full_name`, `type_strain_names`, `validly_published`, `is_legitimate`,
`lpsn_correct_name_id`, `lpsn_parent_id`, `lpsn_address`, and `lpsn_version`.
Missing fields are omitted. These support future explicit nomenclature checks
and culture-deposit matching. Presence in LPSN alone does not imply valid
publication: the specification advises an explicit nomenclatural-code check.
LPSN supplies nomenclature, not a documented cell-dimension dataset.

## Representative cached records: observed behavior

The sample comprises 100 evenly spaced positions in the numerically sorted
cached candidate ID list. It is a deterministic engineering sample, not random,
taxonomically balanced, or a population estimate.

- **166372, Microvirga arsenatis:** length `1.5-3.1 µm`, width `0.8-1.1 µm`.
  Explicit units are inline; separate unit keys are absent.
- **158595, Vicingus serpentipes:** two observations with the same source reference,
  one rod-shaped and one coccus-shaped. They remain separate, even with the same
  reference; no width is transferred between them.
- **140537, Acinetobacter colistiniresistens:** different references report
  coccus-shaped and rod-shaped observations. Both are retained and flagged.
- **134153, Alteromonas hispanica:** one observation reports single-valued dimensions;
  another reports oval shape without dimensions.
- **133950, Pectinatus sottacetonis:** reported length is 16.5 µm. It is retained.
- **163760, Chryseotalea sanaruensis:** reported width is 0.1–0.2 µm, retained
  without imposing a minimum plausible cell size.

Across this sample there are 75 actual morphology observations and 44 strains
without a cell-morphology subsection. Twenty-nine observations have length,
26 have width; all observed dimension strings carry explicit inline µm units.
Dictionary/list variability and missingness are real, not hypothetical.
The normalized schema retains full morphology and taxonomy objects alongside
extracted fields and raw-response pointers.

## Coverage and technical discrepancies

The [BacDive portal](https://bacdive.de/) advertised 102,187 strains and 22,126
type strains when checked. The live SPARQL query returned **20,060** distinct type
IDs. Its documented Boolean type flag actually returned literal strings `"0"`
and `"1"`; a Boolean-true query returned zero rows. All three discovery responses
are preserved. The implemented query uses the observed `"1"` value.

The graph may be an older release; this is an inference, not confirmed source
metadata. REST sample strain DOIs include release component `20260601`.
`--all` means all candidates in the cached SPARQL index, **not guaranteed coverage
of the current portal**. The source does not promise an atomic snapshot across
all REST requests. Per-response times and record DOIs are therefore preserved.

All 100 selected records were retrieved and confirmed by BacDive as type strains;
52 have shape, 28 length, 26 width, and 25 both dimensions in one observation.
These rates must not be extrapolated to the full database or all cultured
prokaryotes. See [initial QC report](MILESTONE1_QC.md) and
[scientific review issues](SCIENTIFIC_REVIEW.md).

## Local GSS schema and validation results

The [official GSS format specification](https://lpsn.dsmz.de/text/lpsn-download-formats)
explains name components (`genus_name`, `sp_epithet`, `subsp_epithet`), the composite
`status`, publication `reference`/`authors`, taxon-page `address`, and `risk_grp`.
For species/subspecies, `nomenclatural_type` lists type-strain designations; for
genera it identifies the type species. `record_no` identifies the CSV taxon record,
and `record_lnk` points to the current correct name. `PENDING` indicates unavailable
information. The full CSV retains every field, including unused risk-group data.

Inspection of this supplied file found 34,515 records (4,622 genus, 28,967 species,
926 subspecies), unique record IDs, 44 repeated name groups, and no dangling
nonempty record links. There is no BacDive-ID column, no explicit domain/phylum,
and no direct per-record release timestamp. Thus the CSV cannot resolve the
higher-taxonomy conflicts or directly enumerate BacDive cross-links.

Implemented cross-database evidence uses exact whitespace-normalized original
BacDive names and culture-collection identifiers (case/whitespace normalized,
punctuation and leading zeros retained). Embedded LPSN names are independent
candidate evidence, never an automatic replacement. Genus type IDs are not used
as strain identifiers. All candidate records and their raw rows are retained.

Of 100 strains, 98 have a unique exact original-name match, explicit ICNP-valid
publication without detected adverse status, and a matching type deposit. This
includes four validly published synonyms whose current-name links are reported.
One original name is illegitimate (BacDive 14603, Staphylococcus ureilyticus), and
one is unmatched (157128, Neisseria abscessus). Both remain in all outputs.
Twenty strains have deposits associated with additional LPSN taxa, often synonyms
or related species/subspecies; those relationships are flagged, not collapsed.
No observation count or morphology value changes through LPSN enrichment.

## Completed full v2 census

The full run did not use the stale SPARQL candidate index. It enumerated the
96,656 IDs returned by the documented v2 culture-collection contains search and
supplemented them with IDs returned by v2 taxon searches for every one of the
4,614 local LPSN GSS genus names. The 4,664 supplemental IDs yield a 101,320-ID
union. Each record was fetched through v2 in batches of no more than 100 IDs;
the cache records 6,284 discovery responses and 1,014 detail responses. All
selected IDs were returned exactly once.

The source field `type strain` is exact `"yes"` for 22,122 records, `"no"` for
77,878, and missing/null for 1,320. Only the 22,122 exact-yes records are
processed as candidates. This is a reproducible operational population, rather
than a provider-issued atomic database snapshot. It can change if a later API
request sees a new release; original response bytes, request metadata, and hashes
remain available for comparison. See [full-census provenance](provenance/bacdive_census_2026-09-14.md).

The full run has 14,352 actual morphology observations plus 11,531 explicit
missing placeholders. It has 5,897 normalized length and 5,779 normalized width
records. LPSN exact-name evidence supports 21,201 name-and-type relationships;
217 status-review cases, 597 unmatched names, 24 ambiguous matches, 1,188
embedded-name disagreements, 4,961 deposits tied to other LPSN taxa, and 84
no-overlap deposits are retained for review. No taxonomy or dimension value is
replaced on this basis.

Morphology availability is highly uneven by original BacDive phylum labels
(chi-square 6,158.40, df 21, Cramer's V 0.528, p below floating-point reporting
precision). This describes database coverage and coexisting taxonomy versions,
not biological morphology. The full coverage table, tail-review records, CDF,
and outputs are summarized in [the full census report](FULL_CENSUS_REPORT.md).

## Scientific QC v1 source verification

Scientific QC v1 uses the raw response cache and normalized census as immutable
inputs. It constructs a separate review table rather than writing a correction
back to BacDive-derived fields. Two primary species descriptions were consulted
through accessible copies of their original descriptions: *Croceitalea marina* (DOI
10.1099/ijsem.0.002298) confirms 0.4–0.6 µm width, and *Nioella aestuarii* (DOI
10.1099/ijsem.0.002442) confirms 0.8–1.0 µm width. The differing cached nm/mm
units are retained as source values; the source-supported values appear only in
the correction overlay with high confidence.

The project made no automated unit substitutions. Its 1,288-record suspect table
marks all other triggered observations unresolved unless a source value was
actually checked. The current taxonomy harmonization uses the embedded LPSN
hierarchy already present in each raw BacDive record because the local GSS export
does not include phylum/class/order/family fields. It retains the local LPSN name
and status evidence and marks every fallback or discrepancy. See
[Scientific QC v1](SCIENTIFIC_QC_V1_REPORT.md) for criteria and limits.
