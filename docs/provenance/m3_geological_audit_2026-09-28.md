# M3 geological-resource audit provenance — 2026-09-28

This record documents the source material inspected for the scientific audit.
It does not authorize redistribution of third-party files. Local source-paper
copies and the Park & Santamarina supplement are immutable, gitignored audit
inputs under `data/raw/m3_audit/`; all derived row tables remain gitignored.

## Locally retained audit inputs

| Source | Local artifact | Bytes | SHA-256 | Access / role |
| --- | --- | ---: | --- | --- |
| Staněk & Géraud (2019), [doi:10.5194/se-10-251-2019](https://doi.org/10.5194/se-10-251-2019) | `source_papers/stanek_geraud_2019_lipnice.pdf` | 12,492,853 | `59a980214b745354380620b56f7cecabbcefd5f4e023759f6eed64349afd7542` | open CC-BY paper; specimen state, MIP semantics, site coordinates, porosity interpretation |
| Liu, Ma & Zhu (2022), [doi:10.3390/app12052611](https://doi.org/10.3390/app12052611) | `source_papers/liu_ma_zhu_2022_carbonate.pdf` | 19,742,835 | `1da4ffc4454e1e34ee8582e504119a5c6202c81dd3304aee26e5b854d7198189` | open CC-BY paper; voxel sizes, porosity, network counts and summary statistics |
| Park & Santamarina (2020), [doi:10.1038/s41598-020-78714-3](https://doi.org/10.1038/s41598-020-78714-3) | `park_santamarina_2020/41598_2020_78714_MOESM1_ESM.pdf` | 3,028,852 | `638c29fada973653315c681d3fb6b689ef977ca1fe4b5a6c12fc27873e6e3e07` | supplementary benchmark; Table S2 and pore-diameter distributions |

## Other source papers and metadata inspected

- Thomson et al. (2018), *A Case Study for Pore Network Modeling of a
  Sandstone Core*, [doi:10.3389/feart.2018.00058](https://doi.org/10.3389/feart.2018.00058),
  together with Zenodo 1184144: voxel size, ROI/segmentation, dry/saturated
  cases, total/connected/isolated porosity, and network definitions.
- Menefee et al. (2022), *Changes in Pore Geometry and Connectivity in the
  Basalt Pore Network Adjacent to Fractures in Response to CO2-Saturated
  Fluid*, [doi:10.1029/2021WR030275](https://doi.org/10.1029/2021WR030275),
  together with Mendeley `n72yhbppkj`: quarry provenance, 14.99 µm voxel,
  core preparation, unreacted/ungrooved state, and source porosity context.
- Payton et al. (2021), *Pore-scale assessment of subsurface carbon storage
  potential*, [doi:10.1144/petgeo2020-092](https://doi.org/10.1144/petgeo2020-092),
  via the NERC repository and Figshare 12707840: sample depths, 2.6860–2.8409
  µm voxels, connected/all-network distinction, porosity and mD units.
- Fan et al. (2022), *Assessment of multi-scale pore structures and pore
  connectivity domains of marine shales by fractal dimensions and correlation
  lengths*, [doi:10.1016/j.fuel.2022.125463](https://doi.org/10.1016/j.fuel.2022.125463),
  using publisher metadata plus the CC0 Harvard WBSHKX/D1LDSO deposited tables
  and documentation: CTSTA class meaning, cluster-domain model, `R/nm`, model
  volume, and microfracture-mediated connectivity. The full publisher paper was
  not retained locally; site/formation metadata not established by the deposit
  remain unresolved rather than inferred.
- Dong & Blunt (2009), *Pore-network extraction from micro-computerized-
  tomography images*, [doi:10.1103/PhysRevE.80.036307](https://doi.org/10.1103/PhysRevE.80.036307),
  Imperial/figshare F42A metadata, and the acquired archive: 9.996 µm voxel,
  300³ image, 1,246 pores, 2,856 throats, laboratory-pack status, porosity,
  permeability, formation factor, and extraction semantics.
- Falcon-Suarez et al. (2017), *Elastic and electrical properties and
  permeability of serpentinites from Atlantis Massif*,
  [doi:10.1093/gji/ggx341](https://doi.org/10.1093/gji/ggx341), and the complete
  PANGAEA 873533–873535 metadata: five event coordinates, lithology, depth,
  bulk porosity, pressure conditions, and transport measurements.

The audit script records source-paper corrections as an overlay. It does not
rewrite raw artifacts or fill source discrepancies. In particular, the South
China Sea carbonate-A workbook/paper throat discrepancy and the Atlantis
velocity unit/magnitude inconsistency remain explicit flags.
