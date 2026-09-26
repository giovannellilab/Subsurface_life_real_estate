# Scientific framework

## Purpose and scope

This project asks how microbial cell geometry interacts with the physical
geometry of subsurface habitats. It distinguishes **habitable space**,
**geometrically accessible space**, and **connected space**. Total porosity is
not sufficient: void volume can be too small or poorly connected for cells,
while low-porosity crystalline rock can host organisms in connected fractures,
fracture fluids, and on fracture surfaces.

This is a working framework. Facts and current empirical results are identified
below; working relationships and later analyses are not validated models.

## Information hierarchy

1. The Google Doc and scientific discussions are a working scientific notebook
   and brainstorming space; they are not a public source and are not linked here.
2. This file is the canonical, version-controlled scientific synthesis for the
   project.
3. `site/` is the tracked source for the public Living Research Report.
4. `gh-pages` is the generated and deployed public output, built from `site/`
   with the allowlisted report builder.

## Conceptual starting point

Park and Santamarina (2020), *The critical role of pore size on depth-dependent
microbial cell counts in sediments*, **Scientific Reports** 10, 21692,
[doi:10.1038/s41598-020-78714-3](https://doi.org/10.1038/s41598-020-78714-3),
provide the conceptual starting point. Their sediment-compaction framework
relates pore-size evolution, a nominal microbial size, and the probability of
pores exceeding microbial dimensions to life-compatible pore volume.

The project extends, rather than rejects, that idea. It will use empirical
microbial distributions; distinguish pore bodies from pore throats; treat
fractures separately; and preserve morphology, orientation, and connectivity.
Sediment porosity alone cannot represent crystalline-rock habitats.

## Data-first principle

The model should emerge from independently characterized microbial and
geological geometry, with their biases and uncertainty quantified before their
distributions are coupled. It should not begin by choosing a universal cell
diameter or pore-size threshold.

## Current empirical cultured baseline

The current cultured baseline represents approximately
`P(cell geometry | cultured, formally described prokaryote, morphology recorded)`.
It is not a universal microbial-size distribution. Cultivability, taxonomic
history, differential reporting, laboratory conditions, phenotypic plasticity,
and weak coverage of ultrasmall, difficult-to-cultivate, environmental, and
subsurface lineages limit extrapolation.

Scientific QC v1 is the primary cultured baseline: 4,452 species with strict
LPSN name-and-type support and non-averaged canonical width data.

| Canonical width metric | N | Median (µm) | 5th–95th percentile (µm) | ≤0.5 µm | ≤1 µm |
| --- | ---: | ---: | --- | ---: | ---: |
| Minimum | 4,452 | 0.55 | 0.25–1.168 | 48.88% | 93.31% |
| Midpoint | 4,452 | 0.60 | 0.30–1.25 | 36.81% | 90.61% |
| Maximum | 4,452 | 0.70 | 0.35–1.40 | 31.58% | 87.15% |

Within this source-conditioned cultured-species dataset, 1 µm lies toward the
upper part of reported width distributions. This is stable to species weighting,
the current high-confidence corrections, and the three reported width
conventions. It does not imply that a 1 µm pore throat is traversable by those
fractions of microorganisms: clearance, orientation, deformability, surfaces,
biofilms, pore geometry, and connectivity remain separate constraints.

Observation-level results remain a secondary layer: 5,849 normalized-width
observations from 5,779 strains, with 4,647 observations from 4,624 strains
analysis-eligible and 1,202 explicit exclusions. There are 4,557 species with a
non-averaged canonical width, including the 4,452 strict LPSN-supported species.
Scientific QC v1 reviewed 1,288 suspect observations,
implemented two high-confidence overlays (*Croceitalea marina* 0.4–0.6 µm and
*Nioella aestuarii* 0.8–1.0 µm), and retains 1,286 unresolved contexts. Raw
BacDive values are immutable. Harmonized taxonomy reduced the apparent phylum
reporting association from Cramér's V=0.528 to V=0.154; residual reporting
heterogeneity remains.

## Geometry and future datasets

Microbial data retain width/length bounds, shape, multiple observations, raw
and normalized values, and verified overlays. For constriction transit, minimum
cross-sectional dimension may be a first-order quantity; pore occupation also
requires full geometry and length. Later simple geometries may include spheres
for cocci and spherocylinders for rods. Filamentous, pleomorphic, branched,
stalked, aggregate/chain-forming, and other complex morphologies require
separate treatment.

A planned environmental/subsurface microbial dataset will compile direct
observations of ultrasmall cells, oligotrophic aquifer organisms, deep-subsurface
cells, CPR/Patescibacteria, DPANN, starvation-associated reduction, dormant
states, and ultramicrocells where available. It will provide an in-situ
counterpart to the cultured baseline; no numerical environmental claim is made
currently.

For matrix-hosted systems, pore-body and pore-throat distributions, connectivity,
tortuosity, and mineral-specific architecture are distinct variables. A large
pore body behind sub-cellular throats may permit occupation but not migration.
For fractures, aperture distributions, local constrictions, connectivity,
roughness, coatings, fillings, fluid volume, wall area, and surface colonization
must be treated separately from matrix pores.

## Working conceptual quantities

`R_occupancy = d_pore / d_cell`, `R_transit = d_throat / d_cell`, and
`R_fracture = a_local / d_cell` are conceptual ratios, not validated models.
No universal critical values are assigned. Likewise, `phi_bio = phi × F_size ×
F_connectivity` is a working concept: total porosity multiplied by the compatible
void fraction and its accessible connected-network fraction. Future work should
integrate microbial distributions against throat distributions rather than use
a single cutoff.

Cellular connectivity differs from hydraulic/water and solute/gas connectivity.
Sub-cellular pathways can transmit water, gases, ions, electron donors/acceptors,
and dissolved organic matter while preventing whole-cell transit. Geometrically
isolated cells can therefore remain metabolically connected.

## Planned integration and questions

Matrix and fracture accessibility will remain separate until an integrated
framework can couple them. Longer term, the project will test whether geometry
and connectivity improve prediction of solid- and fluid-associated subsurface
cell abundance beyond lithology or bulk porosity alone.

Questions for geological discussion include the biologically relevant
constriction metric; comparability among mercury intrusion, micro/nano-CT, gas
adsorption, NMR, thin sections, and microscopy; fracture aperture and
connectivity scales; burial stress, weathering, fillings, and alteration; and
whether lithology priors can be defensible or predictions must be
formation-specific. Biological questions include clearance, orientation,
deformability, motility, dormant/spore/ultrasmall states, weighting schemes,
cultured-versus-in-situ dimensions, and separation of occupation, colonization,
transport, and metabolic persistence.
