# Third-party data

Milestone 1 acquired public BacDive API responses on 2026-09-14, including the
completed full v2 operational census, and used the supplied full LPSN GSS
download for offline validation. Raw and processed datasets remain local and Git-ignored.
The Apache 2.0 license covers software, not third-party data.

| Source | Reuse terms | Attribution and restrictions | Provenance |
| --- | --- | --- | --- |
| BacDive, REST v2 and DSMZ SPARQL | [CC BY 4.0; official terms](https://bacdive.dsmz.de/about) | Cite Schober et al., *BacDive in 2025: the core database for prokaryotic strain data*, retain original references and record DOIs. The site asks commercial users to contact maintainers. Images have separate rights and were not downloaded. | [Full-census record](docs/provenance/bacdive_census_2026-09-14.md); [historical sample](docs/provenance/bacdive.md) |
| LPSN GSS CSV and taxonomy embedded in BacDive | [CC BY-SA 4.0; official terms](https://lpsn.dsmz.de/text/copyright) | Preserve embedded attribution. Current requested publication citation: Freese et al. (2026), [doi:10.1093/nar/gkaf1110](https://doi.org/10.1093/nar/gkaf1110), accessed 2026-09-14. Electronic redistribution requires taxon-page links; license-compliant commercial use is allowed. Automated acquisition only through official API/downloads or permission. | [CSV provenance](docs/provenance/lpsn.md); embedded references in raw BacDive records; [assessment](docs/SOURCE_ASSESSMENT.md) |

## M3 geological sources

M3 retains raw geological artifacts locally only; it does not redistribute them.
The first controlled pass acquired two CC-BY 4.0 tabular records: PANGAEA
898001 (Lipnice granite MIP) and Zenodo 1184144 v1 (Fontainebleau/Berea PNM).
File checksums, attribution, local-only paths, and transformations are in the
[first-ingestion provenance record](docs/provenance/m3_first_ingestion_2026-09-26.md).
The candidate list and remaining acquisition-readiness labels are in the
[pore-geometry resource](docs/PORE_GEOMETRY_RESOURCE.md) and its reconnaissance
[provenance record](docs/provenance/m3_source_reconnaissance_2026-09-26.md).
Before another M3 download, record file-level terms, version, attribution,
checksum, and redistribution constraints. Public landing pages or metadata do
not alone grant permission to republish raw data.

The embedded LPSN references may cite an older publication; they remain unchanged
in the raw data. Cite the current requested LPSN reference in future publications
as well. The independently downloaded GSS CSV is now used for offline validation.
No API requests or credential handling are part of this pipeline. Raw CSV rows
and original taxon-page addresses are retained in matched candidate evidence.

Before distributing combined outputs, determine applicable share-alike terms,
source-specific attribution, and taxon links, and resolve BacDive's commercial
contact request if relevant. No combined-data license has been assigned and no
datasets have been published. The local cache is not a redistribution permission.
