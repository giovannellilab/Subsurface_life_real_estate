# M1 cultured microbial geometry resource v1

## Purpose and population

This is the quality-controlled cultured-species geometry resource used as the
current biological comparison baseline.  It represents
`P(cell geometry | cultured, formally described prokaryote, morphology
recorded)`, not an environmental or subsurface community distribution.

The strict analytical layer contains **4,452 species** with a canonical
morphology record and LPSN name-and-type support.  Canonical values preserve
reported minimum and maximum dimensions; a midpoint is a transparent derived
summary, not an additional source measurement.

## Resource depth

| Stage | Count |
| --- | ---: |
| BacDive records | 101,320 |
| Exact type strains | 22,122 |
| Original species-label groups | 21,985 |
| Bacteria / Archaea / domain unreported | 21,262 / 762 / 98 |
| Strains with shape | 9,816 |
| Strains with normalized length | 5,897 |
| Strains with normalized width | 5,779 |
| Normalized-width observations | 5,849 |
| Observations with both axes in one record | 5,600 |
| Analysis-eligible observations / strains | 4,647 / 4,624 |
| Explicit exclusions | 1,202 |
| Species with a canonical width | 4,557 |
| Strict LPSN-supported canonical species | 4,452 |

Scientific QC reviewed 1,288 suspect observations, applied two
high-confidence source overlays, and retained 1,286 unresolved contexts rather
than silently correcting them.  Harmonising taxonomy reduced the apparent
phylum/reporting association from Cramér's V = 0.528 to 0.154.  That reduction
does not remove the cultured, taxonomic, and morphology-reporting biases.

## Width

The strict species-level width population is N = 4,452 for each convention.

| Canonical convention | Median (µm) | p5–p95 (µm) |
| --- | ---: | --- |
| Minimum | 0.55 | 0.25–1.168 |
| Midpoint | 0.60 | 0.30–1.25 |
| Maximum | 0.70 | 0.35–1.40 |

The primary first-order comparison uses canonical midpoint width,
`(width_min + width_max) / 2` when both bounds are supplied.  Width is a
transverse-dimension proxy, not a universal microbial diameter or a full
description of cell geometry.

## Length and descriptive simple-cell volume

Canonical length midpoint is available for **4,297 strict species**.  Its
median is **2.00 µm** and p5–p95 is **0.85–6.00 µm**.  The reported maximum has
a very long source tail, so its distribution is shown on a log axis and is not
summarised as a typical cell length beyond the robust percentiles.

Estimated equivalent single-cell volume is calculated only for **3,945**
strict canonical species with simple, defensible morphology and both axes:
3,765 rods and 180 cocci/spherical cells.  Excluded from that calculation are
155 species without both axes, 345 complex or unresolved morphology records,
and 7 rod records whose reported total length is shorter than width.

For spherical cells with diameter `d`, `V = πd³ / 6`.  For rods represented as
a spherocylinder with total end-to-end length `L` and diameter `d`,
`V = π(d/2)²(L − d) + πd³/6`.  Here `L − d` is the cylindrical length and the
final term is the two hemispherical endcaps.  The volume distribution has a
median of **0.509 µm³** and p5–p95 of **0.0871–3.47 µm³**.  It is descriptive
occupancy context only and is never used as a pore-throat transit dimension.

Filamentous, branched, strongly pleomorphic, stalked, chain/aggregate, and
other complex records are deliberately not assigned one-cell volumes.

## Limits

This resource does not represent in-situ subsurface cells, ultrasmall or
difficult-to-cultivate lineages, spores, biofilms, deformation, orientation,
or physiological state.  M2 is reserved for a separately evidenced
environmental and subsurface microbial geometry resource.
