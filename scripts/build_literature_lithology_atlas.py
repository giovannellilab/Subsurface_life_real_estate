"""Build the compact Literature Lithology Atlas v1.

This is a curated literature overlay, not a new pore-size harmonisation.  It
stores source-reported quantities and broad sanity envelopes alongside the M3
resource.  Review/benchmark rows are never counted as new physical specimens,
and approximate map coordinates are explicitly labelled.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalogues"
OUT = ROOT / "data/processed/m3_literature_lithology_atlas_v1"
PLOTS = OUT / "plots"

LITHOLOGIES = [
    "unconsolidated sand/sediment", "sandstone", "mudstone/shale", "carbonate",
    "basalt/volcanic rock", "granite/granitoid", "gabbro/mafic crystalline",
    "serpentinite/ultramafic", "metamorphic rock",
]


def source(source_id, year, citation, title, identifier, url, classes, role, note):
    return dict(source_id=source_id, year=year, citation=citation, title=title,
                persistent_identifier=identifier, landing_url=url,
                lithology_classes="|".join(classes), evidence_role=role,
                atlas_use=note)


SOURCES = [
    source("LIT-001", 2020, "Park & Santamarina (2020)", "The critical role of pore size on depth-dependent microbial cell counts in sediments", "doi:10.1038/s41598-020-78714-3", "https://doi.org/10.1038/s41598-020-78714-3", ["unconsolidated sand/sediment", "sandstone", "mudstone/shale", "carbonate"], "benchmark synthesis", "Supplementary Table S2: 39 soil and 44 intact-rock fitted pore-diameter datasets; benchmark only, not pooled primary data."),
    source("LIT-002", 2009, "Dong & Blunt (2009); Imperial College release", "Pore-network extraction from micro-computerized-tomography images", "doi:10.6084/m9.figshare.1189259.v1", "https://doi.org/10.6084/m9.figshare.1189259.v1", ["unconsolidated sand/sediment"], "primary quantitative dataset", "F42A Ottawa quartz sand laboratory pack; body/throat network and connectivity."),
    source("LIT-003", 2021, "Ferrick et al. (2021)", "Microstructural differences between naturally-deposited and laboratory beach sands", "doi:10.1007/s10035-021-01169-4", "https://doi.org/10.1007/s10035-021-01169-4", ["unconsolidated sand/sediment"], "primary study", "Natural beach cores and a laboratory-pluviated comparison; porosity and grain coordination."),
    source("LIT-004", 2000, "Winters (2000)", "Water content, porosity and grain-size distribution of sediments from ODP Leg 164 sites", "doi:10.1594/PANGAEA.804616", "https://doi.org/10.1594/PANGAEA.804616", ["unconsolidated sand/sediment"], "primary tabular dataset", "Natural marine sediments; porosity and grain-size context without a pore-throat distribution."),
    source("LIT-005", 2003, "Tanaka et al. (2003)", "Pore size distribution of clayey soils measured by mercury intrusion porosimetry and its relation to hydraulic conductivity", "doi:10.3208/sandf.43.6_63", "https://doi.org/10.3208/sandf.43.6_63", ["unconsolidated sand/sediment"], "primary study", "Natural and remoulded clays; MIP size distributions used in Park & Santamarina S2."),
    source("LIT-006", 2018, "Thomson et al. (2018)", "Pore network modeling data for Fontainebleau and Berea sandstones", "doi:10.3389/feart.2018.00058", "https://doi.org/10.3389/feart.2018.00058", ["sandstone"], "primary study and dataset", "0.74 um voxel synchrotron CT/PNM; resolved connected phase."),
    source("LIT-007", 2021, "Payton et al. (2021)", "Pore-scale assessment of subsurface sandstone porosity and permeability", "doi:10.1144/petgeo2020-092", "https://doi.org/10.1144/petgeo2020-092", ["sandstone"], "primary study and dataset", "Seven Wilmslow Sandstone plugs from Sellafield BH13B; micro-CT/PNM."),
    source("LIT-008", 2016, "Cao et al. (2016)", "Pore structure characterization of Chang-7 tight sandstone using MICP combined with N2GA", "doi:10.1038/srep36919", "https://doi.org/10.1038/srep36919", ["sandstone"], "primary study", "Fifteen quantified tight-sandstone samples; MICP, gas adsorption and microscopy."),
    source("LIT-009", 2024, "Zhang et al. (2024)", "Pore-throat structure, fractal characteristics and permeability prediction of tight sandstone: Yanchang Formation", "doi:10.1038/s41598-024-79203-7", "https://doi.org/10.1038/s41598-024-79203-7", ["sandstone"], "primary study", "Forty-five samples; sixteen representative MICP curves and pore-throat statistics."),
    source("LIT-010", 2022, "Fan et al. (2022)", "Assessment of multi-scale pore structures for shale samples", "doi:10.1016/j.fuel.2022.125463", "https://doi.org/10.1016/j.fuel.2022.125463", ["mudstone/shale"], "primary study and dataset", "W23 and J24 CTSTA/model data; model radius is not a direct observed throat or body."),
    source("LIT-011", 2017, "Shapiro et al. (2017)", "Porosity and pore size distribution in a sedimentary rock", "doi:10.1016/j.jconhyd.2017.06.006", "https://doi.org/10.1016/j.jconhyd.2017.06.006", ["mudstone/shale"], "primary study and dataset", "Ninety-four MIP samples from seven West Trenton boreholes."),
    source("LIT-012", 2012, "Loucks et al. (2012)", "Spectrum of pore types and networks in mudrocks", "doi:10.1306/08171111061", "https://doi.org/10.1306/08171111061", ["mudstone/shale"], "multi-formation primary synthesis", "FIB-SEM classification across several North American shale systems; source count is one, sites remain multiple."),
    source("LIT-013", 2013, "Kuila & Prasad (2013)", "Specific surface area and pore-size distribution in clays and shales", "doi:10.1111/1365-2478.12028", "https://doi.org/10.1111/1365-2478.12028", ["mudstone/shale"], "primary study and methods synthesis", "Gas adsorption and MIP; exposes method windows and characteristic clay-related 3 nm pores."),
    source("LIT-014", 2022, "Liu, Ma & Zhu (2022)", "Pore structure characteristics of biogenic carbonate rocks in the South China Sea", "doi:10.3390/app12052611", "https://doi.org/10.3390/app12052611", ["carbonate"], "primary study and dataset", "Five natural carbonate specimens at 61.75 um voxels; resolved maximum-ball bodies and throats."),
    source("LIT-015", 1989, "Moshier (1989)", "Microporosity in micritic limestones: a review", "doi:10.1016/0037-0738(89)90132-2", "https://doi.org/10.1016/0037-0738(89)90132-2", ["carbonate"], "review", "Micrite matrix-pore types and reported intercrystalline/secondary micropore scales."),
    source("LIT-016", 2020, "Cardona & Santamarina (2020)", "Carbonate rocks: matrix permeability estimation", "AAPG Bulletin 104:131-144", "https://doi.org/10.1306/08071918123", ["carbonate"], "primary compilation", "Matrix-scale carbonate petrophysics; source behind part of Park & Santamarina S2."),
    source("LIT-017", 1991, "Churcher et al. (1991)", "Rock properties of Berea sandstone, Baker dolomite, and Indiana limestone", "doi:10.2118/21044-MS", "https://doi.org/10.2118/21044-MS", ["carbonate"], "primary comparative study", "Reference carbonate petrophysics; bimodal Indiana limestone fits in Park & Santamarina S2."),
    source("LIT-018", 2022, "Menefee et al. (2022)", "Changes in pore geometry and connectivity in a basalt pore network", "doi:10.1029/2021WR030275", "https://doi.org/10.1029/2021WR030275", ["basalt/volcanic rock"], "primary study and dataset", "Port Fairy basalt; current detailed table is an unreacted ungrooved half-core resolved at 14.99 um."),
    source("LIT-019", 1999, "Saar & Manga (1999)", "Permeability-porosity relationship in vesicular basalts", "doi:10.1029/1998GL900256", "https://doi.org/10.1029/1998GL900256", ["basalt/volcanic rock"], "primary study", "Central Oregon scoria/flows; vesicle bodies and connecting apertures are distinct."),
    source("LIT-020", 1980, "Johnson (1980)", "Porosity and density of Kilauea volcano basalts, Hawaii", "USGS Professional Paper 1123-B", "https://pubs.usgs.gov/pp/1123a-d/", ["basalt/volcanic rock"], "primary tabular study", "Kilauea Iki drill core; helium- and water-accessible porosity versus depth."),
    source("LIT-021", 2010, "Adelinet et al. (2010)", "Frequency and fluid effects on elastic properties of basalt", "doi:10.1029/2009GL041660", "https://doi.org/10.1029/2009GL041660", ["basalt/volcanic rock"], "primary study", "Fresh Reykjanes basalt; MIP separates crack and equant-pore modes."),
    source("LIT-022", 2018, "Heap et al. (2018)", "Permeability of volcanic rocks to gas and water", "doi:10.1016/j.jvolgeores.2018.02.002", "https://doi.org/10.1016/j.jvolgeores.2018.02.002", ["basalt/volcanic rock"], "primary comparative study", "Basalt plus andesite; pressure-dependent permeability and MIP pore-throat context."),
    source("LIT-023", 2019, "Stanek & Geraud (2019)", "Granite microporosity changes due to fracturing and alteration", "doi:10.5194/se-10-251-2019", "https://doi.org/10.5194/se-10-251-2019", ["granite/granitoid"], "primary study and dataset", "Twenty-one deliberately state-diverse specimens from one MEL-5 borehole."),
    source("LIT-024", 1989, "Wong, Fredrich & Gwanmesia (1989)", "Crack aperture statistics and pore-space fractal geometry of Westerly granite and Rutland quartzite", "doi:10.1029/JB094iB08p10267", "https://doi.org/10.1029/JB094iB08p10267", ["granite/granitoid", "metamorphic rock"], "primary comparative study", "Crack-aperture stereology; distinguishes crystalline microcracks from generic pores."),
    source("LIT-025", 2016, "Blake et al. (2016)", "Effect of fracture density and stress state on Westerly granite", "doi:10.1002/2015JB012310", "https://doi.org/10.1002/2015JB012310", ["granite/granitoid"], "primary experimental study", "Untreated and thermally cracked Westerly granite; altered state kept separate."),
    source("LIT-026", 2024, "Sousa et al. (2024)", "Experimental investigation on moisture movement behavior of granites", "doi:10.1007/s10064-024-03935-z", "https://doi.org/10.1007/s10064-024-03935-z", ["granite/granitoid"], "primary study", "Reference and contaminated Portuguese granites; MIP open porosity and pore-diameter classes."),
    source("LIT-027", 2015, "Anovitz & Cole (2015)", "Characterization and analysis of porosity and pore structures", "doi:10.2138/rmg.2015.80.04", "https://doi.org/10.2138/rmg.2015.80.04", ["granite/granitoid"], "review", "Method-aware crystalline-rock pore characterization and weathering examples."),
    source("LIT-028", 2017, "Falcon-Suarez et al. (2017)", "Elastic and electrical properties and permeability of serpentinites from Atlantis Massif", "doi:10.1093/gji/ggx341", "https://doi.org/10.1093/gji/ggx341", ["gabbro/mafic crystalline", "serpentinite/ultramafic"], "primary study and dataset", "Four mafic and four serpentinised cores; bulk porosity and pressure-dependent transport, no PSD."),
    source("LIT-029", 1991, "Goldberg, Broglia & Becker (1991)", "Fracturing, alteration, and permeability: in-situ properties in Hole 735B", "ODP Scientific Results 118", "https://www-odp.tamu.edu/publications/118_SR/VOLUME/CHAPTERS/sr118_14.pdf", ["gabbro/mafic crystalline"], "primary borehole study", "Corrected neutron/core porosity and fracture-controlled permeability in oceanic gabbro."),
    source("LIT-030", 1991, "Pezard et al. (1991)", "Electrical conduction in oceanic gabbros, Hole 735B", "ODP Scientific Results 118", "https://www-odp.tamu.edu/publications/118_SR/", ["gabbro/mafic crystalline"], "primary study", "Twenty-nine gabbroic specimens; electrical formation factor, porosity, crack/microcrack interpretation."),
    source("LIT-031", 1999, "Dick et al. / ODP Leg 176 Shipboard Scientific Party (1999)", "Physical properties of principal lithologies, Hole 735B", "ODP Initial Reports 176 Table T16", "https://www.iodp.tamu.edu/publications/176_IR/CHAP_03/Output/chap215a.htm", ["gabbro/mafic crystalline"], "primary tabular compilation", "Hundreds of measurements from one borehole; measurement count is not site replication."),
    source("LIT-032", 2014, "Gillis et al. / IODP Expedition 345 (2014)", "Hess Deep plutonic crust: Hole U1415 physical properties", "doi:10.2204/iodp.proc.345.2014", "https://publications.iodp.org/proceedings/345/345title.htm", ["gabbro/mafic crystalline"], "primary expedition report", "Discrete gabbroic core porosity/density measurements at Hess Deep."),
    source("LIT-033", 2016, "Tutolo et al. (2016)", "Nanoscale constraints on porosity generation and fluid flow during serpentinization", "doi:10.1130/G37349.1", "https://doi.org/10.1130/G37349.1", ["serpentinite/ultramafic"], "primary study", "(U)SANS on Atlantis Massif and Duluth Complex materials; intrinsic nanopores plus reaction fractures."),
    source("LIT-034", 2023, "Chogani et al. (2023)", "Decoding the nanoscale porosity in serpentinites", "doi:10.1007/s00410-023-02062-4", "https://doi.org/10.1007/s00410-023-02062-4", ["serpentinite/ultramafic"], "primary study and small quantitative supplement", "ODP Site 1274 and Roragen; FIB-SEM/TEM porosity and pore diameters."),
    source("LIT-035", 2017, "Kawano et al. (2017)", "Mantle hydration along outer-rise faults inferred from serpentinite permeability", "doi:10.1038/s41598-017-14309-9", "https://doi.org/10.1038/s41598-017-14309-9", ["serpentinite/ultramafic"], "primary comparative study", "Accretionary-prism and dredged low-temperature serpentinites; porosity, permeability and state."),
    source("LIT-036", 2019, "Morrow et al. (2019)", "Permeability, porosity, and frictional strength of IODP Expedition 366 cores", "doi:10.14379/iodp.proc.366.202.2019", "https://doi.org/10.14379/iodp.proc.366.202.2019", ["serpentinite/ultramafic"], "primary study", "Seven shallow cores from three Mariana forearc serpentinite mud volcanoes; special mud-volcano material."),
    source("LIT-037", 2022, "Yang et al. (2022)", "Semiquantitative microscopic pore characterizations of a metamorphic rock reservoir", "doi:10.1038/s41598-022-05960-y", "https://doi.org/10.1038/s41598-022-05960-y", ["metamorphic rock"], "primary study", "Eight schist/mylonite specimens; HPMI and gas adsorption retain pores and microfractures separately."),
    source("LIT-038", 2000, "Bagde (2000)", "Strength and porous properties of metamorphic rocks in the Himalayas", "doi:10.1023/A:1026518616345", "https://doi.org/10.1023/A:1026518616345", ["metamorphic rock"], "primary study", "Three schist varieties from Nathpa-Jhakri; MIP porosity and PSD."),
    source("LIT-039", 2000, "Siegesmund et al. (2000)", "Physical weathering of marbles caused by anisotropic thermal expansion", "doi:10.1007/s005310050324", "https://doi.org/10.1007/s005310050324", ["metamorphic rock"], "primary comparative study", "Marbles including Carrara; grain-boundary microcracks and thermal state are explicit."),
    source("LIT-040", 1982, "Kessler et al. / USGS (1982)", "Porosity and bulk density of sedimentary and metamorphic rocks", "USGS Open-File Report 82-166", "https://pubs.usgs.gov/of/1982/0166/report.pdf", ["metamorphic rock"], "reference compilation", "Broad porosity table used only as an envelope check, not as a site-level dataset."),
]


def obs(obs_id, source_id, lithology, subtype, state, setting, precision,
        specimens, total="", effective="", geometry="unresolved", size_min="",
        size_central="", size_max="", size_unit="um", convention="",
        weighting="", method="", window="", depth_state="", provenance="",
        counted="yes", note=""):
    return dict(observation_id=obs_id, source_id=source_id, lithology=lithology,
                subtype_or_state=subtype, sample_state=state,
                locality_formation_borehole=setting, location_precision=precision,
                physical_specimens=specimens, total_porosity_percent=total,
                effective_connected_porosity_percent=effective,
                geometry_class=geometry, size_min=size_min,
                size_central=size_central, size_max=size_max, size_unit=size_unit,
                radius_diameter_or_definition=convention, weighting_basis=weighting,
                method=method, resolution_or_detection_window=window,
                depth_stress_state_context=depth_state,
                exact_table_figure_provenance=provenance,
                count_in_primary_specimen_minimum=counted, interpretation_note=note)


OBSERVATIONS = [
    obs("OBS-001", "LIT-001", "unconsolidated sand/sediment", "natural soils", "natural; heterogeneous soil types", "14 source settings", "multiple/unknown", 14, geometry="fitted pore scale", size_min=0.11, size_max=178.4, convention="fitted mean pore diameter", weighting="source-dependent distributions fitted by Park & Santamarina", method="source-dependent; benchmark fit", provenance="Supplementary Table S2, natural soils [14]", counted="benchmark", note="Fourteen dataset entries, not asserted here as fourteen independently verified physical specimens."),
    obs("OBS-002", "LIT-001", "unconsolidated sand/sediment", "remoulded soils", "laboratory/remoulded", "laboratory materials", "laboratory", 25, geometry="fitted pore scale", size_min=0.16, size_max=233, convention="fitted mean pore diameter", weighting="source-dependent", method="source-dependent; benchmark fit", provenance="Supplementary Table S2, remoulded soils [25]", counted="benchmark"),
    obs("OBS-003", "LIT-002", "unconsolidated sand/sediment", "Ottawa F42 quartz sand pack", "laboratory pack", "Imperial College F42A", "laboratory", 1, total=33.0, geometry="pore body", size_central=46.48, convention="native pore radius; comparison diameter is separately derived", weighting="network-object count", method="micro-CT + extracted PNM", window="9.996 um voxel; 300^3 voxels", provenance="Results_F42A; Statoil node files; M3-RLD v1 sample summary"),
    obs("OBS-004", "LIT-002", "unconsolidated sand/sediment", "Ottawa F42 quartz sand pack", "laboratory pack", "Imperial College F42A", "laboratory", 1, total=33.0, geometry="pore throat", size_central=26.75, convention="native throat radius", weighting="network-object count", method="micro-CT + extracted PNM", window="9.996 um voxel; 300^3 voxels", provenance="Results_F42A; Statoil link files; M3-RLD v1 sample summary", counted="no", note="Same physical pack as OBS-003; not counted twice."),
    obs("OBS-005", "LIT-003", "unconsolidated sand/sediment", "beach sand", "natural, undisturbed", "unnamed beach, Alameda County, California", "exact", 3, total="37.1-40.3", geometry="grain-contact network", convention="grain coordination, not a pore-body or throat size", weighting="grain count", method="synchrotron micro-CT", window="6.45 um voxel", depth_state="1, 6 and 11 cm below beach surface", provenance="Methods sample collection; Table 1", note="Mean grain coordination 7.71-8.31; three depths at one beach."),
    obs("OBS-006", "LIT-003", "unconsolidated sand/sediment", "same beach sand", "laboratory pluviated", "laboratory reconstruction of Alameda sand", "laboratory", 1, total=38.5, geometry="grain-contact network", convention="grain coordination, not a pore-body or throat size", weighting="grain count", method="synchrotron micro-CT", window="6.45 um voxel", provenance="Table 1", note="Mean grain coordination 7.45; kept separate from the natural cores."),
    obs("OBS-007", "LIT-005", "unconsolidated sand/sediment", "Bothkennar/Osaka/Kyoto natural clays", "natural clay", "Scotland and Japan source localities", "multiple/approximate", 4, geometry="MIP entry-equivalent", size_min=0.33, size_max=1.58, convention="Park S2 fitted mean diameter from Tanaka et al. MIP distributions", weighting="intrusion/source fit", method="MIP", provenance="Park & Santamarina Supplementary Table S2 entries 1-4; Tanaka et al. 2003", note="Grouped only for compact atlas display; localities remain distinct in the source paper."),
    obs("OBS-008", "LIT-001", "sandstone", "intact sandstones", "intact natural rocks", "multiple literature settings", "multiple/unknown", 17, geometry="fitted pore scale", size_min=0.019, size_max=3.648, convention="fitted mean pore diameter; source methods differ", weighting="source-dependent", method="source-dependent; benchmark fit", provenance="Supplementary Table S2, sandstones [17]", counted="benchmark"),
    obs("OBS-009", "LIT-006", "sandstone", "Fontainebleau and Berea reference sandstone", "natural reference specimens; one saturated case", "sample origins not reported in release", "unknown", 2, total="3.8;19.9", effective="3.0;19.6", geometry="pore body", size_min=2.74, size_max=4.54, convention="sample median native EqRadius", weighting="resolved network-object count", method="synchrotron micro-CT + PerGeos PNM", window="0.74 um voxel; connected segmented phase", provenance="paper porosity table; Zenodo network tables; M3 audit sample medians"),
    obs("OBS-010", "LIT-006", "sandstone", "Fontainebleau and Berea reference sandstone", "natural reference specimens", "sample origins not reported in release", "unknown", 2, geometry="pore throat", size_min=1.29, size_max=3.80, convention="sample median native throat EqRadius", weighting="resolved connected-throat object count", method="synchrotron micro-CT + PerGeos PNM", window="0.74 um voxel; connected segmented phase", provenance="Zenodo network tables; M3 audit sample medians", counted="no", note="Same two physical specimens as OBS-009."),
    obs("OBS-011", "LIT-007", "sandstone", "Wilmslow Sandstone Formation", "natural borehole plugs, epoxy impregnated", "Sellafield borehole 13B, Cumbria", "exact borehole", 7, total="9.77-26.42", effective="8.89-26.31", geometry="pore body", size_min=2.10, size_max=16.06, convention="range of sample median native EqRadius", weighting="all extracted objects; connected and disconnected mixed", method="micro-CT + PerGeos PNM", window="2.6860-2.8409 um voxel", depth_state="seven borehole depths", provenance="paper Table 2; Figshare all-object tables; M3 audit"),
    obs("OBS-012", "LIT-007", "sandstone", "Wilmslow Sandstone Formation", "natural borehole plugs, epoxy impregnated", "Sellafield borehole 13B, Cumbria", "exact borehole", 7, geometry="pore throat", size_min=5.85, size_max=11.62, convention="range of sample median native throat EqRadius", weighting="all extracted objects; connected and disconnected mixed", method="micro-CT + PerGeos PNM", window="2.6860-2.8409 um voxel", provenance="Figshare all-object tables; M3 audit", counted="no", note="Same seven plugs as OBS-011; not a connected-path-only distribution."),
    obs("OBS-013", "LIT-008", "sandstone", "Chang-7 tight lithic arkose/feldspathic litharenite", "fresh natural core", "Longdong area, Ordos Basin", "regional", 15, total="1.20-13.98", geometry="matrix pore body", size_min=0.05, size_max=100, convention="direct microscopy ranges: clay intercrystalline through dissolved pores", weighting="descriptive/method-specific", method="SEM + thin section + N2 adsorption", window="N2 1.7-300 nm; combined PSD 2-10000 nm", depth_state="about 1441-2069 m examples", provenance="Results pore types; Figs 2 and 7; Supplementary Tables S2-S4"),
    obs("OBS-014", "LIT-008", "sandstone", "Chang-7 tight sandstone", "fresh natural core", "Longdong area, Ordos Basin", "regional", 15, geometry="pore throat / entry constriction", size_min=0.006, size_central=0.127, size_max=0.910, convention="MICP median pore-throat radius range; central is study average", weighting="mercury intrusion", method="MICP", window="reported MICP range; high-pressure lower-limit caveat", provenance="Results pore throat structure; Supplementary Table S3", counted="no"),
    obs("OBS-015", "LIT-009", "sandstone", "Yanchang Formation tight sandstone", "natural reservoir core", "southeast Ordos Basin", "regional", 45, total="0.5-10.5", geometry="pore throat / entry constriction", size_central=0.10, convention="example type-I median MICP throat radius; maximum-throat mean 0.89 um", weighting="mercury intrusion", method="MICP + microscopy", provenance="porosity results; Table 1 and Figure 5", note="Sixteen representative MICP specimens within a 45-sample petrophysical suite."),
    obs("OBS-016", "LIT-001", "mudstone/shale", "intact shales", "intact natural rocks", "North Sea, Mancos, Bakken, Woodford source settings", "regional/multiple", 4, geometry="fitted pore scale", size_min=0.004, size_max=0.112, convention="fitted mean pore diameter", weighting="source-dependent", method="source distributions fitted by Park & Santamarina", provenance="Supplementary Table S2, shales [4]", counted="benchmark"),
    obs("OBS-017", "LIT-010", "mudstone/shale", "W23/J24 marine shale", "natural samples; model-derived curve", "formation/locality unresolved in deposit", "unknown", 2, geometry="modelled pore-cluster/domain", size_min=0.0002, size_central=0.181, size_max=60, convention="W23 modelled radius R; approximate weighted range/median from M3 audit; not an observed body/throat", weighting="modelled volume", method="CTSTA + multiscale fractal model", window="physical CTSTA resolution absent from deposit", provenance="Harvard Dataverse WBSHKX/D1LDSO; M3 audit", note="J24 lacks a resolved physical R unit and is excluded from physical-size comparison."),
    obs("OBS-018", "LIT-011", "mudstone/shale", "Lockatong Formation mudstone", "natural core; shallow fractured aquifer matrix", "former NAWC, West Trenton, New Jersey", "approximate locality", 94, total="mostly 1-10; overall ~2 orders of magnitude", geometry="pore throat / MIP entry", convention="MIP pore diameter", weighting="incremental intruded porosity", method="MIP", depth_state="seven boreholes; to ~35 m below land surface", provenance="paper Methods and Results; USGS data release 10.5066/F7GX48RZ", note="About 0.1% porosity is associated with the largest throat class; fracture porosity was not measured from cores."),
    obs("OBS-019", "LIT-013", "mudstone/shale", "natural clay-rich shales", "natural rocks and compacted clay analogues", "North American shale settings", "regional/multiple", "not stated in abstract", geometry="matrix pore", size_central=0.003, convention="characteristic gas-adsorption pore diameter in illite-smectite", weighting="adsorbed-volume/surface model", method="N2 adsorption + MIP", window="N2 <200 nm; MIP misses/perturbs finest shale pores", provenance="abstract and method discussion", counted="no", note="Review-supported scale, not a single lithology-wide mode."),
    obs("OBS-020", "LIT-001", "carbonate", "intact carbonates", "intact natural rocks", "multiple literature settings", "multiple/unknown", 23, geometry="fitted pore scale", size_min=0.37, size_max=31.5, convention="fitted mean pore diameter; multimodal rows retained", weighting="source-dependent", method="source-dependent; benchmark fit", provenance="Supplementary Table S2, carbonates [23]", counted="benchmark"),
    obs("OBS-021", "LIT-014", "carbonate", "biogenic carbonate rock A-E", "natural marine cores", "Nansha Islands, South China Sea", "regional", 5, total="7.35-23.41", geometry="pore body", size_min=108, size_max=139, convention="range of source median body radius", weighting="resolved network-object count", method="micro-CT + maximum-ball PNM", window="61.75 um voxel", depth_state="within 400 m below coral-reef surface", provenance="paper Tables 2-4; workbook REV2 tables; M3 audit"),
    obs("OBS-022", "LIT-014", "carbonate", "biogenic carbonate rock A-E", "natural marine cores", "Nansha Islands, South China Sea", "regional", 5, geometry="pore throat", size_min=54.3, size_max=97.0, convention="range of source median throat radius", weighting="resolved network-object count", method="micro-CT + maximum-ball PNM", window="61.75 um voxel", provenance="paper Table 4; workbook REV2 tables; M3 audit", counted="no", note="Carbonate A workbook/paper throat count and maximum disagree; workbook retained."),
    obs("OBS-023", "LIT-015", "carbonate", "micritic limestone", "natural, diagenetic matrix", "multiple Phanerozoic settings", "multiple/unknown", "review", total=">20 reported in some microporous limestones", geometry="matrix intercrystalline pore", size_min=5, size_max=10, convention="typical intercrystalline micropore width", weighting="reviewed microscopy observations", method="SEM/petrography review", provenance="abstract/review synthesis", counted="no"),
    obs("OBS-024", "LIT-015", "carbonate", "micritic limestone", "secondary microporosity", "multiple Phanerozoic settings", "multiple/unknown", "review", geometry="microvug / secondary pore", size_max=64, convention="secondary micropore diameter upper scale", weighting="review synthesis", method="SEM/petrography review", provenance="abstract/review synthesis", counted="no"),
    obs("OBS-025", "LIT-018", "basalt/volcanic rock", "Port Fairy basalt", "natural block; lab-cut unreacted half-core", "Bambstone Bluestone quarry, Victoria", "approximate locality", 1, total="9.75 study-core CT context; 12 separate bulk core", geometry="pore body", size_central=54.42, convention="median equivalent diameter", weighting="resolved object count", method="micro-CT", window="14.99 um voxel", provenance="paper porosity context; Mendeley unreacted-ungrooved table; M3 audit", note="Porosity values are contextual and not exact scale factors for the half-core distribution."),
    obs("OBS-026", "LIT-019", "basalt/volcanic rock", "scoria, lava flows, diktytaxitic and micropore basalt", "natural vesicular basalts", "central Oregon volcanic settings", "regional", "five sample types; specimen n not recovered", geometry="vesicle body", convention="mean bubble radius; source-specific image analysis", weighting="image/object", method="image analysis + gas permeability/porosity", provenance="paper Figure 2 and sample-type description", counted="no", note="Vesicles are bodies; permeability is governed by much smaller inter-vesicle apertures."),
    obs("OBS-027", "LIT-019", "basalt/volcanic rock", "same vesicular basalts", "natural vesicular basalts", "central Oregon volcanic settings", "regional", "same suite", geometry="vesicle connecting aperture", convention="aperture radius typically order 10 times smaller than mean bubble radius", weighting="model/image comparison", method="porosity-permeability + image analysis", provenance="abstract and discussion", counted="no"),
    obs("OBS-028", "LIT-020", "basalt/volcanic rock", "Kilauea Iki basalt", "natural drill core; dense to vesicular", "Kilauea Iki, Hawaii", "exact volcanic setting", 8, total="7.32-40.8 helium-accessible in displayed table", effective="4.71-38.9 water-accessible in displayed table", geometry="vesicle/crack porosity", convention="bulk accessible porosity; no PSD", method="helium and water saturation", depth_state="0.99-7.39 m core depths in Table 1", provenance="USGS Professional Paper 1123-B Table 1", note="State varies strongly with lava-lake depth and vesicularity."),
    obs("OBS-029", "LIT-021", "basalt/volcanic rock", "ISL26 alkali basalt", "fresh natural road outcrop", "Reykjanes Peninsula, Iceland", "regional", 1, total=7.93, geometry="crack / microfracture", size_central=0.1, convention="MIP bimodal peak near 0.1 um; source labels cracks", weighting="intruded porosity; about 1 percentage point", method="MIP", window="Autopore IV 9500; entrance radius derived by Washburn law", depth_state="0-200 MPa hydrostatic experiments after characterization", provenance="sample description and Figure 1"),
    obs("OBS-030", "LIT-021", "basalt/volcanic rock", "ISL26 alkali basalt", "fresh natural road outcrop", "Reykjanes Peninsula, Iceland", "regional", 1, total=7.93, geometry="equant pore", size_central=100, convention="MIP bimodal peak near 100 um; source labels equant pores", weighting="intruded porosity; about 7 percentage points", method="MIP + SEM", provenance="Figure 1", counted="no"),
    obs("OBS-031", "LIT-022", "basalt/volcanic rock", "Mt Etna basalt", "natural volcanic rock", "Mt Etna, Sicily", "regional", 1, total=4.0, effective=4.0, geometry="pore throat / entry constriction", size_central=0.17, convention="mean MIP pore-throat radius; 65% of porosity is accessed through radii below 0.5 um", weighting="intruded connected pore volume", method="MIP + pressure-dependent permeability", provenance="sample table, Figure 4b and discussion"),
    obs("OBS-032", "LIT-023", "granite/granitoid", "Lipnice granite", "fresh matrix through fractured/altered/gouge states", "MEL-5 borehole, Melechov pluton", "exact borehole", 21, total="0.50-6.53 connected MIP; median 2.01", geometry="pore throat / MIP entry", size_min=0.008, size_max=309, convention="source pipe-pore/crack-equivalent entry diameter; not body diameter", weighting="incremental intruded porosity", method="MIP", window="paper about 0.005-300 um", depth_state="one 150 m borehole; state deliberately heterogeneous", provenance="paper sections 3.3-4.4, Figs 3 and 11; PANGAEA.898001", note="Fresh specimen 11 is 0.50%; elevated porosity occurs in fracture/alteration/cavity/gouge states."),
    obs("OBS-033", "LIT-024", "granite/granitoid", "Westerly granite", "intact crystalline rock", "Westerly, Rhode Island", "approximate locality", 1, geometry="microcrack aperture", convention="stereological crack-aperture distribution", weighting="crack surface area per bulk volume", method="quantitative stereology", provenance="paper crack-aperture statistics and power-law fits", note="Microcracks are not generic matrix pore bodies."),
    obs("OBS-034", "LIT-025", "granite/granitoid", "Westerly granite", "untreated versus thermally cracked", "Westerly, Rhode Island", "approximate locality", "one parent material; thermal series", total="3.2 after 600 C treatment", geometry="thermal microcrack", convention="BSE fracture density/length/aperture", weighting="image fracture metrics", method="BSE microscopy + porosity", provenance="paper sample description and fracture table", counted="no", note="Thermally induced 3.2% porosity is a laboratory-damaged state, not intact granite baseline."),
    obs("OBS-035", "LIT-026", "granite/granitoid", "Mondim and Pedras granites", "reference and contaminated stone", "northern Portugal quarry stones", "regional", "specimen n not recovered", geometry="matrix pore / microfracture classes", convention="MIP pore diameter classes; >10 um explicitly air void/microfracture", weighting="intruded volume", method="MIP + water transport", provenance="Table 4 and pore-size-distribution figure", counted="no"),
    obs("OBS-036", "LIT-028", "gabbro/mafic crystalline", "Atlantis Massif mafic cores", "natural drilled cores; variably altered/fractured", "Atlantis Massif, five IODP boreholes", "exact boreholes", 4, total="0.9-2.9", geometry="connectivity/transport only", convention="no pore-size distribution", method="wet-dry bulk porosity + pressure-series transport", depth_state="confining-pressure series", provenance="paper Table 1; PANGAEA.873535/873533/873534"),
    obs("OBS-037", "LIT-029", "gabbro/mafic crystalline", "Hole 735B oceanic gabbro", "fresh through altered/fractured borehole zones", "ODP Hole 735B, Southwest Indian Ridge", "exact borehole", "continuous logs + core checks", total="core/log means ~1.5-3.4 by interval", geometry="fracture network", convention="borehole fractures; no matrix PSD", weighting="depth/log interval", method="neutron/density/televiewer logs + packer tests", depth_state="23-500 mbsf", provenance="Table 2, Figures 3-6", counted="no", note="Porosity-log peaks may be fracture porosity unsampled by core; hydrous-mineral correction is essential."),
    obs("OBS-038", "LIT-030", "gabbro/mafic crystalline", "Hole 735B gabbros", "natural core", "ODP Hole 735B, Southwest Indian Ridge", "exact borehole", 29, geometry="crack/microcrack network", convention="electrical formation factor indicates cracks/microcracks; no PSD", method="porosity + electrical conduction", provenance="paper sample count and electrical-conduction interpretation"),
    obs("OBS-039", "LIT-032", "gabbro/mafic crystalline", "Hess Deep gabbroic rock", "natural oceanic core", "IODP Hole U1415, Hess Deep", "exact borehole", "at least 3 discrete physical-property specimens", geometry="bulk pore space", convention="porosity/density only; no PSD", method="wet-dry volume/density and core physical properties", provenance="Expedition 345 site chapters and physical-properties tables", note="A separate oceanic-crust locality from Atlantis Massif and Hole 735B."),
    obs("OBS-040", "LIT-028", "serpentinite/ultramafic", "Atlantis Massif serpentinised ultramafic cores", "natural drilled cores; fracture-sensitive", "Atlantis Massif, three IODP boreholes", "exact boreholes", 4, total="2.6-12.8", geometry="connectivity/transport only", convention="no pore-size distribution", method="wet-dry bulk porosity + pressure-series permeability/resistivity", provenance="paper Table 1; PANGAEA.873535/873533/873534", note="Highest values were interpreted as stress-release/fracture influenced."),
    obs("OBS-041", "LIT-033", "serpentinite/ultramafic", "partially serpentinised peridotite", "natural core/outcrop", "Atlantis Massif U1309D and Duluth Complex", "exact borehole + regional", 2, geometry="intrinsic nanopore plus reaction fracture", convention="(U)SANS pore-size distribution; components must remain distinct", weighting="scattering-volume/surface model", method="SANS/USANS", provenance="paper methods and pore-size/surface-area distributions", note="Two geological settings; not a universal serpentinite curve."),
    obs("OBS-042", "LIT-034", "serpentinite/ultramafic", "lizardite serpentinite veins", "natural partially serpentinised peridotite/dunite", "ODP Site 1274 MAR and Roragen, Norway", "exact core + regional", 2, total="FIB volumes 0.2-0.7; TEM foils 1-3; local brucite interface 12+/-4", geometry="grain-boundary / reaction nanoporosity", size_min=0.001, size_max=0.1, convention="direct pore diameter; dominant <100 nm, prevalent <10 nm", weighting="image-object/area/volume depending panel", method="FIB-SEM nanotomography + TEM", window="~3 nm SEM pixels; 0.5 nm TEM and 5 nm FIB-SEM histogram bins", provenance="Methods; Figs 2-5 and 9", note="Highly local analysed volumes; the 12% interface is not whole-rock porosity."),
    obs("OBS-043", "LIT-035", "serpentinite/ultramafic", "low-temperature serpentinites", "natural accretionary-prism and dredged samples", "Mineoka Belt, Parece Vela, Mariana and Tonga trenches", "regional/multiple", "specimen n in Table 1/S1-S2", total="10.5-24.7 for dredged specimens", geometry="bulk pore space / fracture-sensitive transport", convention="gas porosity; no PSD", method="gas-expansion porosity + pressure-dependent permeability", depth_state="5-100 MPa confining pressure", provenance="Table 1 and Supplementary Tables S1-S2", counted="no", note="Large bulk porosity does not yield proportionally high permeability; transport porosity is lower."),
    obs("OBS-044", "LIT-036", "serpentinite/ultramafic", "serpentinite mud-volcano cores", "natural but special mud-volcano material", "three Mariana forearc mud volcanoes", "regional/multiple", 7, total="37-51", geometry="bulk pore space / transport", convention="bulk porosity; no PSD", method="wet-dry/gas porosity + permeability/friction", depth_state="19.6-197.9 mbsf", provenance="IODP data report abstract and tables", note="Unconsolidated/saponitic serpentinite mud is not intact serpentinite matrix."),
    obs("OBS-045", "LIT-024", "metamorphic rock", "Rutland quartzite", "intact crystalline metamorphic rock", "Rutland, Vermont", "approximate locality", 1, geometry="microcrack aperture", convention="stereological crack-aperture distribution", weighting="crack surface area per bulk volume", method="quantitative stereology", provenance="paper crack-aperture statistics", note="Pore microstructure differs from Westerly granite despite similar crack porosity/compressibility."),
    obs("OBS-046", "LIT-037", "metamorphic rock", "chlorite/mica schist and granitic mylonite", "natural borehole reservoir; weathering/structural microfractures", "LT1/LT2 wells, Songliao Basin", "regional", 8, total="schist mean 1.46; mylonite mean 1.00", geometry="matrix pore", size_min=0.002, size_max=1, convention="HPMI/gas-adsorption pore diameter ranges", weighting="intruded/adsorbed pore volume", method="HPMI + N2 adsorption/DFT", window="DFT <100 nm; HPMI to micron scale", provenance="Tables 4-6; Figs 5-8", note=">60% of schist pore volume <0.1 um; mylonite chiefly 0.05-1 um."),
    obs("OBS-047", "LIT-037", "metamorphic rock", "same schist/mylonite suite", "natural borehole reservoir", "LT1/LT2 wells, Songliao Basin", "regional", 8, geometry="structural/weathering microfracture", convention="microscopy classification; not pooled with matrix PSD", method="thin section/SEM", provenance="Table 3 and Figure 3", counted="no"),
    obs("OBS-048", "LIT-038", "metamorphic rock", "quartz-mica and biotite schists", "natural low-grade metamorphic rock", "Nathpa-Jhakri, Himalaya, India", "approximate locality", 3, geometry="matrix pore / MIP entry", convention="MIP pore-size distribution", weighting="intruded volume", method="MIP", provenance="paper methods/results", note="Three varieties include quartz-veined material; states must not be pooled."),
    obs("OBS-049", "LIT-039", "metamorphic rock", "Carrara and comparison marbles", "natural stone; thermal-weathering series", "Carrara, Italy and comparison quarries", "regional/multiple", "specimen n not recovered", geometry="grain-boundary microcrack", convention="thermal-expansion microcracks; not generic matrix pore bodies", weighting="image/porosity", method="dilatometry + microscopy + petrophysics", provenance="paper marble tables and thermal-cycling figures", counted="no", note="Thermal damage is a sample-state sensitivity, not an intact marble baseline."),
]


LOCATIONS = [
    ("LOC-001", "Alameda County beach", "LIT-003", "unconsolidated sand/sediment", 37.85111, -122.30000, "exact", "natural", "reported 37 51 04 N, 122 18 00 W"),
    ("LOC-002", "Blake Ridge ODP Leg 164", "LIT-004", "unconsolidated sand/sediment", 31.70, -75.50, "regional centroid", "natural", "regional expedition setting; not a hole coordinate"),
    ("LOC-003", "Sellafield BH13B", "LIT-007", "sandstone", 54.38815, -3.47205, "exact borehole", "natural", "published British National Grid converted at map scale"),
    ("LOC-004", "Longdong, Ordos Basin", "LIT-008", "sandstone", 36.0, 107.5, "regional centroid", "natural", "Qingyang-Zhenjing-Huachi study area"),
    ("LOC-005", "SE Ordos Basin", "LIT-009", "sandstone", 36.6, 109.4, "regional centroid", "natural", "Yanchang Formation study region"),
    ("LOC-006", "West Trenton NAWC", "LIT-011", "mudstone/shale", 40.26, -74.81, "approximate locality", "natural", "former Naval Air Warfare Center; exact boreholes not geocoded here"),
    ("LOC-007", "Barnett Shale region", "LIT-012", "mudstone/shale", 32.7, -97.3, "regional centroid", "natural", "one of several formations in Loucks et al."),
    ("LOC-008", "Woodford Shale region", "LIT-012|LIT-001", "mudstone/shale", 35.0, -97.0, "regional centroid", "natural", "regional benchmark marker"),
    ("LOC-009", "Mancos Shale region", "LIT-001|LIT-013", "mudstone/shale", 37.2, -108.5, "regional centroid", "natural", "regional benchmark marker"),
    ("LOC-010", "Bakken region", "LIT-001|LIT-013", "mudstone/shale", 48.0, -103.0, "regional centroid", "natural", "regional benchmark marker"),
    ("LOC-011", "Nansha Islands", "LIT-014", "carbonate", 10.0, 114.0, "regional centroid", "natural", "South China Sea reef-carbonate study region"),
    ("LOC-012", "Austin Chalk region", "LIT-001", "carbonate", 30.2, -97.5, "regional centroid", "natural", "Park S2 source formation"),
    ("LOC-013", "Mount Gambier", "LIT-001", "carbonate", -37.83, 140.78, "approximate locality", "natural", "Park S2 carbonate source"),
    ("LOC-014", "Port Fairy quarry", "LIT-018", "basalt/volcanic rock", -38.38, 142.24, "approximate locality", "natural", "Bambstone Bluestone quarry region"),
    ("LOC-015", "Central Oregon basalt fields", "LIT-019", "basalt/volcanic rock", 44.3, -121.3, "regional centroid", "natural", "scoria/lava sample region"),
    ("LOC-016", "Kilauea Iki", "LIT-020", "basalt/volcanic rock", 19.42, -155.28, "exact volcanic setting", "natural", "Kilauea Iki drill core"),
    ("LOC-017", "Reykjanes Peninsula", "LIT-021", "basalt/volcanic rock", 63.9, -22.5, "regional centroid", "natural", "road-outcrop ISL26 block"),
    ("LOC-034", "Mt Etna", "LIT-022", "basalt/volcanic rock", 37.75, 15.00, "regional centroid", "natural", "volcanic-edifice centroid; not a specimen coordinate"),
    ("LOC-018", "Lipnice MEL-5", "LIT-023", "granite/granitoid", 49.62072, 15.41032, "exact borehole", "natural", "published borehole coordinate"),
    ("LOC-019", "Westerly granite", "LIT-024|LIT-025", "granite/granitoid", 41.38, -71.83, "approximate locality", "natural", "reference-stone locality, not a quarry coordinate"),
    ("LOC-020", "Northern Portugal granites", "LIT-026", "granite/granitoid", 41.3, -7.9, "regional centroid", "natural", "Mondim/Pedras stone region"),
    ("LOC-021", "Atlantis Massif", "LIT-028|LIT-033", "gabbro/mafic crystalline|serpentinite/ultramafic", 30.14, -42.12, "exact drilling region", "natural", "multiple IODP boreholes; one mixed mafic-ultramafic massif setting"),
    ("LOC-022", "ODP Hole 735B", "LIT-029|LIT-030|LIT-031", "gabbro/mafic crystalline", -32.72, 57.27, "exact borehole", "natural", "Southwest Indian Ridge / Atlantis II Fracture Zone"),
    ("LOC-023", "Hess Deep U1415", "LIT-032", "gabbro/mafic crystalline", 2.25, -101.55, "exact drilling region", "natural", "IODP Expedition 345"),
    ("LOC-024", "Duluth Complex", "LIT-033", "serpentinite/ultramafic", 47.5, -91.5, "regional centroid", "natural", "olivine-rich outcrop setting"),
    ("LOC-025", "ODP Site 1274", "LIT-034", "serpentinite/ultramafic", 15.65, -46.68, "exact drilling region", "natural", "31 km north of 15 20 N fracture zone"),
    ("LOC-026", "Roragen ultramafic complex", "LIT-034", "serpentinite/ultramafic", 62.6, 11.9, "approximate locality", "natural", "Norwegian onshore complex"),
    ("LOC-027", "Mineoka Belt", "LIT-035", "serpentinite/ultramafic", 35.1, 140.1, "regional centroid", "natural", "accretionary-prism serpentinite"),
    ("LOC-028", "Parece Vela Basin", "LIT-035", "serpentinite/ultramafic", 17.0, 139.0, "regional centroid", "natural", "dredged serpentinite setting"),
    ("LOC-029", "Mariana forearc mud volcanoes", "LIT-036", "serpentinite/ultramafic", 18.0, 147.0, "regional centroid", "natural special state", "three mud volcanoes; plotted once as a regional setting"),
    ("LOC-030", "Rutland quartzite", "LIT-024", "metamorphic rock", 43.61, -72.97, "approximate locality", "natural", "reference-stone locality"),
    ("LOC-031", "Songliao Basin LT wells", "LIT-037", "metamorphic rock", 45.5, 124.5, "regional centroid", "natural", "central paleo-uplift belt"),
    ("LOC-032", "Nathpa-Jhakri", "LIT-038", "metamorphic rock", 31.56, 78.0, "approximate locality", "natural", "Himalayan hydroelectric project setting"),
    ("LOC-033", "Carrara marble district", "LIT-039", "metamorphic rock", 44.08, 10.10, "approximate locality", "natural", "quarry district; comparison marbles not separately mapped"),
]


ENVELOPES = [
    ("unconsolidated sand/sediment", "intact/natural or depositional fabric", 25, 60, "", "", 0.1, 500, 0.01, 200, "LIT-001|LIT-003|LIT-004|LIT-005", "Very broad soil/sediment domain; clay, silt and sand cannot be treated as one universal PSD."),
    ("unconsolidated sand/sediment", "laboratory/remoulded/packed", 25, 50, "", "", 0.1, 500, 0.01, 200, "LIT-001|LIT-002|LIT-003", "Preparation history changes fabric and coordination."),
    ("sandstone", "intact matrix, conventional through tight", 1, 30, "", "", 0.002, 200, 0.003, 10, "LIT-001|LIT-006|LIT-007|LIT-008|LIT-009", "Includes nanometre clay pores, intergranular/dissolution bodies and MIP entry throats; method labels are essential."),
    ("mudstone/shale", "intact matrix", 0.1, 20, "", "", 0.001, 1, 0.002, 0.2, "LIT-001|LIT-010|LIT-011|LIT-012|LIT-013", "Organic, clay and mineral pores dominate nano/submicron scales; cracks are separate."),
    ("mudstone/shale", "weathered/fractured/shallow", 1, 30, "", "", 0.001, 10, 0.002, 10, "LIT-011|LIT-012", "Fractures control flow but must not be folded into matrix PSD."),
    ("carbonate", "intact matrix", 0.1, 35, "", "", 0.01, 100, 0.01, 100, "LIT-001|LIT-014|LIT-015|LIT-016|LIT-017", "Microporosity, interparticle and moldic systems coexist."),
    ("carbonate", "vuggy/dissolution/weathered", 5, 50, "", "", 10, 10000, 0.1, 1000, "LIT-015|LIT-016|LIT-017", "Vugs are bodies and do not imply equally large connecting throats."),
    ("basalt/volcanic rock", "dense/intact lava matrix", 0.1, 10, "", "", 0.05, 300, 0.05, 10, "LIT-018|LIT-020|LIT-021|LIT-022", "Crack and equant-pore modes may coexist."),
    ("basalt/volcanic rock", "vesicular/scoria/brecciated", 10, 70, "", "", 10, 10000, 0.1, 100, "LIT-019|LIT-020", "Large vesicles can remain poorly connected through small apertures."),
    ("granite/granitoid", "fresh/intact crystalline matrix", 0.1, 2, "", "", 0.005, 10, 0.005, 10, "LIT-023|LIT-024|LIT-027", "Mostly grain-boundary/intragranular microcracks and cleavage porosity."),
    ("granite/granitoid", "altered/weathered/fractured/gouge", 0.5, 15, "", "", 0.01, 1000, 0.01, 1000, "LIT-023|LIT-025|LIT-026|LIT-027", "State-specific extension; not an intact-matrix reference."),
    ("gabbro/mafic crystalline", "fresh/intact matrix", 0.1, 3, "", "", 0.005, 10, 0.005, 10, "LIT-028|LIT-029|LIT-030|LIT-031|LIT-032", "Core-scale porosity is low; cracks/fractures can dominate transport."),
    ("gabbro/mafic crystalline", "altered/fractured", 0.5, 10, "", "", 0.01, 100, 0.01, 100, "LIT-028|LIT-029|LIT-030", "Borehole log peaks and hydraulic permeability can be fracture dominated."),
    ("serpentinite/ultramafic", "intact/moderately serpentinised", 0.1, 5, "", "", 0.001, 0.1, 0.001, 0.1, "LIT-028|LIT-033|LIT-034", "Intrinsic lizardite/brucite porosity is predominantly nanoscale; local interface porosity is not whole-rock porosity."),
    ("serpentinite/ultramafic", "fractured/weathered/dredged", 2, 25, "", "", 0.001, 100, 0.001, 100, "LIT-028|LIT-035", "Bulk and transport porosity diverge strongly."),
    ("serpentinite/ultramafic", "mud-volcano/saponitic special state", 35, 55, "", "", "", "", "", "", "LIT-036", "Not representative of coherent serpentinite matrix."),
    ("metamorphic rock", "dense intact quartzite/marble/gneiss/schist", 0.1, 3, "", "", 0.002, 1, 0.002, 10, "LIT-024|LIT-037|LIT-038|LIT-039|LIT-040", "Protolith and fabric matter; matrix pores and grain-boundary cracks remain distinct."),
    ("metamorphic rock", "weathered/foliated/thermally cracked", 1, 20, "", "", 0.01, 100, 0.01, 1000, "LIT-037|LIT-038|LIT-039|LIT-040", "Structural/weathering/thermal microcracks are special states."),
]


# Broad envelopes above retain the historical, compact matrix/body and
# throat/constriction columns.  This second table is the reporting-grade layer:
# one row has one void class and one material state.  It is deliberately not a
# universal PSD or a conversion between methods.
VOID_ENVELOPES = [
    ("unconsolidated sand/sediment", "intact/natural depositional fabric", "intergranular pore", 0.1, 500, "um", "LIT-001|LIT-003|LIT-004", "Fitted or image-scale pore domains; grain and depositional fabric vary."),
    ("unconsolidated sand/sediment", "intact/natural depositional fabric", "pore throat / entry constriction", 0.01, 200, "um", "LIT-001|LIT-003|LIT-005", "Do not equate grain coordination with a throat-size distribution."),
    ("unconsolidated sand/sediment", "laboratory/remoulded/packed", "intergranular pore", 0.1, 500, "um", "LIT-001|LIT-002|LIT-003", "Preparation changes fabric; not a natural-site envelope."),
    ("unconsolidated sand/sediment", "laboratory/remoulded/packed", "pore throat / entry constriction", 0.01, 200, "um", "LIT-001|LIT-002|LIT-003", "Resolved network values remain voxel-conditioned."),
    ("sandstone", "intact matrix", "matrix/intergranular pore", 0.002, 200, "um", "LIT-001|LIT-006|LIT-007|LIT-008|LIT-009", "Includes clay-associated and intergranular domains; method labels remain essential."),
    ("sandstone", "intact matrix", "pore throat / entry constriction", 0.003, 10, "um", "LIT-001|LIT-008|LIT-009", "MIP/gas-adsorption entry or throat scale; not a CT body radius."),
    ("mudstone/shale", "intact matrix", "matrix pore", 0.001, 1, "um", "LIT-001|LIT-010|LIT-011|LIT-012|LIT-013", "Organic, clay and mineral pores; modelled domains are separately labelled."),
    ("mudstone/shale", "intact matrix", "pore throat / entry constriction", 0.002, 0.2, "um", "LIT-001|LIT-011|LIT-013", "Method-window-dependent nano/submicrometre entry scale."),
    ("mudstone/shale", "weathered/fractured/shallow", "fracture-associated void", 0.002, 10, "um", "LIT-011|LIT-012", "Fracture flow is not matrix-pore evidence."),
    ("carbonate", "intact matrix", "matrix intercrystalline pore", 0.01, 10, "um", "LIT-001|LIT-015|LIT-016", "Micritic/intercrystalline matrix domain."),
    ("carbonate", "intact matrix", "pore body", 0.01, 100, "um", "LIT-001|LIT-014|LIT-015|LIT-017", "Interparticle and moldic bodies remain distinct from their throats."),
    ("carbonate", "intact matrix", "pore throat / entry constriction", 0.01, 100, "um", "LIT-014|LIT-016|LIT-017", "Broad method-conditioned throat domain; the CT layer is coarse."),
    ("carbonate", "vuggy/dissolution/weathered", "vug / dissolution cavity", 10, 10000, "um", "LIT-015|LIT-016|LIT-017", "Large vugs do not imply equally large connecting throats."),
    ("carbonate", "vuggy/dissolution/weathered", "pore throat / entry constriction", 0.1, 1000, "um", "LIT-015|LIT-016|LIT-017", "Separate from vug-body scale."),
    ("basalt/volcanic rock", "dense/intact lava matrix", "equant pore body", 0.05, 300, "um", "LIT-018|LIT-020|LIT-021", "Dense basalt may contain both equant pores and crack modes."),
    ("basalt/volcanic rock", "dense/intact lava matrix", "microcrack / crack", 0.05, 10, "um", "LIT-021|LIT-022", "Crack-associated MIP mode; not an equant-pore body."),
    ("basalt/volcanic rock", "vesicular/scoria/brecciated", "vesicle", 10, 10000, "um", "LIT-019|LIT-020", "Vesicle-body state is not dense matrix."),
    ("basalt/volcanic rock", "vesicular/scoria/brecciated", "pore throat / connecting aperture", 0.1, 100, "um", "LIT-019|LIT-022", "Connecting apertures can be much smaller than vesicles."),
    ("granite/granitoid", "fresh/intact crystalline matrix", "grain-boundary / intragranular pore", 0.005, 10, "um", "LIT-023|LIT-027", "Matrix-scale porosity; do not merge with open fractures."),
    ("granite/granitoid", "fresh/intact crystalline matrix", "microcrack / crack", 0.005, 10, "um", "LIT-023|LIT-024", "Stereological/MIP crack-related domain; not a body distribution."),
    ("granite/granitoid", "altered/weathered/fractured/gouge", "fracture-associated void", 0.01, 1000, "um", "LIT-023|LIT-025|LIT-026|LIT-027", "Special state, not a fresh-granite reference."),
    ("gabbro/mafic crystalline", "fresh/intact matrix", "grain-boundary / intragranular pore", 0.005, 10, "um", "LIT-028|LIT-029|LIT-030|LIT-032", "Low-porosity core-scale material; direct PSD evidence is sparse."),
    ("gabbro/mafic crystalline", "altered/fractured", "fracture-associated void", 0.01, 100, "um", "LIT-028|LIT-029|LIT-030", "Fracture-controlled transport is separate from matrix porosity."),
    ("serpentinite/ultramafic", "intact/moderately serpentinised", "grain-boundary / reaction nanoporosity", 0.001, 0.1, "um", "LIT-033|LIT-034", "Intrinsic lizardite/brucite nanoporosity; local interface values are not whole rock."),
    ("serpentinite/ultramafic", "fractured/weathered/dredged", "fracture-associated void", 0.001, 100, "um", "LIT-028|LIT-035", "Bulk and transport porosity can diverge strongly."),
    ("metamorphic rock", "dense intact quartzite/marble/gneiss/schist", "matrix pore", 0.002, 1, "um", "LIT-037|LIT-038|LIT-040", "Protolith and metamorphic fabric remain explicit."),
    ("metamorphic rock", "dense intact quartzite/marble/gneiss/schist", "grain-boundary pore / microcrack", 0.002, 10, "um", "LIT-024|LIT-037|LIT-039", "Grain-boundary cracks are not generic matrix pores."),
    ("metamorphic rock", "weathered/foliated/thermally cracked", "fracture-associated void", 0.01, 1000, "um", "LIT-037|LIT-038|LIT-039|LIT-040", "Structural/weathering/thermal special state."),
]


M3_AUDIT = [
    ("M3-001", "granite/granitoid", "special geological state", "Fresh Lipnice (0.50% connected MIP porosity) fits the 0.1-2% intact envelope; the 0.50-6.53% 21-specimen suite deliberately mixes matrix, altered, fracture-surface, cavity and gouge states.", "Report the seven matrix-reference specimens separately; never call 21 specimens 21 localities."),
    ("M3-002", "sandstone", "strongly resolution-conditioned|likely biased toward large resolved voids", "Fontainebleau/Berea bulk porosities are plausible, but 0.74 um CT/PNM retains only the segmented connected population and is coarser than many Park/Cao nanometre-submicrometre modes.", "Keep resolved-network results; label all size/fit statements conditional on resolved throats and bodies."),
    ("M3-RLD-003", "carbonate", "strongly resolution-conditioned|likely biased toward large resolved voids|requires further investigation", "Porosities 7.35-23.41% lie within carbonate envelopes; body/throat radii around 54-139 um are shifted high by 61.75 um voxels. Carbonate A workbook and paper throat counts/maxima disagree.", "Use as macropore-network evidence only; retain discrepancy flag and do not infer a full carbonate PSD."),
    ("M3-RLD-003-S", "sandstone", "strongly resolution-conditioned|likely biased toward large resolved voids", "Sandstone S has low CT porosity (1.06%) and 30.45 um voxels; it cannot see the tight-sandstone throat domain documented by MIP/adsorption studies.", "Treat as resolved macropore-network example, not a representative sandstone distribution."),
    ("M3-005", "basalt/volcanic rock", "special geological state|strongly resolution-conditioned|likely biased toward large resolved voids", "The 9.75/12% contextual porosities sit at the dense/vesicular boundary, while 14.99 um CT resolves only large bodies. Exact table-specific bulk porosity is unavailable.", "Relabel as a resolved body population from one half-core; do not scale to whole-rock pore volume."),
    ("M3-RLD-004", "sandstone", "broadly representative / within expected range|strongly resolution-conditioned", "Wilmslow total/connected porosity 9.77-26.42% is plausible; 2.686-2.841 um voxels omit finer pores, and all-object files mix connected/disconnected objects.", "Preserve seven depths as within-borehole variation; connected transit requires connected-object filtering."),
    ("M3-023", "mudstone/shale", "requires further investigation|special analytical construct", "W23 spans shale-relevant scales but is a modelled pore-cluster/domain radius with microfracture connectivity; J24 lacks a resolved physical R unit.", "Keep as model evidence, not direct matrix-body or throat measurement; exclude J24 from size statistics."),
    ("M3-024", "unconsolidated sand/sediment", "broadly representative / within expected range|strongly resolution-conditioned|laboratory standard", "F42A porosity 33% is plausible for a pack, but it is not natural depositional replication and 9.996 um CT censors small throats.", "Keep as topology/connectivity standard; compare natural beach/sediment fabric separately."),
    ("M3-025-mafic", "gabbro/mafic crystalline", "broadly representative / within expected range", "Atlantis mafic bulk porosity 0.9-2.9% matches low-porosity intact/altered oceanic gabbro envelopes; pressure transport is fracture sensitive.", "Retain as connectivity/transport-only evidence."),
    ("M3-025-ultramafic", "serpentinite/ultramafic", "special geological state|broadly representative / within expected range", "Atlantis ultramafic bulk porosity 2.6-12.8% spans intact-to-fractured/serpentinised states; high values are stress-release/fracture influenced and do not contradict nanoscale intrinsic porosity.", "Separate bulk fracture-sensitive porosity from Chogani/Tutolo intrinsic nanopores; no size curve is present."),
]


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rows[0], dict):
        fieldnames = list(rows[0])
        records = rows
    else:
        raise TypeError("Rows must be dictionaries")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def source_counts():
    return Counter(c for s in SOURCES for c in s["lithology_classes"].split("|"))


def make_coverage():
    counts = source_counts()
    mapped = Counter(c for row in LOCATIONS if row[7].startswith("natural") for c in row[3].split("|"))
    primary_min = Counter()
    for row in OBSERVATIONS:
        if row["count_in_primary_specimen_minimum"] != "yes":
            continue
        try:
            primary_min[row["lithology"]] += int(row["physical_specimens"])
        except (ValueError, TypeError):
            pass
    park = {"unconsolidated sand/sediment": 39, "sandstone": 17,
            "mudstone/shale": 4, "carbonate": 23}
    rows = []
    for lith in LITHOLOGIES:
        rows.append({
            "lithology": lith,
            "independent_literature_sources": counts[lith],
            "mapped_natural_settings": mapped[lith],
            "documented_primary_physical_specimens_minimum": primary_min[lith],
            "park_santamarina_benchmark_groups_not_added_to_specimen_total": park.get(lith, 0),
            "counting_note": "Conservative minimum: review/benchmark rows, duplicate geometry rows, unspecified n, continuous logs and repeated studies of the same specimens are excluded.",
        })
    return rows


def make_envelopes():
    keys = ["lithology", "state_class", "total_porosity_min_percent", "total_porosity_max_percent",
            "effective_porosity_min_percent", "effective_porosity_max_percent",
            "pore_body_or_matrix_scale_min_um", "pore_body_or_matrix_scale_max_um",
            "throat_or_constriction_scale_min_um", "throat_or_constriction_scale_max_um",
            "supporting_source_ids", "scope_note"]
    return [dict(zip(keys, row)) for row in ENVELOPES]


def make_void_envelopes():
    keys = ["lithology", "state_class", "void_class", "size_min_um", "size_max_um",
            "size_unit", "supporting_source_ids", "scope_note"]
    return [dict(zip(keys, row)) for row in VOID_ENVELOPES]


def make_locations():
    keys = ["location_id", "location_name", "source_ids", "lithology", "latitude", "longitude",
            "location_precision", "material_setting", "coordinate_provenance"]
    return [dict(zip(keys, row)) for row in LOCATIONS]


def make_m3_audit():
    keys = ["m3_source_id", "lithology", "atlas_assessment_flags", "evidence", "recommended_resource_treatment"]
    return [dict(zip(keys, row)) for row in M3_AUDIT]


def make_porosity_summary(coverage):
    """Report only statistics the curated source rows can honestly support.

    Most atlas papers report sample ranges or heterogeneous groups rather than
    a common list of individual porosities.  We preserve those reported ranges
    and leave cross-source quartiles blank rather than treating interval bounds
    or millions of image objects as independent specimens.
    """
    envelope_by_lith = defaultdict(list)
    for row in make_envelopes():
        if row["total_porosity_min_percent"] != "":
            envelope_by_lith[row["lithology"]].append(row)
    rows = []
    coverage_by_lith = {r["lithology"]: r for r in coverage}
    for lith in LITHOLOGIES:
        source_rows = [r for r in OBSERVATIONS if r["lithology"] == lith]
        numeric_total = []
        numeric_effective = []
        seen_total, seen_effective = set(), set()
        for r in source_rows:
            key = (r["source_id"], r["subtype_or_state"])
            try:
                value = float(r["total_porosity_percent"])
                if key not in seen_total:
                    numeric_total.append(value); seen_total.add(key)
            except ValueError:
                pass
            try:
                value = float(r["effective_connected_porosity_percent"])
                if key not in seen_effective:
                    numeric_effective.append(value); seen_effective.add(key)
            except ValueError:
                pass
        reported = envelope_by_lith[lith]
        total_lo = min(float(r["total_porosity_min_percent"]) for r in reported)
        total_hi = max(float(r["total_porosity_max_percent"]) for r in reported)
        def stats(values):
            # At least four independent scalar source groups are required for
            # an unweighted quartile; all other material remains range-only.
            if len(values) < 4:
                return ("", "", "")
            a = np.asarray(values)
            return (f"{np.percentile(a, 25):.6g}", f"{np.median(a):.6g}", f"{np.percentile(a, 75):.6g}")
        tq1, tmed, tq3 = stats(numeric_total)
        eq1, emed, eq3 = stats(numeric_effective)
        rows.append({
            "lithology": lith,
            "independent_literature_sources": coverage_by_lith[lith]["independent_literature_sources"],
            "mapped_natural_settings": coverage_by_lith[lith]["mapped_natural_settings"],
            "conservative_primary_specimens_minimum": coverage_by_lith[lith]["documented_primary_physical_specimens_minimum"],
            "total_porosity_scalar_source_groups": len(numeric_total),
            "total_porosity_q1_percent": tq1, "total_porosity_median_percent": tmed, "total_porosity_q3_percent": tq3,
            "total_porosity_state_stratified_reference_min_percent": f"{total_lo:.6g}",
            "total_porosity_state_stratified_reference_max_percent": f"{total_hi:.6g}",
            "effective_connected_scalar_source_groups": len(numeric_effective),
            "effective_connected_q1_percent": eq1, "effective_connected_median_percent": emed, "effective_connected_q3_percent": eq3,
            "statistical_interpretation": "Unweighted quartiles are blank when fewer than four independent scalar source groups are available; source-reported intervals, different states and non-equivalent methods are not converted into pseudo-observations.",
        })
    return rows


def make_plots(coverage, locations, envelopes, void_envelopes):
    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 13, "axes.labelsize": 11,
                         "legend.fontsize": 8.5, "svg.fonttype": "none"})
    palette = dict(zip(LITHOLOGIES, plt.cm.tab10(np.linspace(0, .9, len(LITHOLOGIES)))))
    palette["mixed mafic/ultramafic"] = "#6b4c9a"

    fig, ax = plt.subplots(figsize=(13.2, 7.0))
    ax.set_xlim(-180, 180); ax.set_ylim(-65, 85)
    ax.set_xticks(np.arange(-180, 181, 60)); ax.set_yticks(np.arange(-60, 81, 30))
    ax.grid(color="#d7dde3", linewidth=.7); ax.axhline(0, color="#9aa7b2", linewidth=.8)
    map_classes = LITHOLOGIES + ["mixed mafic/ultramafic"]
    for lith in map_classes:
        if lith == "mixed mafic/ultramafic":
            pts = [r for r in locations if "|" in r["lithology"]]
        else:
            pts = [r for r in locations if r["lithology"] == lith]
        if not pts:
            continue
        for precision, marker in (("exact", "o"), ("approximate", "s"), ("regional", "^")):
            selected = [r for r in pts if precision in r["location_precision"]]
            if selected:
                ax.scatter([float(r["longitude"]) for r in selected], [float(r["latitude"]) for r in selected],
                           s=48, marker=marker, color=palette[lith], edgecolor="white", linewidth=.65,
                           label=lith if precision == "exact" else None, zorder=3)
    ax.set_xlabel("Longitude (degrees)", labelpad=12); ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Literature Lithology Atlas v1: independent natural geological settings")
    color_handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=palette[lith],
                            markeredgecolor="white", markersize=7, label=lith) for lith in map_classes]
    shape_handles = [Line2D([0], [0], marker=marker, color="#4a5560", linestyle="none", markersize=7, label=label)
                     for marker, label in (("o", "exact source-supported"), ("s", "approximate locality"), ("^", "regional centroid"))]
    legend_a = ax.legend(handles=color_handles, ncol=1, loc="upper left", bbox_to_anchor=(1.01, 1.03), frameon=False, title="Lithology", fontsize=8)
    ax.add_artist(legend_a)
    ax.legend(handles=shape_handles, ncol=1, loc="upper left", bbox_to_anchor=(1.01, .40), frameon=False, title="Coordinate precision", fontsize=8)
    ax.text(.01, .02, "Each mark is one natural setting. Regional-centroid and approximate-locality points are cartographic anchors, not invented sample GPS. Laboratory packs are not mapped.", transform=ax.transAxes, fontsize=8.2)
    fig.subplots_adjust(bottom=.17, right=.69); fig.savefig(PLOTS / "literature_atlas_global_map.svg"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    y = np.arange(len(LITHOLOGIES))
    for i, lith in enumerate(LITHOLOGIES):
        rows = [r for r in envelopes if r["lithology"] == lith]
        for j, row in enumerate(rows):
            lo, hi = row["total_porosity_min_percent"], row["total_porosity_max_percent"]
            if lo == "" or hi == "":
                continue
            off = (j - (len(rows)-1)/2) * .14
            ax.plot([float(lo), float(hi)], [i+off, i+off], lw=6, alpha=.72,
                    color=palette[lith], solid_capstyle="butt")
            ax.text(float(hi)+.7, i+off, row["state_class"], va="center", fontsize=7.3)
    ax.set_yticks(y, LITHOLOGIES); ax.set_xlim(0, 78)
    ax.set_xlabel("Broad source-supported total porosity envelope (%)")
    ax.set_title("Preliminary porosity sanity envelopes: state is part of the result")
    ax.grid(axis="x", alpha=.25); ax.invert_yaxis(); fig.tight_layout()
    fig.savefig(PLOTS / "literature_porosity_envelopes.svg"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.barh(y-.17, [int(r["independent_literature_sources"]) for r in coverage], .34,
            color="#365f91", label="independent literature sources")
    ax.barh(y+.17, [int(r["mapped_natural_settings"]) for r in coverage], .34,
            color="#82a96b", label="mapped natural settings")
    for i, row in enumerate(coverage):
        ax.text(max(int(row["independent_literature_sources"]), int(row["mapped_natural_settings"]))+.12,
                i, f"n≥{row['documented_primary_physical_specimens_minimum']} specimens", va="center", fontsize=8)
    ax.set_yticks(y, LITHOLOGIES); ax.invert_yaxis(); ax.set_xlabel("Count")
    ax.set_xlim(0, 8.45)
    ax.set_title("Atlas evidence depth (objects and review entries are not replication)")
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, -.10))
    ax.grid(axis="x", alpha=.25); fig.subplots_adjust(bottom=.20, left=.31, right=.96, top=.90)
    fig.savefig(PLOTS / "literature_atlas_evidence_depth.svg"); plt.close(fig)

    # One row is one state-specific void class.  The figure therefore avoids
    # a pooled lithology PSD and makes crack/vug/vesicle domains visible.
    class_colors = {
        "matrix/intergranular pore": "#4c78a8", "matrix pore": "#4c78a8",
        "matrix intercrystalline pore": "#4c78a8", "equant pore body": "#4c78a8",
        "intergranular pore": "#4c78a8", "pore body": "#4c78a8",
        "pore throat / entry constriction": "#e07b39", "pore throat / connecting aperture": "#e07b39",
        "grain-boundary / intragranular pore": "#6b9e6b", "grain-boundary / reaction nanoporosity": "#6b9e6b",
        "grain-boundary pore / microcrack": "#8c6bb1", "microcrack / crack": "#8c6bb1",
        "fracture-associated void": "#b44d4d", "vug / dissolution cavity": "#9a8b38", "vesicle": "#9a8b38",
    }
    rows = sorted(void_envelopes, key=lambda r: (LITHOLOGIES.index(r["lithology"]), r["state_class"], r["void_class"]))
    fig, ax = plt.subplots(figsize=(12.5, max(8.5, .34 * len(rows))))
    for i, row in enumerate(rows):
        lo, hi = float(row["size_min_um"]), float(row["size_max_um"])
        color = class_colors[row["void_class"]]
        ax.plot([lo, hi], [i, i], color=color, lw=5, solid_capstyle="butt", alpha=.86)
        ax.scatter([lo, hi], [i, i], color=color, s=18, zorder=3)
    labels = [f"{r['lithology']} — {r['state_class']} — {r['void_class']}" for r in rows]
    ax.set_yticks(range(len(rows)), labels, fontsize=7.1); ax.invert_yaxis(); ax.set_xscale("log")
    ax.set_xlabel("Source-supported size envelope (µm; log scale)")
    ax.set_title("Reference envelopes by void class and material state")
    handles = [
        Line2D([0], [0], color="#4c78a8", lw=5, label="matrix/intergranular or pore body"),
        Line2D([0], [0], color="#e07b39", lw=5, label="throat / entry / connecting aperture"),
        Line2D([0], [0], color="#6b9e6b", lw=5, label="grain-boundary / reaction pore"),
        Line2D([0], [0], color="#8c6bb1", lw=5, label="microcrack"),
        Line2D([0], [0], color="#b44d4d", lw=5, label="fracture-associated void"),
        Line2D([0], [0], color="#9a8b38", lw=5, label="vug / vesicle"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, -0.16), ncol=3, frameon=False, fontsize=7.5)
    ax.grid(axis="x", which="both", alpha=.25); fig.subplots_adjust(left=.47, right=.97, bottom=.19, top=.94)
    fig.savefig(PLOTS / "literature_void_class_envelopes.svg"); plt.close(fig)

    # This is a context comparison, not a re-scaling of any object table.
    # Grey bands are state-matched atlas envelopes; coloured intervals are the
    # reported M3 porosity contexts and retain their method/state caveats.
    m3_context = [
        ("Lipnice matrix-reference subset", "granite/granitoid", "fresh/intact crystalline matrix", .50, .50, "MIP connected"),
        ("Lipnice complete borehole suite", "granite/granitoid", "altered/weathered/fractured/gouge", .50, 6.53, "MIP connected; mixed states"),
        ("Fontainebleau/Berea", "sandstone", "intact matrix, conventional through tight", 3.8, 19.9, "CT total; resolved network"),
        ("Wilmslow BH13B", "sandstone", "intact matrix, conventional through tight", 9.77, 26.42, "CT total; 7 depths"),
        ("South China Sea carbonate", "carbonate", "intact matrix", 7.35, 23.41, "CT total; coarse macropore view"),
        ("Port Fairy basalt", "basalt/volcanic rock", "dense/intact lava matrix", 9.75, 9.75, "context only; not table-specific"),
        ("F42A laboratory pack", "unconsolidated sand/sediment", "laboratory/remoulded/packed", 33.0, 33.0, "CT image; laboratory standard"),
        ("Atlantis mafic cores", "gabbro/mafic crystalline", "fresh/intact matrix", .9, 2.9, "wet/dry bulk; transport context"),
        ("Atlantis ultramafic cores", "serpentinite/ultramafic", "fractured/weathered/dredged", 2.6, 12.8, "wet/dry bulk; fracture-sensitive"),
    ]
    envelope_lookup = {(r["lithology"], r["state_class"]): r for r in envelopes}
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    for i, (name, lith, state, lo, hi, note) in enumerate(m3_context):
        ref = envelope_lookup[(lith, state)]
        ax.axvspan(float(ref["total_porosity_min_percent"]), float(ref["total_porosity_max_percent"]),
                   ymin=(i-.38)/len(m3_context), ymax=(i+.38)/len(m3_context), color="#dfe5e8", zorder=0)
        ax.plot([lo, hi], [i, i], lw=6, color=palette[lith], solid_capstyle="butt", zorder=2)
        ax.scatter([lo, hi], [i, i], color=palette[lith], edgecolor="white", linewidth=.5, s=34, zorder=3)
    ax.set_xscale("log"); ax.set_xlim(.08, 250); ax.set_ylim(len(m3_context)-.5, -.5)
    ax.set_yticks(range(len(m3_context)), [f"{r[0]} — {r[5]}" for r in m3_context], fontsize=8.4)
    ax.set_xlabel("Porosity (%) — log scale")
    ax.set_title("Detailed M3 porosity context against state-matched literature envelopes")
    ax.grid(axis="x", which="both", alpha=.28)
    ax.legend([Line2D([0], [0], color="#dfe5e8", lw=9), Line2D([0], [0], color="#334e68", lw=5)],
              ["state-matched literature envelope", "M3 source-reported value/range"], loc="lower left", frameon=False)
    fig.subplots_adjust(left=.40, right=.97, bottom=.12, top=.92)
    fig.savefig(PLOTS / "m3_porosity_against_literature_envelopes.svg"); plt.close(fig)


def main():
    source_rows = sorted(SOURCES, key=lambda r: r["source_id"])
    obs_rows = sorted(OBSERVATIONS, key=lambda r: r["observation_id"])
    location_rows = make_locations(); envelope_rows = make_envelopes()
    void_envelope_rows = make_void_envelopes()
    coverage_rows = make_coverage(); audit_rows = make_m3_audit()
    porosity_summary_rows = make_porosity_summary(coverage_rows)
    write_csv(CAT / "literature_lithology_atlas_sources_v1.csv", source_rows)
    write_csv(CAT / "literature_lithology_atlas_observations_v1.csv", obs_rows)
    write_csv(CAT / "literature_lithology_atlas_locations_v1.csv", location_rows)
    write_csv(CAT / "literature_lithology_reference_envelopes_v1.csv", envelope_rows)
    write_csv(CAT / "literature_lithology_void_envelopes_v1.csv", void_envelope_rows)
    write_csv(CAT / "literature_lithology_atlas_coverage_v1.csv", coverage_rows)
    write_csv(CAT / "literature_lithology_porosity_summary_v1.csv", porosity_summary_rows)
    write_csv(CAT / "m3_literature_envelope_audit_v1.csv", audit_rows)
    make_plots(coverage_rows, location_rows, envelope_rows, void_envelope_rows)
    print(f"Literature Lithology Atlas v1: {len(source_rows)} sources, {len(obs_rows)} observation rows, {len(location_rows)} mapped settings")
    for row in coverage_rows:
        print(f"  {row['lithology']}: {row['independent_literature_sources']} sources, {row['mapped_natural_settings']} settings, n>={row['documented_primary_physical_specimens_minimum']} primary specimens")


if __name__ == "__main__":
    main()
