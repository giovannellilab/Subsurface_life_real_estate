# LPSN GSS snapshot, 2026-09-14

The user downloaded the full LPSN GSS CSV after registration and supplied the
unmodified file locally. The pipeline opens it read-only. No credentials were
requested, inspected, or stored, and no authenticated requests are needed.

- Original filename: `lpsn_gss_2026-09-14.csv`
- Location: `data/raw/lpsn/lpsn_gss_2026-09-14.csv`
- Size: **15,652,936 bytes**
- SHA-256: `f57a015a7d52e6db2d1a3a38130db3be7e82c89f04b3bf4f67a36fe4dd5872eb`
- Download date: **2026-09-14**, based on the filename and the user's report in
  this session. Exact download time, request URL, and server release ID were not
  supplied; filesystem modification time is not used as a download timestamp.
- Source: [official LPSN downloads](https://lpsn.dsmz.de/downloads).
- Terms: [CC BY-SA 4.0 and LPSN-specific attribution/access terms](https://lpsn.dsmz.de/text/copyright), checked 2026-09-14.
- Citation: Freese HM, Meier-Kolthoff JP, Sardà Carbasse J, Afolayan AO, Göker M
  (2026). TYGS and LPSN in 2025: a Global Core Biodata Resource for genome-based
  classification and nomenclature of prokaryotes within DSMZ Digital Diversity.
  Nucleic Acids Research 54:D884–D891.
  [doi:10.1093/nar/gkaf1110](https://doi.org/10.1093/nar/gkaf1110).

The [machine-readable provenance](lpsn_gss_2026-09-14.json) pins the filename,
size, and checksum. Processing refuses a mismatch. It does not rewrite the
source file or re-register a changed checksum automatically. Register future
exports under distinct filenames/provenance files and select them explicitly.

The export has **34,515 records**: 4,622 genera, 28,967 species, and 926 subspecies.
These counts include synonyms and spelling/status variants; they are not counts
of distinct accepted species. All record IDs are unique. There are 44 repeated
name groups and no unresolved nonempty `record_lnk` targets. All rows remain in
the original CSV; genus records are indexed for links, not treated as strains.

Derived `lpsn_validation.csv` has one row per BacDive ID. Candidate evidence in
`lpsn_candidates.jsonl` includes original CSV rows and their ordinal (1-based CSV
data-record position, excluding the header, not a physical line number).
`lpsn_registry_qc.json` describes the full local export. Processing manifests
include both source and provenance-file hashes. Morphology source references
continue to point to BacDive; LPSN validation has separate provenance fields.

For academic publication retain attribution, the requested citation, and access
date. Electronic redistribution must preserve taxon-page links. Commercial use
is permitted in compliance with CC BY-SA; adaptation/share-alike obligations
must be addressed before releasing combined datasets. API access is an optional
future update route, not a dependency of this workflow.
