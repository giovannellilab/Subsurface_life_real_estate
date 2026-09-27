# M3 source reconnaissance provenance — 2026-09-26

## Scope and status

This is metadata-only targeted reconnaissance for M3. It created the tracked catalogue at `data/catalogues/m3_pore_geometry_source_catalogue.csv`; it did not acquire or cache a third-party artifact. No raw artifact path, byte size, or checksum exists yet. Before acquisition, create a per-source provenance record and preserve immutable source bytes under `data/raw/<source_id>/<acquisition_id>/`.

Reconnaissance date: 2026-09-26 UTC. Selection targeted representative lithological and method space, machine-readable quantitative artifacts, a persistent landing identifier, and explicit separation of pore bodies, throats, matrix pores, grain-boundary pores, microcracks, and unresolved geometry.

## Primary records checked

| Catalogue source | Persistent record | Confirmed for reconnaissance | Reuse note at reconnaissance |
| --- | --- | --- | --- |
| `pangaea_898001` | [PANGAEA 898001](https://doi.pangaea.de/10.1594/PANGAEA.898001) | Lipnice granite MIP throat distributions; tabular download | CC-BY 4.0; cite Staněk & Géraud (2019) and DOI. |
| `zenodo_1184144` | [Zenodo 1184144](https://zenodo.org/records/1184144) | Fontainebleau/Berea pore and throat CSVs | Verify record license and file metadata at acquisition. |
| `usgs_f7gx48rz` | [USGS F7GX48RZ](https://doi.org/10.5066/F7GX48RZ) | Mudstone MIP core-sample release | Retain USGS data-release citation and terms. |
| `bgs_estaillades_ct` | [BGS landing page](https://ckan.publishing.service.gov.uk/dataset/high-resolution-x-ray-micro-tomography-and-nano-tomography-datasets-of-estaillades-limestone) | Estaillades 3.9676-µm micro-CT and 32-nm nano-CT products | Confirm exact resource/version/terms at download. |
| `mendeley_n72yhbppkj` | [Mendeley n72yhbppkj](https://data.mendeley.com/datasets/n72yhbppkj/1) | Basalt distributions and connected-pathway CSVs | CC-BY 4.0; cite Phukan (2021) versioned DOI. |
| `yoda_serpentinite_nanoporosity` | [Utrecht YODA](https://public.yoda.uu.nl/geo/UU01/ZGEYQY.html) | TEM/FIB-SEM serpentinite nanoporosity data publication | Inspect files and license before acquisition. |
| `darus_2977` | [DaRUS 2977](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-2977) | Carrara marble micro-XRCT crack-network dataset | Inspect license and artificial-thermal protocol before acquisition. |

The other candidates remain labelled discovery/context records. Their `B` or `C` readiness prevents them being mistaken for verified compatible inputs.

## Future acquisition protocol

For each selected source, record creators, full citation, persistent ID, landing and exact download URL, version, UTC access time, terms, attribution, selected scope, checksum, and size. Preserve received bytes immutably; then record a separate processing run and exact source locator for every derived value. Do not bulk-download image volumes merely because metadata are public.
