# BacDive: Milestone 1 source record

- Provider: Leibniz Institute DSMZ, BacDive / DSMZ Digital Diversity.
- Citation: Schober et al., *BacDive in 2025: the core database for prokaryotic
  strain data*, Nucleic Acids Research, database issue 2025. Current citation
  instructions: https://bacdive.dsmz.de/about.
- Interfaces: https://api.bacdive.dsmz.de/v2/ and
  https://sparql.dsmz.de/api/bacdive.
- Acquisition date: 2026-09-14; exact UTC times/URLs/query parameters/byte counts/
  hashes are in [bacdive_milestone1.json](bacdive_milestone1.json).
- Local snapshot: `data/raw/bacdive/milestone1/`, JSON response + JSON metadata
  per request directory. The local original filenames are `response.json` and
  `metadata.json`; the server did not supply an original download filename.
- Selection: 100 evenly spaced positions in the numeric ordering of 20,060
  type-strain candidates from the graph. The exact IDs and response keys are
  preserved in `data/interim/milestone1/acquisition.json` and the inventory.
- Version: REST v2; response record DOIs include per-record release/version
  information. Graph release was not supplied. No atomic database snapshot is
  claimed. Refer to record DOIs, timestamps, and checksums.
- Scope: structured cell morphology and strain/taxonomy metadata; complete
  returned records are cached to preserve context. No images, PDFs, or external
  primary-literature content were fetched by the acquisition pipeline.
- Terms: [BacDive](https://bacdive.dsmz.de/about),
  [embedded LPSN data](https://lpsn.dsmz.de/text/copyright), and
  [third-party register](../../THIRD_PARTY_DATA.md). No special commercial
  permission was requested or assumed.
- Limitations: the graph's string type flag differs from documented Boolean
  representation; candidate coverage is lower than the portal total; taxonomy
  can disagree with embedded LPSN. Independent offline validation is now supplied
  by the [LPSN GSS snapshot](lpsn.md); original BacDive responses remain unchanged.
- Reproduce: `python3 scripts/acquire_bacdive.py --sample-size 100`, then
  `python3 scripts/process_bacdive.py`. Existing response directories are reused;
  a fresh download requires a different snapshot path.
