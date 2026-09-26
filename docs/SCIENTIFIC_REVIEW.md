# Milestone 1: issues for scientific review

## Full census review status

The completed 2026-09-14 full v2 run has an operational population of 22,122
source-labelled type strains, drawn from a 101,320-ID union of the culture index
and all local-LPSN-genus searches. This replaces the historical 100-record sample
as the current analytical source. It is not a provider-certified atomic global
snapshot, and it must not be described as representing all prokaryotic diversity.
The full processing and analysis results are in [the census report](FULL_CENSUS_REPORT.md).

The first two issues below describe the historical sample and stale SPARQL route.
The current unresolved full-census questions are:

1. **Source coverage and taxonomy representation.** Morphology availability
   varies strongly across original BacDive phylum labels (Cramer's V 0.528), and
   old/new phylum labels coexist. This is a database-coverage signal. A taxonomy
   reconciliation policy requires scientific review before taxon-level inference.
2. **Nomenclature evidence needs scoped interpretation.** LPSN supports 21,201
   original name/type-deposit combinations, while unmatched, ambiguous, status,
   deposit, and embedded-name discrepancies remain in the documented QC tables.
   Neither a name match nor a deposit overlap establishes current culture
   availability or resolves synonymy automatically.
3. **Morphology classes and numerical tails need human review.** The pipeline
   preserves multiple observations, complex morphology, nanometre-labelled, and
   millimetre-labelled dimensions. Outlier flags identify records such as
   *Flavobacterium lutivivi*, *Nioella aestuarii*, and *Virgibacillus pantothenticus*;
   they are not corrections or biological exclusion criteria.
4. **No pore-accessibility result is yet justified.** The current outputs are
   source dimensions and coverage diagnostics. Selecting a dimension convention,
   handling complex morphology, and connecting cells to pore-throat or fracture
   geometry remain future scientific decisions.
5. **Scientific QC v1 confirms two unit overlays but leaves 1,286 suspects
   unresolved.** *Croceitalea marina* and *Nioella aestuarii* have
   high-confidence source-verified µm corrections. The raw values remain intact.
   Unit/scale anomalies including *Flavobacterium lutivivi* and
   *Virgibacillus pantothenticus* need further primary-source review before any
   analytical replacement. See [Scientific QC v1](SCIENTIFIC_QC_V1_REPORT.md).
6. **Species weighting is stable at the median under the stated rules, but
   source selection remains imperfect.** A 4,557-species canonical-width table
   preserves a 0.55 µm minimum-width median. The likely-primary-description
   category is inferred from citation titles and needs validation before it can
   be treated as a formal protologue registry.

## Historical engineering-sample issues

1. **Offline nomenclatural validation is operational; two cases need review.**
   The full local LPSN CSV corroborates original names and type deposits for 98/100
   candidates. BacDive **14603**, *Staphylococcus ureilyticus*, exactly matches an
   ICNP-valid but illegitimate LPSN name. Its embedded BacDive LPSN name is
   *Staphylococcus cohnii subsp. ureilyticus*; no automatic substitution is made.
   BacDive **157128**, *Neisseria abscessus*, has no exact name or deposit match in
   the export (CCUG 69613, CECT 9178). Absence does not establish invalid publication.
   Both records remain for review. Credential/API access is not a blocker.
2. **Population coverage is incomplete.** The cached graph lists 20,060 candidate
   IDs versus 22,126 advertised type strains. Establish a current authoritative
   enumeration before claiming database completeness. Only the 100-record initial
   sample was downloaded; `--all` is implemented for the cached index.
3. **Taxonomic conflicts require a policy.** BacDive and its embedded LPSN object
   often differ, including old/new phylum labels. Conflicting normalized fields
   are null; both original values remain in `taxonomy_raw`. No synonym or
   classification reconciliation is assumed. The GSS CSV has no domain/phylum
   fields. Four supported original names are valid synonyms with linked current
   names: *Marmoricola bigeumensis* → *Nocardioides marmoribigeumensis*,
   *Undibacterium parvum* → *Neoundibacterium parvum*,
   *Streptomyces cinereoruber subsp. fructofermentans* → *Streptomyces fructofermentans*,
   and *Chryseoglobus indicus* → *Microcella indica*. These links are reported as
   LPSN's opinion, not applied as renaming. Twenty strains match deposits shared
   by additional LPSN names; review these before any taxon-level deduplication.
4. **Multiple shapes and morphology context need interpretation.** Different
   observations may represent conditions, developmental states, or different
   reports. Retain all observations. Flags for filaments, spores, appendages,
   aggregates, and other complex contexts are conservative cues, not conclusions
   that the reported dimensions describe those structures. Numeric conversion
   does not certify suitability for a simple cell-geometry model.
5. **Dimensions remain source-defined.** A length reported for a coccus is still
   length; it is not copied into width or interpreted as a representative diameter.
   Unknown units, inequalities, composite descriptions, and malformed values stay
   unnormalized. Missing values are never imputed.
6. **Outlier criteria are provisional.** Bounds below 0.05 or above 100 µm trigger
   review and remain in outputs. These thresholds are engineering screening
   choices, not biological limits; review before using them scientifically.
7. **Sampling and independence.** ID-spaced sampling is for exercising the
   pipeline. Morphology coverage is sparse; multiple reports and multiple strains
   of one species cannot automatically be treated as independent observations.
   Exact duplicate relationships are reported; fuzzy deposit matching and synonym
   collapse are deliberately unresolved.
8. **Dataset redistribution/commercial terms.** BacDive is CC BY 4.0 with an
   additional request to contact it for commercial use; LPSN is CC BY-SA 4.0.
   Determine attribution, taxon links, and share-alike handling for combined data
   before public distribution or commercial reuse. No data publication occurred.

9. **Validation scope and metadata limits.** An exact name plus one matching
   deposit corroborates the database relationship, not present-day culture
   viability, purity, or every listed deposit. The operational name criterion is
   explicit ICNP publication with no detected adverse status; it does not infer
   an explicit legitimacy field absent from GSS. Download date is recorded from
   the supplied filename/user report; exact download time and release ID were
   not provided. Processing hashes pin the actual source bytes.
