# M3 Literature Lithology Atlas v1 provenance

Access and extraction date: **2026-09-28** (Europe/Rome).

## Scope

The atlas was intentionally bounded at approximately five useful independent
literature records for each of nine high-level lithologies. Search stopped once
each class had a primary-data core plus an appropriate review, compilation or
external benchmark. No CT image volume or other large raw dataset was acquired.
The already local 3.0 MB Park & Santamarina supplement was re-read; other new
evidence was extracted from publisher text, institutional tables, article text
and existing M3 source papers/metadata.

This layer complements, but does not overwrite or pool with, Reference
Lithology Dataset v1.

## Search and selection rules

- Prefer primary papers, institutional expedition reports, data-release pages,
  accessible article tables and small supplements.
- Use reviews for classification and broad range support, not as new physical
  specimens or field sites.
- Retain one source count for one publication/data release even when it covers
  several lithologies or formations.
- Map one row per independent natural setting. Use exact coordinates only when
  source supported; otherwise use a clearly marked approximate locality or
  regional centroid.
- Do not map laboratory packs or remoulded standards as natural locations.
- Do not assign a single invented point to a global/multi-region review.
- Keep source-native radius/diameter and weighting semantics in the observation
  table. Broad envelope size bounds are only order-of-magnitude audit domains.
- Keep matrix pores, pore bodies, throats/entries, grain-boundary pores,
  microcracks, fractures, vugs and vesicles distinct.

## Park & Santamarina benchmark

Local source file:

`data/raw/m3_audit/park_santamarina_2020/41598_2020_78714_MOESM1_ESM.pdf`

The file remains raw, local and gitignored. Supplementary Table S2 was read
directly. It contains:

- 14 natural-soil dataset entries, fitted mean pore diameter 0.11–178.4 µm;
- 25 remoulded-soil entries, 0.16–233 µm;
- 23 carbonate entries/groups with 35 reported fitted components,
  0.37–31.5 µm;
- 17 sandstone entries/groups with 23 fitted components, 0.019–3.648 µm;
- four shale entries/groups with eight fitted components, 0.004–0.112 µm.

These 83 entries/groups are reported separately from the atlas's conservative
primary-specimen minimum because Supplementary Table S2 is a secondary
compilation and some underlying papers are independently represented in the
atlas.

## Quantitative text/table extractions

The most consequential extractions were checked against source text/tables:

- Ferrick et al. 2021, Methods and Table 1: three natural Alameda beach cores,
  one pluviated comparison, 6.45 µm voxels, porosity and coordination.
- Cao et al. 2016, Results and Supplementary Tables S2–S4: 15 Chang-7
  tight-sandstone PSD specimens, porosity, direct pore classes and MIP throat
  radii.
- Zhang et al. 2024, petrophysical results/Table 1/Figure 5: 45 Yanchang
  specimens and representative MIP throat parameters.
- Shapiro et al. 2017, Methods/Results and USGS release: 94 West Trenton MIP
  specimens from seven boreholes; majority porosity range and large-entry
  porosity statement.
- Moshier 1989 review: intercrystalline and secondary carbonate micropore
  scales; microvugs remain a separate class.
- Adelinet et al. 2010, sample description/Figure 1: 7.93% open porosity and
  separate crack/equant-pore MIP modes in fresh Reykjanes basalt.
- Johnson 1980, USGS Professional Paper 1123-B Table 1: Kilauea Iki helium- and
  water-accessible porosity versus depth.
- Heap et al. 2018, sample table/Figure 4b/discussion: 4% connected porosity,
  mean MIP throat radius 0.17 µm, and 65% of porosity accessed through radii
  below 0.5 µm in the Mt Etna basalt.
- Goldberg et al. 1991, Hole 735B Table 2 and Figures 3–6: corrected log/core
  porosity and fracture-zone permeability.
- Chogani et al. 2023, Methods and Figures 2–5/9: direct FIB-SEM/TEM local
  porosity and nanometre pore scale in two serpentinite settings.
- Kawano et al. 2017, Table 1 and supplements: dredged-serpentinite porosity
  and the disconnect between bulk porosity and permeability.
- Yang et al. 2022, Tables 3–6 and Figures 5–8: schist/mylonite porosity,
  matrix PSD and explicitly separate structural/weathering microfractures.

Existing M3 source-paper extractions are inherited from
`docs/provenance/m3_geological_audit_2026-09-28.md`; native third-party files
and row-level processed outputs were not changed.

## Coordinate policy

The coordinate table stores a precision class and a short coordinate-
provenance statement. Exact site/borehole coordinates are used for Alameda,
Lipnice, Sellafield and scientific-drilling settings where available.
Approximate-locality points identify named quarry/stone/project districts.
Regional centroids are only cartographic anchors for formation/basin/volcanic
regions and are never presented as sample coordinates.

Atlantis Massif is one mapped setting associated with both gabbro/mafic and
serpentinite/ultramafic evidence. It is one point in the map table and counts
once within each applicable lithology.

## Conservative specimen counting

`documented_primary_physical_specimens_minimum` includes only rows marked
`count_in_primary_specimen_minimum=yes`. Duplicate geometry rows from the same
specimen, reviews, Park benchmark groups, continuous logs, unspecified sample
counts and known repeated specimens are excluded. The minimum therefore favors
under-counting over false replication.

Notable choices:

- Fontainebleau/Berea contributes two physical rocks, not three experimental
  cases.
- Lipnice contributes 21 specimens but one borehole/site.
- Pezard's 29 Hole 735B specimens are counted; overlapping shipboard/log
  records are not added.
- Chogani contributes two geological sample settings, while its many FIB/TEM
  image domains do not become physical specimens.
- Reviews and compilation tables with uncertain specimen independence are not
  added to the minimum.

## Envelope construction

Reference envelopes were set after comparing the selected observations with
the class-specific literature. They are deliberately broad, state-stratified
sanity checks. They are not meta-analytic confidence intervals, universal
constants, or priors for the pore × microbe model.

Empty effective/connected-porosity bounds indicate that the selected evidence
does not support a class-wide range under a consistent definition. Likewise,
the serpentinite mud-volcano row has no pore/throat scale because the source is
bulk/transport evidence rather than a coherent-rock PSD.

## Reproducibility

Build:

```bash
MPLCONFIGDIR=/tmp/mpl-atlas .venv/bin/python scripts/build_literature_lithology_atlas.py
```

Validate:

```bash
.venv/bin/python scripts/validate_literature_lithology_atlas.py
```

The builder writes the tracked catalogue tables and three local, gitignored
derived SVGs. It does not read or alter the microbial dataset and does not run
the pore × microbe analysis.
