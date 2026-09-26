# BacDive full morphology census: source record

- Provider: Leibniz Institute DSMZ, BacDive / DSMZ Digital Diversity.
- Citation: Schober et al., *BacDive in 2025: the core database for prokaryotic
  strain data*, *Nucleic Acids Research* (2025). Current citation and terms:
  <https://bacdive.dsmz.de/about>.
- Interface: public BacDive REST v2, <https://api.bacdive.dsmz.de/v2/>.
- Acquisition date: 2026-09-14. Individual request URLs, UTC retrieval times,
  response byte counts, content types, and SHA-256 checksums are immutable
  `metadata.json` companions to every cached `response.json` file.
- Local raw root: `data/raw/bacdive/census_2026-09-14/`. Original response bytes
  are never rewritten. This local cache contains 6,284 discovery responses and
  1,014 detail responses; `data/interim/census_2026-09-14/acquisition.json`
  records their request keys and verifies their checksums before processing.
- Selection: 96,656 IDs from the v2 `culturecollectionno/%25?search_type=contains`
  index, supplemented by v2 `taxon/<genus>` queries for all 4,614 genus names in
  the immutable local LPSN GSS snapshot. The union has 101,320 returned records.
  Of those, 22,122 have exact source field `type strain: "yes"` and form the
  processing population. The all-record statuses are 77,878 `"no"`, 22,122
  `"yes"`, and 1,320 absent/null.
- Scope caveat: this is the project's operational full v2 census for this
  retrieval date. It is a union of documented searches, not a provider-declared
  atomic global snapshot or a claim of complete representation of all prokaryotes.
  Every API response is timestamped because the API does not promise an atomic
  snapshot across the multi-request retrieval.
- Terms: BacDive declares CC BY 4.0 and asks commercial users to contact its
  maintainers. Preserve attribution and source references; obtain any needed
  commercial clarification before redistribution. No images or literature PDFs
  were downloaded. See [third-party data](../../THIRD_PARTY_DATA.md).
- Reproduce or verify cache integrity: run `python3 scripts/acquire_census.py`.
  It only reuses checksum-verified immutable cache entries at these default paths.
  Use new raw and manifest paths for a later snapshot.
