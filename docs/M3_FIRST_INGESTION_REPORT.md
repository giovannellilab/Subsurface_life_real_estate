# M3 first ingestion report

Status: **complete for scientific review** (2026-09-26).

## What was ingested

| Source | Samples/cases | Method-specific content retained | Derived rows |
| --- | ---: | --- | ---: |
| Lipnice granite, PANGAEA.898001 | 21 specimens from MEL-5 | MIP incremental intrusion porosity by entry/throat-equivalent bin; intrusion only | 1,365 bins |
| Fontainebleau/Berea, Zenodo.1184144 v1 | 3 source-labelled PNM cases | Separate micro-CT/PNM pore-body and pore-throat object tables | 46,467 bodies; 173,174 throats |

This produces 24 sample/case records and 27 measurements. All raw artifacts
are local and gitignored; checksums, URLs, and transformation details are in
[the provenance record](provenance/m3_first_ingestion_2026-09-26.md).

## Native descriptive results

Lipnice has 65 intrusion bins per specimen spanning source-labelled
entry-equivalent bins of 0.008–309 µm. Summed incremental intrusion porosity
across those retained bins ranges from 0.0050% to 0.0653% among the 21
specimens. This is an MIP intrusion observation, not a direct pore-body result.

The network data retain `EqRadius` exactly as supplied. The 5th/50th/95th
percentiles (µm, radius) are: Fontainebleau bodies 0.459/4.547/18.268 and
throats 1.002/3.830/13.950; Berea case 2 bodies 1.691/2.737/7.013 and throats
0.358/1.294/3.502; Berea case 3 bodies 1.583/2.746/5.791 and throats
0.361/1.321/3.071. These are within-method, case-labelled descriptions—not
combined sandstone distributions and not converted to diameters.

## Schema outcome

The reconnaissance model worked for samples, measurements, and binned MIP
data. The PNM source demonstrated one necessary addition: a source-preserving
`network_objects.csv` table. It holds explicit geometry class, original and
normalized-unit radius, and object attributes without pretending that these are
generic pore sizes. No universal `pore_size` field was added.

One source-format issue was discovered: the two Case2 CSV headers contain
unquoted commas and replacement characters around the micro symbol. The parser
uses the explicit documented field order for those headers and flags every
affected derived object; source bytes remain authoritative.

## Coverage and unresolved comparability

| Lithology | MIP | micro-CT/PNM | Status |
| --- | --- | --- | --- |
| Plutonic crystalline | Lipnice throat/entry equivalent | — | ingested |
| Siliciclastic sandstone | — | Fontainebleau/Berea bodies and throats | ingested |
| Mudstone, carbonate, volcanic, ultramafic/serpentinized, metamorphic | — | — | no processed artifact yet |

MIP entry-equivalent binning and CT/PNM equivalent radius have distinct
physics, definitions, and observational windows. The sandstone CSV does not
report CT voxel size or extraction parameters, so its resolution window is
explicitly unknown here. These distributions must not be pooled, ranked as a
single pore-size variable, or used for microbial accessibility at this stage.

## Deferred/unusable for this pass

West Trenton’s public catalogue endpoint returned access denial in this
environment. Estaillades resolves to image-resource links rather than a compact
numeric distribution table. The Mendeley basalt page confirms CC-BY-4.0 but its
public metadata endpoint did not yield file inventory. YODA serpentinite
returned 403. Carrara’s smallest segmentation is 292 MB and its deposit warns
that the segmentation overestimates crack volume. All are deferred pending an
artifact-level acquisition and scientific review; none is interpreted as a
negative geological result.
