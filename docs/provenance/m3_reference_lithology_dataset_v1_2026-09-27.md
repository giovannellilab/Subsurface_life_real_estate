# Reference Lithology Dataset v1 acquisition record

Date: 2026-09-27. This record covers the representative expansion from the
two-source M3 first ingestion. Raw artifacts remain immutable and gitignored
under `data/raw/m3_acquisitions/`; this tracked document records identifiers,
license, checksum, and the narrow extraction decision rather than distributing
third-party data.

| Source | Artifact retained locally | SHA-256 | License | Use in v1 |
| --- | --- | --- | --- | --- |
| South China Sea carbonate PNM, [10.17632/t8rj6b6gwn.1](https://doi.org/10.17632/t8rj6b6gwn.1) | `mendeley_t8rj6b6gwn/carbonate_pnm_statistics.rar` | `79dd11cebba4b40c84cf8f101351e8fa46efbf02f6b4ddc1327ffd25d8860a03` | CC-BY-4.0 | Five carbonate REV sheets: source pore/throat radii, volumes, and throat lengths. Workbook omits voxel size, retained as missing. |
| Unreacted basalt PNM, [10.17632/n72yhbppkj.1](https://doi.org/10.17632/n72yhbppkj.1) | `mendeley_n72yhbppkj/Pore_ungrooved_Unreacted_PoresizeDist.csv` | `1fff1f7d21370dc017df935bbaf7988bc714261d0463c30f3c1f22bc30c9cbc8` | CC-BY-4.0 | Only the unreacted, ungrooved pore-body EqDiameter table. The associated article supplies the mm convention and 14.99 µm CT window; reacted/pathway files were not used as reference distributions. |
| UKGEOS Wilmslow Sandstone PNM, [10.17637/rh.12707840](https://doi.org/10.17637/rh.12707840) | `figshare_ukgeos_12707840/UKGEOS_PNM_Paper.zip` | `be326d5936b6a329241b87dcc9d9fc9591f4fa2c6f73ac4744f475675a5cdf00` | CC-BY-4.0 | Seven Sellafield/Wilmslow sandstone samples: all pore/throat EqRadius objects, plus total/effective porosity and permeability. Archive readme states the all-object tables include connected and disconnected objects; voxel size and permeability unit are not present there. |

Existing Lipnice and Fontainebleau/Berea artifacts retain their earlier
checksums and processing record in
[m3_first_ingestion_2026-09-26.md](m3_first_ingestion_2026-09-26.md) and the
local processing manifest. `scripts/ingest_reference_lithology_dataset_v1.py`
reads these artifacts without modifying them and writes local-only dataset
tables. Native-value plots remain source-native. The biological-comparison
table adds a separate analytical comparison diameter only where semantics allow:
`2 × radius`, retained source diameter, or retained MIP entry/throat-equivalent
dimension. It does not alter native values, infer unresolved dimensions, or
infer unobserved connectivity.
