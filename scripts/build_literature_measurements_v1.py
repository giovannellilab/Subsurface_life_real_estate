"""Build a compact, source-faithful quantitative literature measurement resource.

This is not a raw-data mirror.  It re-expresses explicit numbers already
extracted from the selected 40-source atlas and the locally held Park &
Santamarina Supplementary Table S2.  Detailed M3 ingestions are deliberately
excluded: their rows remain in the M3 resource and must not be double-counted
as independent literature measurements.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalogues"
OUT = ROOT / "data/processed/m3_literature_measurements_v1"
PLOTS = OUT / "plots"
LITHOLOGIES = [
    "unconsolidated sand/sediment", "sandstone", "mudstone/shale", "carbonate",
    "basalt/volcanic rock", "granite/granitoid", "gabbro/mafic crystalline",
    "serpentinite/ultramafic", "metamorphic rock",
]
DETAILED_M3_SOURCE_IDS = {"LIT-002", "LIT-006", "LIT-007", "LIT-010", "LIT-014", "LIT-018", "LIT-023", "LIT-028"}
NUMBER = re.compile(r"(?<![A-Za-z])(?:\d+(?:\.\d+)?|\.\d+)")


# One line is one named fitted component from Park & Santamarina S2.  The
# columns are: lithology | state | group | component label | fitted mean um |
# fitted standard deviation um | S2 reference number.  Bimodal components
# remain separate but retain their shared parent group.
PARK_S2 = """
unconsolidated sand/sediment|natural soil|1|Bothkennar clay|1.58|0.57|3
unconsolidated sand/sediment|natural soil|2|Osaka clay (Ma11)|0.43|0.17|3
unconsolidated sand/sediment|natural soil|3|Kyoto clay (Ma4)|0.33|0.13|3
unconsolidated sand/sediment|natural soil|4|Osaka clay (Ma13)|1.36|0.49|3
unconsolidated sand/sediment|natural soil|5|Soil A|178.4|47.2|4
unconsolidated sand/sediment|natural soil|6|GB-0.2|38.5|50.4|5
unconsolidated sand/sediment|natural soil|7|Pusan clay 1|0.33|0.14|6
unconsolidated sand/sediment|natural soil|8|Pusan clay 5|0.75|0.33|6
unconsolidated sand/sediment|natural soil|9|Fontainebleau|6.87|1.60|7
unconsolidated sand/sediment|natural soil|10|Brown Agra|7.14|1.67|7
unconsolidated sand/sediment|natural soil|11|green Agra|0.11|0.03|7
unconsolidated sand/sediment|natural soil|12|Roche fine|26.4|4.53|7
unconsolidated sand/sediment|natural soil|13|Liais|0.20|0.10|7
unconsolidated sand/sediment|natural soil|14|St Guillaume clay|0.14|0.20|8
unconsolidated sand/sediment|remoulded soil|1|Soil B|121.3|38.5|4
unconsolidated sand/sediment|remoulded soil|2|Soil C|27.7|10.0|4
unconsolidated sand/sediment|remoulded soil|3|Soil A - High|169.2|42.9|4
unconsolidated sand/sediment|remoulded soil|4|Soil A - Low|233.0|84.1|4
unconsolidated sand/sediment|remoulded soil|5|Soil C - Low|27.1|11.3|4
unconsolidated sand/sediment|remoulded soil|6|Soil C - High|57.4|23.9|4
unconsolidated sand/sediment|remoulded soil|7|Pusan clay 2|0.48|0.19|6
unconsolidated sand/sediment|remoulded soil|8|Pusan clay 3|0.61|0.24|6
unconsolidated sand/sediment|remoulded soil|9|Pusan clay 4|0.54|0.23|6
unconsolidated sand/sediment|remoulded soil|10|St Guillaume clay|0.40|0.40|8
unconsolidated sand/sediment|remoulded soil|11|Silty clay 1|2.50|1.58|9
unconsolidated sand/sediment|remoulded soil|12|Silty clay 2|2.74|1.73|9
unconsolidated sand/sediment|remoulded soil|13|Silty clay 3|3.67|1.74|9
unconsolidated sand/sediment|remoulded soil|14|Silty clay 4|4.46|1.04|9
unconsolidated sand/sediment|remoulded soil|15|Glacial till 17%|2.70|2.15|10
unconsolidated sand/sediment|remoulded soil|16|Glacial till 8%|1.91|1.14|10
unconsolidated sand/sediment|remoulded soil|17|Glacial 17% (After SWCC)|0.16|0.09|10
unconsolidated sand/sediment|remoulded soil|18|Glacial 17% (Before SWCC)|1.36|1.52|10
unconsolidated sand/sediment|remoulded soil|19|Sample mta-1|1.88|1.12|11
unconsolidated sand/sediment|remoulded soil|20|Kaolin|0.17|0.08|12
unconsolidated sand/sediment|remoulded soil|21|Soil 1 (30 kPa)|0.46|0.17|13
unconsolidated sand/sediment|remoulded soil|22|Soil 1 (LL)|1.72|0.92|13
unconsolidated sand/sediment|remoulded soil|23|Soil 2 (LL)|0.23|0.12|13
unconsolidated sand/sediment|remoulded soil|24|Soil 4 (LL)|3.09|2.25|13
unconsolidated sand/sediment|remoulded soil|25|Soil 4 (120 kPa)|0.75|0.54|13
carbonate|intact rock|1|Winterset|1.53|0.77|14
carbonate|intact rock|2|Austin Chalk|1.08|0.94|15
carbonate|intact rock|3|Desert Pink|5.88|2.31|16
carbonate|intact rock|4|Edwards White|0.95|0.45|17
carbonate|intact rock|5|Edward Yellow|3.96|0.92|17
carbonate|intact rock|6|Indiana 2-4|0.45|0.33|18
carbonate|intact rock|7|Indiana 60 (1)|0.39|0.21|18
carbonate|intact rock|7|Indiana 60 (2)|13.5|15.1|18
carbonate|intact rock|8|Indiana 70 (1)|25.1|13.4|18
carbonate|intact rock|8|Indiana 70 (2)|0.37|0.20|18
carbonate|intact rock|9|Indiana 200 (1)|31.5|18.7|18
carbonate|intact rock|9|Indiana 200 (2)|0.41|0.24|18
carbonate|intact rock|10|Mount Gambier|29.6|11.3|19
carbonate|intact rock|11|Silurian Dolomite|11.7|4.23|20
carbonate|intact rock|12|Carbonate-1 (1)|19.0|8.80|21
carbonate|intact rock|12|Carbonate-1 (2)|3.59|1.49|21
carbonate|intact rock|13|Carbonate-2|9.41|4.24|21
carbonate|intact rock|14|Carbonate-3 (1)|10.6|4.54|21
carbonate|intact rock|14|Carbonate-3 (2)|2.52|1.34|21
carbonate|intact rock|15|Carbonate-4|19.1|11.3|21
carbonate|intact rock|16|Carbonate-5 (1)|16.1|10.6|21
carbonate|intact rock|16|Carbonate-5 (2)|2.39|1.27|21
carbonate|intact rock|17|Carbonate-6 (1)|16.1|10.6|21
carbonate|intact rock|17|Carbonate-6 (2)|3.40|1.81|21
carbonate|intact rock|18|Carbonate-7 (1)|19.8|8.71|21
carbonate|intact rock|18|Carbonate-7 (2)|3.30|2.62|21
carbonate|intact rock|19|Carbonate-8 (1)|16.1|10.6|21
carbonate|intact rock|19|Carbonate-8 (2)|3.83|3.05|21
carbonate|intact rock|20|Carbonate-9 (1)|21.7|14.3|21
carbonate|intact rock|20|Carbonate-9 (2)|3.25|2.14|21
carbonate|intact rock|21|Carbonate-10 (1)|18.1|10.8|21
carbonate|intact rock|21|Carbonate-10 (2)|3.25|2.14|21
carbonate|intact rock|22|Carbonate-11 (1)|17.3|5.68|21
carbonate|intact rock|22|Carbonate-11 (2)|3.33|2.37|21
carbonate|intact rock|23|Carbonate-12 (1)|18.6|9.93|21
carbonate|intact rock|23|Carbonate-12 (2)|3.97|2.61|21
sandstone|intact rock|1|C11|0.603|0.479|22
sandstone|intact rock|2|C29|0.228|0.121|22
sandstone|intact rock|3|No.1|0.023|0.011|23
sandstone|intact rock|4|No.2|0.267|0.096|23
sandstone|intact rock|5|No.3|0.030|0.012|23
sandstone|intact rock|6|No.4 (1)|0.264|0.087|23
sandstone|intact rock|6|No.4 (2)|0.071|0.025|23
sandstone|intact rock|7|No.5 (1)|0.283|0.080|23
sandstone|intact rock|7|No.5 (2)|0.075|0.023|23
sandstone|intact rock|8|No.6 (1)|0.342|0.097|23
sandstone|intact rock|8|No.6 (2)|0.077|0.023|23
sandstone|intact rock|9|No.7|0.395|0.100|23
sandstone|intact rock|10|No.8|0.019|0.008|23
sandstone|intact rock|11|No.9|0.252|0.099|23
sandstone|intact rock|12|No.10|0.028|0.008|23
sandstone|intact rock|13|No.11|0.312|0.085|23
sandstone|intact rock|14|No.12 (1)|1.523|0.387|23
sandstone|intact rock|14|No.12 (2)|3.648|0.812|23
sandstone|intact rock|15|No.13 (1)|0.257|0.079|23
sandstone|intact rock|15|No.13 (2)|0.083|0.015|23
sandstone|intact rock|16|No.14 (1)|0.309|0.072|23
sandstone|intact rock|16|No.14 (2)|0.079|0.016|23
sandstone|intact rock|17|No.15 (1)|0.401|0.176|23
sandstone|intact rock|17|No.15 (2)|0.083|0.016|23
mudstone/shale|intact rock|1|North Sea shale (1)|0.042|0.007|24
mudstone/shale|intact rock|1|North Sea shale (2)|0.013|0.003|24
mudstone/shale|intact rock|2|Mancos B (1)|0.046|0.030|24
mudstone/shale|intact rock|2|Mancos B (2)|0.112|0.034|24
mudstone/shale|intact rock|3|Middle Bakken (1)|0.029|0.019|24
mudstone/shale|intact rock|3|Middle Bakken (2)|0.112|0.034|24
mudstone/shale|intact rock|4|Woodford shale (1)|0.004|0.001|24
mudstone/shale|intact rock|4|Woodford shale (2)|0.026|0.011|24
""".strip()


def read_csv(name: str) -> list[dict]:
    with (CAT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FIELDS = [
    "measurement_id", "provenance_layer", "source_id", "source_citation", "lithology",
    "sample_state", "natural_setting", "location_precision", "sample_group_id",
    "parent_group_id", "component_label", "physical_specimens_represented",
    "measurement_family", "geometry_class", "statistic_type", "value", "value_min",
    "value_max", "auxiliary_statistic_type", "auxiliary_value", "unit",
    "native_definition", "method", "weighting_or_definition",
    "observation_window_or_detection_limit", "depth_stress_state_context",
    "source_locator", "value_text_raw", "notes",
]


def record(**kwargs) -> dict:
    row = {field: "" for field in FIELDS}
    row.update(kwargs)
    return row


def numeric_summary(raw: str) -> tuple[str, str, str]:
    """Return one scalar or one source-reported range; never explode ranges."""
    values = NUMBER.findall(raw)
    if len(values) == 1:
        return values[0], "", ""
    if len(values) == 2:
        return "", values[0], values[1]
    return "", "", ""


def park_rows(source_lookup: dict) -> list[dict]:
    rows = []
    for line in PARK_S2.splitlines():
        lith, state, group, component, mean, sd, reference = line.split("|")
        # Soil state is needed in the key: Supplementary Table S2 restarts
        # group numbering for natural and remoulded soils.
        parent = f"PARK-S2-{lith[:3].upper()}-{state[:3].upper()}-{group.zfill(2)}"
        shared = dict(
            provenance_layer="park_santamarina_benchmark", source_id="LIT-001",
            source_citation=source_lookup["LIT-001"]["citation"], lithology=lith,
            sample_state=state, natural_setting="Park & Santamarina S2 source-specific group",
            location_precision="source-specific; not mapped here", sample_group_id=parent,
            parent_group_id=parent, component_label=component, physical_specimens_represented="one named S2 dataset/group; underlying specimen count source-specific",
            measurement_family="pore_size", geometry_class="fitted pore-scale distribution",
            unit="um", native_definition="Park & Santamarina Table S2 mean pore diameter μd; source-specific fitted distribution component",
            method="source-dependent distribution fitted by Park & Santamarina",
            weighting_or_definition="source-dependent; retain S2 component and cited source reference",
            source_locator=f"Park & Santamarina 2020 Supplementary Table S2, group {group}, Ref. {reference}",
            notes="One row per named fitted component. Bimodal components share a parent group; neither components nor parameters are individual pores.",
        )
        rows.append(record(**shared, statistic_type="fitted distribution mean", value=mean))
        rows.append(record(**shared, statistic_type="fitted distribution standard deviation", value=sd))
    return rows


def atlas_context_rows(observations: list[dict], source_lookup: dict) -> list[dict]:
    """Translate existing non-M3, non-Park extracted values without adding data."""
    rows = []
    for obs in observations:
        if obs["source_id"] in DETAILED_M3_SOURCE_IDS or obs["source_id"] == "LIT-001":
            continue
        shared = dict(
            provenance_layer="selected_literature_outside_detailed_m3",
            source_id=obs["source_id"], source_citation=source_lookup[obs["source_id"]]["citation"],
            lithology=obs["lithology"], sample_state=obs["sample_state"],
            natural_setting=obs["locality_formation_borehole"], location_precision=obs["location_precision"],
            sample_group_id=obs["observation_id"], physical_specimens_represented=obs["physical_specimens"],
            geometry_class=obs["geometry_class"], unit=obs["size_unit"],
            native_definition=obs["radius_diameter_or_definition"], method=obs["method"],
            weighting_or_definition=obs["weighting_basis"],
            observation_window_or_detection_limit=obs["resolution_or_detection_window"],
            depth_stress_state_context=obs["depth_stress_state_context"],
            source_locator=obs["exact_table_figure_provenance"], notes=obs["interpretation_note"],
        )
        for family, raw, definition in (
            ("total_porosity", obs["total_porosity_percent"], "source-reported total/open/bulk porosity; source text preserved"),
            ("effective_connected_porosity", obs["effective_connected_porosity_percent"], "source-reported effective/connected/accessibility porosity; source text preserved"),
        ):
            if raw:
                value, lo, hi = numeric_summary(raw)
                # Multi-clause narrative context (for example, three different
                # image-domain porosities) belongs in the atlas observation
                # row, not in a fake long-form scalar row.  Explicit component
                # values are retained separately when already recovered.
                # Semicolon-delimited clauses name separate materials or
                # domains in this compact atlas field; their explicit values
                # are emitted as separate rows below only when source context
                # supports that separation.
                if (value or lo or hi) and ";" not in raw:
                    rows.append(record(**{**shared, "measurement_family": family,
                                          "statistic_type": "source-reported scalar" if value else "source-reported range/context",
                                          "value": value, "value_min": lo, "value_max": hi,
                                          "unit": "percent", "native_definition": definition,
                                          "value_text_raw": raw}))
        if any(obs[key] for key in ("size_min", "size_central", "size_max")):
            statistic = "reported central value"
            if obs["size_min"] and obs["size_max"]:
                statistic = "reported range with central value" if obs["size_central"] else "reported range"
            rows.append(record(**shared, measurement_family="pore_size_or_void_scale", statistic_type=statistic,
                               value=obs["size_central"], value_min=obs["size_min"], value_max=obs["size_max"],
                               value_text_raw="; ".join(f"{key}={obs[key]}" for key in ("size_min", "size_central", "size_max") if obs[key])))
    return rows


def extra_rows(source_lookup: dict) -> list[dict]:
    """Explicit published numbers noted in existing atlas provenance but absent from its compact fields."""
    entries = [
        ("LIT-003", "unconsolidated sand/sediment", "natural, undisturbed", "Alameda County beach, California", "exact", "three beach cores", "connectivity", "grain-contact coordination", "range", "", "7.71", "8.31", "", "", "count", "mean grain coordination", "synchrotron micro-CT", "grain count", "6.45 um voxel", "1, 6 and 11 cm below surface", "Table 1", "Natural cores; coordination is not throat size."),
        ("LIT-003", "unconsolidated sand/sediment", "laboratory pluviated", "Alameda sand reconstruction", "laboratory", "one reconstruction", "connectivity", "grain-contact coordination", "mean", "7.45", "", "", "", "", "count", "mean grain coordination", "synchrotron micro-CT", "grain count", "6.45 um voxel", "", "Table 1", "Laboratory fabric; not mapped as natural setting."),
        ("LIT-008", "sandstone", "fresh natural core", "Longdong, Ordos Basin", "regional", "15 cores", "pore_throat", "pore throat / entry constriction", "study mean", "0.127", "", "", "", "", "um", "MICP mean pore-throat radius", "MICP", "mercury intrusion", "", "about 1441-2069 m examples", "Supplementary Table S3", "Separate from reported sample range."),
        ("LIT-009", "sandstone", "natural reservoir core", "southeast Ordos Basin", "regional", "45 samples; 16 representative curves", "pore_throat", "pore throat / entry constriction", "mean", "0.89", "", "", "", "", "um", "mean maximum throat radius for reported type-I example", "MICP + microscopy", "mercury intrusion", "", "", "Table 1 and Figure 5", "Not a lithology-wide throat statistic."),
        ("LIT-011", "mudstone/shale", "shallow fractured aquifer matrix", "West Trenton, New Jersey", "approximate locality", "94 cores", "porosity_fraction", "largest MIP entry class", "reported fraction", "0.1", "", "", "", "", "percent", "porosity associated with the largest MIP entry class", "MIP", "incremental intruded porosity", "", "seven boreholes to ~35 m", "Results", "Not total porosity; fracture porosity was not measured from cores."),
        ("LIT-021", "basalt/volcanic rock", "fresh natural road outcrop", "Reykjanes Peninsula, Iceland", "regional", "one specimen", "porosity_fraction", "crack-associated intrusion", "reported contribution", "1", "", "", "", "", "percent", "approximately one percentage point of open porosity in crack-associated MIP mode", "MIP", "intruded porosity", "", "0-200 MPa experiments after characterization", "Figure 1", "Separate from equant-pore contribution."),
        ("LIT-021", "basalt/volcanic rock", "fresh natural road outcrop", "Reykjanes Peninsula, Iceland", "regional", "one specimen", "porosity_fraction", "equant-pore intrusion", "reported contribution", "7", "", "", "", "", "percent", "approximately seven percentage points of open porosity in equant-pore MIP mode", "MIP + SEM", "intruded porosity", "", "0-200 MPa experiments after characterization", "Figure 1", "Separate from crack-associated mode."),
        ("LIT-022", "basalt/volcanic rock", "natural volcanic rock", "Mt Etna, Sicily", "regional", "one specimen", "porosity_fraction", "MIP entry constrictions below threshold", "reported fraction", "65", "", "", "", "", "percent", "fraction of porosity accessed through throat radii below 0.5 um", "MIP + pressure-dependent permeability", "intruded connected pore volume", "", "", "Figure 4b and discussion", "Threshold is radius, not diameter."),
        ("LIT-022", "basalt/volcanic rock", "natural volcanic rock", "Mt Etna, Sicily", "regional", "one specimen", "pore_throat", "pore throat / entry constriction", "threshold", "0.5", "", "", "", "", "um", "MIP throat radius threshold used for reported 65% porosity fraction", "MIP + pressure-dependent permeability", "intruded connected pore volume", "", "", "Figure 4b and discussion", "Retained separately from mean throat radius."),
        ("LIT-034", "serpentinite/ultramafic", "partially serpentinised natural rock", "ODP Site 1274 and Roragen", "exact core + regional", "two settings", "porosity_fraction", "FIB-SEM analysed volume", "range", "", "0.2", "0.7", "", "", "percent", "local FIB-SEM porosity", "FIB-SEM nanotomography", "image volume", "~3 nm SEM pixels", "", "Figures 2-5", "Local analysed volume; not whole-rock porosity."),
        ("LIT-034", "serpentinite/ultramafic", "partially serpentinised natural rock", "ODP Site 1274 and Roragen", "exact core + regional", "two settings", "porosity_fraction", "TEM analysed foil", "range", "", "1", "3", "", "", "percent", "local TEM-foil porosity", "TEM", "image area/foil", "0.5 nm TEM", "", "Figures 2-5", "Local analysed volume; not whole-rock porosity."),
        ("LIT-034", "serpentinite/ultramafic", "partially serpentinised natural rock", "ODP Site 1274 and Roragen", "exact core + regional", "two settings", "porosity_fraction", "brucite-rich interface", "mean with uncertainty", "12", "", "", "standard deviation", "4", "percent", "local interface porosity", "TEM/FIB-SEM", "local interface image domain", "", "", "Figure 9", "Not a bulk serpentinite porosity."),
        ("LIT-037", "metamorphic rock", "natural borehole reservoir", "LT1/LT2 wells, Songliao Basin", "regional", "schist/mylonite suite", "porosity_fraction", "chlorite/mica schist", "mean", "1.46", "", "", "", "", "percent", "reported mean porosity", "HPMI + N2 adsorption/DFT", "source-reported", "", "", "Tables 4-6", "Separate material from mylonite."),
        ("LIT-037", "metamorphic rock", "natural borehole reservoir", "LT1/LT2 wells, Songliao Basin", "regional", "schist/mylonite suite", "porosity_fraction", "granitic mylonite", "mean", "1.00", "", "", "", "", "percent", "reported mean porosity", "HPMI + N2 adsorption/DFT", "source-reported", "", "", "Tables 4-6", "Separate material from schist."),
        ("LIT-037", "metamorphic rock", "natural borehole reservoir", "LT1/LT2 wells, Songliao Basin", "regional", "schist/mylonite suite", "porosity_fraction", "chlorite/mica schist fine-pore contribution", "reported fraction", "60", "", "", "", "", "percent", "more than 60% of schist pore volume below 0.1 um", "HPMI + N2 adsorption/DFT", "intruded/adsorbed pore volume", "", "", "Figures 5-8", "Lower-bound statement; retained as reported."),
        ("LIT-037", "metamorphic rock", "natural borehole reservoir", "LT1/LT2 wells, Songliao Basin", "regional", "schist/mylonite suite", "pore_size", "matrix pore", "threshold", "0.1", "", "", "", "", "um", "threshold for reported schist pore-volume fraction", "HPMI + N2 adsorption/DFT", "intruded/adsorbed pore volume", "", "", "Figures 5-8", "Diameter domain as reported."),
    ]
    rows = []
    for entry in entries:
        (source, lith, state, setting, precision, specimens, family, geometry, statistic, value, lo, hi, aux_stat, aux_value, unit, definition, method, weighting, window, depth, locator, notes) = entry
        rows.append(record(
            provenance_layer="selected_literature_outside_detailed_m3", source_id=source,
            source_citation=source_lookup[source]["citation"], lithology=lith, sample_state=state,
            natural_setting=setting, location_precision=precision, sample_group_id=f"EXTRA-{source}-{len(rows)+1:02d}",
            physical_specimens_represented=specimens, measurement_family=family, geometry_class=geometry,
            statistic_type=statistic, value=value, value_min=lo, value_max=hi,
            auxiliary_statistic_type=aux_stat, auxiliary_value=aux_value, unit=unit,
            native_definition=definition, method=method, weighting_or_definition=weighting,
            observation_window_or_detection_limit=window, depth_stress_state_context=depth,
            source_locator=locator, notes=notes,
        ))
    return rows


# Johnson (1980) Table 1, transcribed as reported from the small USGS paper.
# Values are two different accessible-porosity measurements on each core
# specimen, not two estimates to average.  The table demonstrates depth- and
# vesicularity-sensitive basalt state without creating a pore-size record.
KILAUEA_TABLE1 = [
    (0.99, 40.8, 38.9), (1.91, 26.8, 26.1), (2.87, 24.7, 22.3), (3.73, 26.7, 25.6),
    (4.70, 14.1, 13.6), (5.59, 14.6, 13.1), (6.53, 7.32, 4.71), (7.39, 12.6, 12.6),
    (8.31, 15.4, 15.6), (9.22, 20.2, 19.4), (10.13, 17.2, 16.5), (11.00, 13.7, 13.0),
    (11.96, 24.3, 23.5), (12.88, 10.1, 9.38), (13.84, 10.4, 10.4), (14.71, 10.6, 10.1),
    (15.62, 10.4, 10.4), (16.56, 26.4, 25.9), (16.56, 11.7, 11.2), (17.45, 9.58, 8.85),
    (18.31, 10.4, 9.96), (19.30, 14.7, 14.0), (20.57, 13.0, 12.2), (21.65, 13.1, 12.6),
    (23.24, 18.7, 18.1), (24.16, 11.8, 11.2), (25.07, 15.2, 14.8), (25.96, 9.63, 8.31),
    (27.20, 9.70, 7.97), (28.32, 9.92, 9.12), (28.93, 7.94, 7.03), (29.90, 10.4, 8.11),
    (30.99, 9.14, 8.09), (32.54, 7.92, 4.43), (33.45, 7.28, 4.14), (34.47, 6.72, 4.53),
    (35.38, 8.41, 6.19), (36.60, 8.43, 7.42), (37.57, 11.4, 10.6), (39.04, 13.3, 12.5),
    (39.80, 5.42, 5.04), (41.17, 5.95, 4.51), (42.11, 5.42, 4.54), (43.03, 7.47, 4.94),
]


def kilauea_table_rows(source_lookup: dict) -> list[dict]:
    rows = []
    for index, (depth, helium, water) in enumerate(KILAUEA_TABLE1, 1):
        shared = dict(
            provenance_layer="selected_literature_outside_detailed_m3", source_id="LIT-020",
            source_citation=source_lookup["LIT-020"]["citation"], lithology="basalt/volcanic rock",
            sample_state="natural Kilauea Iki drill-core basalt; depth/vesicularity variable",
            natural_setting="Kilauea Iki drill hole KI-76-1, Hawaii", location_precision="exact volcanic setting",
            sample_group_id=f"KILAUEA-KI-76-1-{index:02d}", physical_specimens_represented="one Table 1 core specimen",
            geometry_class="vesicle/crack-accessible bulk porosity", statistic_type="individual table value",
            unit="percent", method="helium and water saturation", weighting_or_definition="individual core specimen",
            depth_stress_state_context=f"core depth {depth:.2f} m",
            source_locator="Johnson 1980, USGS Professional Paper 1123-B, Table 1",
            notes="Accessible porosity; no pore-size distribution is asserted. Helium and water values remain separate.",
        )
        rows.append(record(**shared, measurement_family="total_porosity", value=str(helium),
                           native_definition="helium-accessible porosity PHe"))
        rows.append(record(**shared, measurement_family="effective_connected_porosity", value=str(water),
                           native_definition="water-accessible porosity PH2O after saturation at about one atmosphere"))
    return rows


def classify_measurement(row: dict) -> str:
    text = (row["measurement_family"] + " " + row["geometry_class"]).lower()
    if "porosity" in text:
        return "porosity"
    # P&S report fitted pore-scale components.  Their source-specific
    # pore-definition is useful benchmark evidence, but it cannot be promoted
    # to a pore-body or throat class here.
    if "fitted pore-scale" in text:
        return "fitted_pore_scale_unresolved"
    if any(word in text for word in ("throat", "entry", "aperture")):
        return "throat_or_constriction"
    if any(word in text for word in ("crack", "fracture")):
        return "crack_or_fracture"
    if any(word in text for word in ("pore", "vesicle", "vug", "grain-boundary")):
        return "pore_body_or_other_void"
    return "connectivity_or_context"


def first_integer(text: str) -> int:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def coverage(rows: list[dict], sources: list[dict], locations: list[dict], observations: list[dict]) -> list[dict]:
    by_lith = defaultdict(list)
    for row in rows:
        by_lith[row["lithology"]].append(row)
    output = []
    for lith in LITHOLOGIES:
        group = by_lith[lith]
        counts = Counter(classify_measurement(r) for r in group)
        scalar_values = sum(bool(r["value"]) + bool(r["value_min"]) + bool(r["value_max"]) + bool(r["auxiliary_value"]) for r in group)
        source_records = [r for r in sources if r["source_id"] not in DETAILED_M3_SOURCE_IDS and lith in r["lithology_classes"].split("|")]
        measurement_sources = {r["source_id"] for r in group}
        context = [r for r in observations if r["source_id"] not in DETAILED_M3_SOURCE_IDS and r["source_id"] != "LIT-001" and r["lithology"] == lith]
        natural_context = [r for r in context if "laboratory" not in (r["sample_state"] + " " + r["locality_formation_borehole"]).lower()]
        lab_context = [r for r in context if r not in natural_context]
        natural_specimens = sum(first_integer(r["physical_specimens"]) for r in natural_context if r["count_in_primary_specimen_minimum"] == "yes")
        laboratory_specimens = sum(first_integer(r["physical_specimens"]) for r in lab_context if r["count_in_primary_specimen_minimum"] == "yes")
        mapped_settings = [
            r for r in locations
            if r["material_setting"].startswith("natural")
            and lith in r["lithology"].split("|")
            and set(r["source_ids"].split("|")) & {s["source_id"] for s in source_records}
        ]
        output.append({
            "lithology": lith,
            "atlas_source_records_outside_detailed_m3": len(source_records),
            "sources_with_quantitative_rows": len(measurement_sources),
            "direct_context_observation_rows_outside_detailed_m3": len(context),
            "mapped_natural_settings_outside_detailed_m3": len(mapped_settings),
            "conservative_natural_specimens_outside_detailed_m3": natural_specimens,
            "conservative_laboratory_specimens_outside_detailed_m3": laboratory_specimens,
            "quantitative_measurement_rows": len(group),
            "quantitative_scalar_values": scalar_values,
            "park_s2_measurement_rows": sum(r["provenance_layer"] == "park_santamarina_benchmark" for r in group),
            "park_s2_component_groups": len({(r["parent_group_id"], r["component_label"]) for r in group if r["provenance_layer"] == "park_santamarina_benchmark"}),
            "other_literature_rows": sum(r["provenance_layer"] != "park_santamarina_benchmark" for r in group),
            "porosity_measurement_rows": counts["porosity"],
            "pore_body_or_other_void_rows": counts["pore_body_or_other_void"],
            "fitted_pore_scale_unresolved_rows": counts["fitted_pore_scale_unresolved"],
            "throat_or_constriction_rows": counts["throat_or_constriction"],
            "crack_or_fracture_rows": counts["crack_or_fracture"],
            "connectivity_or_context_rows": counts["connectivity_or_context"],
            "methods_represented": "|".join(sorted({r["method"] for r in group if r["method"]})),
            "counting_note": "Measurement rows are explicit published scalar, range, threshold or fitted-distribution summaries. They are not individual pores and not necessarily individual specimens. Source/settings/specimen columns exclude detailed M3 rows; Park S2 source-specific groups are counted separately.",
        })
    return output


def make_plots(rows: list[dict], cov: list[dict]) -> None:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 13, "axes.labelsize": 11, "legend.fontsize": 8.5, "svg.fonttype": "none"})
    palette = dict(zip(LITHOLOGIES, plt.cm.tab10(np.linspace(0, .9, len(LITHOLOGIES)))))

    # Published-measurement breadth and detailed-M3 context are intentionally separate axes.
    y = np.arange(len(LITHOLOGIES))
    fig, ax = plt.subplots(figsize=(11, 6.4))
    other = [int(r["other_literature_rows"]) for r in cov]
    park = [int(r["park_s2_measurement_rows"]) for r in cov]
    ax.barh(y, other, color="#547aa5", label="other selected-literature rows")
    ax.barh(y, park, left=other, color="#c99032", label="Park S2 mean/SD parameter rows")
    for i, row in enumerate(cov):
        ax.text(other[i] + park[i] + .7, i, f"{row['quantitative_scalar_values']} scalar values", va="center", fontsize=8)
    ax.set_yticks(y, [r["lithology"] for r in cov]); ax.invert_yaxis()
    ax.set_xlabel("Explicit published measurement rows")
    ax.set_title("Literature measurement depth (detailed-M3 raw objects excluded)")
    ax.legend(frameon=False, loc="lower right"); ax.grid(axis="x", alpha=.25)
    fig.tight_layout(); fig.savefig(PLOTS / "literature_quantitative_measurement_depth.svg"); plt.close(fig)

    # Individual scalar porosities and published ranges, one source/group per mark.
    porosity = [r for r in rows if classify_measurement(r) == "porosity" and r["unit"] == "percent"]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for i, lith in enumerate(LITHOLOGIES):
        group = [r for r in porosity if r["lithology"] == lith]
        for j, row in enumerate(group):
            # Keep high-depth tables inside their lithology lane; the marks
            # represent measurement count, not a vertical variable.
            offsets = np.linspace(-.32, .32, len(group)) if len(group) > 1 else np.array([0.0])
            yy = i + offsets[j]
            if row["value_min"] and row["value_max"]:
                ax.plot([float(row["value_min"]), float(row["value_max"])], [yy, yy], color=palette[lith], lw=2.5)
            if row["value"]:
                ax.scatter(float(row["value"]), yy, color=palette[lith], s=28, edgecolor="white", linewidth=.5, zorder=3)
    ax.set_xscale("log"); ax.set_xlim(.03, 100); ax.set_yticks(y, LITHOLOGIES); ax.invert_yaxis()
    ax.set_xlabel("Published porosity value or reported range (%) — log scale")
    ax.set_title("Published porosity measurements outside detailed M3")
    ax.text(.01, .02, "Dots = reported scalar/mean; horizontal lines = one source-reported range. State and method remain in the long-form table.", transform=ax.transAxes, fontsize=8)
    ax.grid(axis="x", which="both", alpha=.25); fig.tight_layout()
    fig.savefig(PLOTS / "literature_published_porosity.svg"); plt.close(fig)

    # Size records retain source geometry labels; fitted S2 pore scales are not relabelled as throats.
    size = [r for r in rows if r["unit"] == "um" and r["statistic_type"] != "fitted distribution standard deviation" and any((r["value"], r["value_min"], r["value_max"]))]
    panels = [
        ("Pore/matrix/vesicle/vug and fitted pore-scale summaries", lambda r: classify_measurement(r) in {"pore_body_or_other_void", "fitted_pore_scale_unresolved"}),
        ("Throat/entry and crack/fracture summaries", lambda r: classify_measurement(r) in {"throat_or_constriction", "crack_or_fracture"}),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    for ax, (title, predicate) in zip(axes, panels):
        subset = [r for r in size if predicate(r)]
        for i, lith in enumerate(LITHOLOGIES):
            group = [r for r in subset if r["lithology"] == lith]
            for j, row in enumerate(group):
                offsets = np.linspace(-.32, .32, len(group)) if len(group) > 1 else np.array([0.0])
                yy = i + offsets[j]
                lo = float(row["value_min"]) if row["value_min"] else None
                hi = float(row["value_max"]) if row["value_max"] else None
                if lo is not None and hi is not None:
                    ax.plot([lo, hi], [yy, yy], color=palette[lith], lw=1.8, alpha=.65)
                if row["value"]:
                    marker = "s" if row["provenance_layer"] == "park_santamarina_benchmark" else "o"
                    ax.scatter(float(row["value"]), yy, color=palette[lith], marker=marker, s=18, edgecolor="white", linewidth=.35, zorder=3)
        ax.set_yticks(y, LITHOLOGIES); ax.invert_yaxis(); ax.set_title(title); ax.grid(axis="x", which="both", alpha=.24)
    axes[-1].set_xscale("log"); axes[-1].set_xlim(1e-4, 2e4)
    axes[-1].set_xlabel("Published source-native size (µm) — log scale")
    fig.text(.5, .01, "Square = Park & Santamarina S2 fitted pore-scale component; circle = other selected literature. Lines are one reported range.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(PLOTS / "literature_published_void_sizes.svg"); plt.close(fig)


def main() -> None:
    sources = read_csv("literature_lithology_atlas_sources_v1.csv")
    source_lookup = {r["source_id"]: r for r in sources}
    observations = read_csv("literature_lithology_atlas_observations_v1.csv")
    locations = read_csv("literature_lithology_atlas_locations_v1.csv")
    rows = park_rows(source_lookup) + atlas_context_rows(observations, source_lookup) + extra_rows(source_lookup) + kilauea_table_rows(source_lookup)
    for index, row in enumerate(rows, 1):
        row["measurement_id"] = f"LITM-{index:04d}"
    cov = coverage(rows, sources, locations, observations)
    write_csv(CAT / "literature_quantitative_measurements_v1.csv", rows)
    write_csv(CAT / "literature_quantitative_coverage_v1.csv", cov)
    make_plots(rows, cov)
    park = sum(r["provenance_layer"] == "park_santamarina_benchmark" for r in rows)
    park_components = len({(r["parent_group_id"], r["component_label"]) for r in rows if r["provenance_layer"] == "park_santamarina_benchmark"})
    scalar = sum(bool(r["value"]) + bool(r["value_min"]) + bool(r["value_max"]) + bool(r["auxiliary_value"]) for r in rows)
    print(f"Literature measurement resource v1: {len(rows)} rows, {scalar} explicit scalar values; {park} Park S2 parameter rows from {park_components} fitted components and {len(rows)-park} other-literature rows.")


if __name__ == "__main__":
    main()
