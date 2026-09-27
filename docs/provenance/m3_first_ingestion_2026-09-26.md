# M3 first-ingestion provenance — 2026-09-26

## Scope

This first review ingests only two of the existing source-census records, selected
because they provide compact, public, machine-readable numeric artifacts. Raw
files are immutable local inputs under `data/raw/m3_acquisitions/` and are
gitignored. The tracked outputs are derived tables, file-level checksums, and
figures; no raw third-party rows or images are published.

| Source | Artifact acquired | Terms | Raw SHA-256 | Parsing outcome |
| --- | --- | --- | --- | --- |
| M3-001 / PANGAEA.898001 | `pangaea_898001.tab`, 51,508 bytes | CC-BY-4.0 | `62df7beee806f5c3c5566cdf817c327f7a60b2f8b9c87232d6692cc6cad633d6` | 21 Lipnice specimen intrusion distributions; 1,365 non-empty bins retained. |
| M3-002 / Zenodo.1184144 v1 | Six case-specific pore/throat CSVs | CC-BY-4.0 | File-level hashes in `processing_manifest.json` | Fontainebleau case and two Berea cases; 46,467 body and 173,174 throat objects retained. |

Acquisition URLs and byte sizes are in
`data/processed/m3_first_ingestion/processing_manifest.json`. The PANGAEA
source was downloaded from its DOI text-file representation. Zenodo files were
downloaded from the record v1 API content endpoints. The local input directory
is ignored by Git, and the script never writes to it.

## Transformations

`scripts/ingest_m3_first.py` parses only these two source formats. It copies
source values to long-form derived CSVs, records the original field name/file,
and copies micrometre values to normalized micrometre columns where the source
already used µm. It does not calculate diameters from `EqRadius`, fit models,
or merge distributions.

For Lipnice, the script retains only columns explicitly labelled `Poros increm
intrus`; reintrusion columns are deliberately excluded. The PANGAEA bin label
is retained as the MIP entry/throat-equivalent window and the value as
incremental intruded porosity (%). For the sandstone record, each CSV row is
an object record. `EqRadius`, area, volume, channel length, and coordination
are retained only in their appropriate body or throat rows.

## QC and limitations

All retained numeric sizes are positive; each MIP bin has positive ordered
bounds; sample and measurement keys are unique; and every object is linked to
a known measurement. The Zenodo files contain non-UTF-8 micro-symbol bytes in
some headers. The parser records this as a QC flag while interpreting the
otherwise explicit source header as µm; the raw byte files remain authoritative.

The imported source CSVs do not supply the CT voxel size or network-extraction
settings. Those fields remain explicitly `not supplied in CSV`, so the sandstone
network values must not be treated as resolution-complete or pooled with MIP.

## Deferred records

West Trenton was not acquired because the sciencebase catalogue endpoint
returned access denial in this environment. Estaillades currently exposes
image-resource links rather than a small numeric distribution artifact.
Basalt Mendeley metadata confirmed CC-BY-4.0 but the public API endpoint did
not return file inventory here. Serpentinite YODA returned 403. Carrara’s
smallest public segmentation is 292 MB, and its metadata warns that the
segmentation overestimates crack volume; it is deferred pending a scientifically
controlled subvolume/threshold review. These are acquisition limitations, not
negative findings about the datasets.
