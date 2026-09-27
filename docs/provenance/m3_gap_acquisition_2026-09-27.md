# M3 targeted lithology-gap acquisition

Acquisition date: 2026-09-27. This is a bounded acquisition and ingestion
record. Original third-party bytes are immutable, local, and
gitignored beneath `data/raw/m3_acquisitions/`. No raw source artifact is
redistributed by this repository.

## Acquired artifacts

| Source / persistent identifier | Local raw artifact | Bytes | SHA-256 | License | Direct retrieval location |
| --- | --- | ---: | --- | --- | --- |
| Harvard Dataverse, [10.7910/DVN/WBSHKX](https://doi.org/10.7910/DVN/WBSHKX) | `harvard_wbshkx/J24_R-S.tab` | 6,250,450 | `9b81ffcbc4c706a7b3c931181b27168bc76cd845ded2244c74b1670623549948` | CC0-1.0 | `https://dataverse.harvard.edu/api/access/datafile/5224074` |
| Harvard Dataverse, [10.7910/DVN/WBSHKX](https://doi.org/10.7910/DVN/WBSHKX) | `harvard_wbshkx/J24_R-n.tab` | 232,493 | `754254e1ff4740d9b2e4fd306cb640d7319631e9a17be3a2764f70d836edc659` | CC0-1.0 | `https://dataverse.harvard.edu/api/access/datafile/5224076` |
| Harvard Dataverse, [10.7910/DVN/WBSHKX](https://doi.org/10.7910/DVN/WBSHKX) | `harvard_wbshkx/W23_R-n.tab` | 105,512 | `41bdb1b0a47a028b0afa4c7396f12771f5e045e178f70ee4dd625a0bb5a92aa0` | CC0-1.0 | `https://dataverse.harvard.edu/api/access/datafile/5224077` |
| Harvard Dataverse, [10.7910/DVN/WBSHKX](https://doi.org/10.7910/DVN/WBSHKX) | `harvard_wbshkx/W23_R-S.xlsx` | 8,502 | `7fd5ce11272c7edcd8b706a8fa4a1e8432e0293b4cf42b1383518574e35fa323` | CC0-1.0 | `https://dataverse.harvard.edu/api/access/datafile/5224075` |
| Harvard Dataverse, [10.7910/DVN/WBSHKX](https://doi.org/10.7910/DVN/WBSHKX) | `harvard_wbshkx/PLS.docx` | 15,146 | `ed4e91bdc8a2f3763b64d8efd478650cab00cf5484f27de80f489ed90e4a4725` | CC0-1.0 | `https://dataverse.harvard.edu/api/access/datafile/5224078` |
| Harvard Dataverse companion, [10.7910/DVN/D1LDSO](https://doi.org/10.7910/DVN/D1LDSO) | `harvard_d1ldso/J24_analysis.xlsx` | 290,006 | `c93549e7aa8c8536af80d5c50ddab19d583afe40dcc2f55de4c4e62984059940` | CC0-1.0 | Harvard Dataverse public file API |
| Harvard Dataverse companion, [10.7910/DVN/D1LDSO](https://doi.org/10.7910/DVN/D1LDSO) | `harvard_d1ldso/W23_analysis.xlsx` | 133,437 | `69daf12484f9daa725dfdf60590ac5095e42b402f1e4a35beea47f9e81b0963a` | CC0-1.0 | Harvard Dataverse public file API |
| Harvard Dataverse companion, [10.7910/DVN/D1LDSO](https://doi.org/10.7910/DVN/D1LDSO) | `harvard_d1ldso/intermediate_psd.docx` | 78,235 | `454c9393cf555d50ff1c8e20b85e65342cee0486548c015f6e93a574ea4b93b7` | CC0-1.0 | Harvard Dataverse public file API |
| Figshare F42A, [10.6084/m9.figshare.1189259.v1](https://doi.org/10.6084/m9.figshare.1189259.v1) | `figshare_f42a/F42A.7z` | 4,653,852 | `9e69710a72c1186556fb9fde0426d224296ad2b2c03e9ef3995c2a82478cb0dd` | CC-BY-4.0 | `https://ndownloader.figshare.com/files/3229787` |
| PANGAEA Atlantis Massif, [10.1594/PANGAEA.873535](https://doi.pangaea.de/10.1594/PANGAEA.873535) | `pangaea_873535/PANGAEA_873535.zip` | 6,249 | `96871d7f81ea9581597641fe893dd02f34a47c855d1ebd75c1def6ffac1ebc72` | CC-BY-3.0 | `https://doi.pangaea.de/10.1594/PANGAEA.873535?format=zip` |

### Harvard marine shale digital-core data

The exact dataset title is *The utilized data in article Assessment of
multi-scale pore structures and pore connectivity of marine shales based on
fractal dimensions and connectivity probability of digital cores*. It supplies
J24 and W23 source tables labelled `PORE-SIZE`, `NUMBERS`, `RADIUS^2`,
`FRACTION`, and `ACC-FRACTION` (and corresponding source-native raw tables).
The supplied plain-language document describes pore-size distributions,
correlation length, and connectivity probability. It does **not** label these
values as pore bodies or pore throats, and the retained tables do not themselves
establish a physical unit or radius/diameter convention. The linked CC0
companion record supplies a modelled curve: W23 explicitly labels `R/nm` and
`V/nm3`, whereas J24 does not label the `R` unit. Ingestion retains all classes
and uses only W23's clearly labelled modelled matrix-pore-cluster radius curve
in the physical native-size display. Neither table is guessed to be a
constriction measure. Sample state is `as supplied`; the source calls them
marine shale. `L(R/rmax)` is retained as a source model parameter, not inferred
as a graph connectivity metric or physical correlation length.

### F42A quartz sand pack extracted network

The Figshare record is a compact archive named `F42A.7z`, supplied under
CC-BY-4.0. It is the public mirror selected after the original Imperial College
network/results attachment returned HTTP 403. The associated source describes a
laboratory-packed Ottawa F42 quartz sand, imaged by micro-CT (9.996 µm voxel
edge; 300 cubed voxels) and processed by pore-network extraction. It therefore
has separate pore-body and throat semantics in principle, rather than a
universal size column. The archive is retained unchanged. Only its compact
`F42A_NetworkAndResults.zip` member was extracted to ignored
`data/interim/m3_f42a/`; the raw image was not extracted. Ingestion retains
1,246 pore nodes, 2,856 throat edges, source radii, topology, coordination,
volumes, shape factors, and reported porosity/permeability/formation-factor
metrics. It is a laboratory-packed unconsolidated sand reference, not a natural
cemented sandstone.

### Atlantis Massif serpentinised ultramafic and gabbro tables

The PANGAEA bundle contains source tables for sample description/density/bulk
porosity and for pressure-dependent physical properties. It covers natural
drilled cores of serpentinised harzburgite, serpentinised dunite, gabbro, and
olivine gabbro from the Atlantis Massif. The latter table retains confining and
pore pressure, P- and S-wave velocities, resistivity, and permeability. Thus it
provides a quantitative connected-flow-relevant record plus bulk porosity; it
does **not** provide a pore-size distribution, pore/throat object table,
radius/diameter definition, voxel size, or segmentation window. Do not use it
as a size distribution or as proof of a specific connectivity topology.

## Routes inspected but not acquired

| Target | Public route and outcome | Consequence |
| --- | --- | --- |
| Chogani & Plümper natural serpentinite nanoporosity, YODA `UU01/ZGEYQY` | The DOI/article and EPOS metadata identify FIB-SEM/TEM natural serpentinite pore observations, but the YODA page and its API returned an Anubis proof-of-work gate on 2026-09-27. The browser surface was unavailable for a final interactive attempt. | No raw source bytes, no figure digitisation, and no inferred pore table. Retain as a blocked high-value source. |
| Utrecht/EPOS gabbro–serpentinite–greenschist BSE record, [10.24416/UU01-GHPUMU](https://doi.org/10.24416/UU01-GHPUMU) | EPOS confirms CC-BY-4.0 and BSE maps at 50 nm (HR), 200 nm (LR), and 800 nm for greenschist, but its file view contains no files and the linked YODA source is proof-of-work gated. | No bytes acquired. The record is microscopy input/model-metrics data, not a precomputed pore-geometry table; later work requires segmentation and geometry eligibility review. |
| USGS West Trenton MIP, [10.5066/F7GX48RZ](https://doi.org/10.5066/F7GX48RZ) | The existing ScienceBase route remained inaccessible behind the frontend protection in the earlier M3 pass. The CC0 Harvard shale source above already provides the requested mudstone/shale quantitative acquisition without extending the search. | Retained in the catalogue for a future source-specific retry; not needed for this bounded pass. |

No multi-gigabyte image volume, credential, or restricted source was downloaded.
The compact F42A archive includes a 91 MB raw image member, which was retained
inside the immutable archive and not extracted. The later source-preserving ingestion generated only ignored local
tables and first-order native-size descriptive outputs; no raw third-party data
are published or coupled into a new constriction `C(k)` calculation.
