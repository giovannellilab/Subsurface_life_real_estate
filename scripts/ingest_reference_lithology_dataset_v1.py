"""Build a small, source-preserving Reference Lithology Dataset v1.

This is intentionally a concrete ingestion for the locally acquired M3 records
and three small public data releases.  It keeps pore bodies, throats, MIP entry
equivalents, and connectivity metrics in separate rows rather than attempting
to harmonise them into a universal pore-size distribution.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/m3_acquisitions"
FIRST = ROOT / "data/processed/m3_first_ingestion"
OUT = ROOT / "data/processed/reference_lithology_dataset_v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, fields: list[str], rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader(); writer.writerows(rows)


REGISTRY_FIELDS = [
    "dataset_id", "source_id", "source_title", "source_landing_url", "license",
    "lithology", "sample_id", "sample_state", "method", "geometry_class",
    "quantity_name", "native_size_definition", "native_unit", "weighting_basis",
    "observation_window_or_resolution", "connectivity_available", "inclusion_note",
]
VALUE_FIELDS = [
    "dataset_id", "source_id", "sample_id", "measurement_id", "lithology", "method",
    "geometry_class", "quantity_name", "native_size_definition", "size_raw",
    "size_unit_raw", "size_um", "comparison_dimension", "comparison_diameter_um",
    "comparison_derivation", "comparison_role", "weight_raw", "weighting_basis", "source_locator",
    "observation_window_or_resolution", "qc_flags",
]
CONNECTIVITY_FIELDS = [
    "dataset_id", "source_id", "sample_id", "lithology", "method", "metric_name",
    "value_raw", "value_normalized", "unit", "definition", "source_locator", "qc_flags",
]
ATTRIBUTE_FIELDS = [
    "dataset_id", "source_id", "sample_id", "measurement_id", "geometry_class",
    "object_id_raw", "attribute_name", "value_raw", "unit_raw", "definition",
    "source_locator", "qc_flags",
]
EDGE_FIELDS = [
    "dataset_id", "source_id", "sample_id", "edge_id_raw", "pore1_id_raw",
    "pore2_id_raw", "source_locator", "qc_flags",
]


def add_registry(rows: list[dict], **row: str) -> None:
    rows.append({key: row.get(key, "") for key in REGISTRY_FIELDS})


def add_value(rows: list[dict], **row: str) -> None:
    """Add a native value plus a narrowly defined analytical comparison field.

    The native columns are never altered.  Only records whose source semantics
    explicitly establish a radius or a diameter receive a comparison diameter.
    """
    source = row.get("source_id", "")
    geometry = row.get("geometry_class", "")
    unit = row.get("size_unit_raw", "").lower()
    definition = row.get("native_size_definition", "").lower()
    quantity = row.get("quantity_name", "").lower()
    native_um = row.get("size_um", "")
    dimension = diameter = derivation = role = ""
    if native_um:
        if source == "M3-001" and geometry == "pore_throat":
            dimension = "MIP entry/throat-equivalent comparison diameter"
            diameter = native_um
            derivation = "Source MIP entry/throat-equivalent bin dimension retained; no radius conversion"
            role = "throat_entry_nominal_transit"
        elif source == "M3-023" and quantity == "r" and unit == "nm radius":
            dimension = "modelled matrix-pore-cluster comparison diameter"
            diameter = str(2 * float(native_um))
            derivation = "2 × source modelled W23 R/nm; native radius retained"
            role = "modelled_matrix_pore_cluster_accommodation"
        elif "radius" in unit or "radius" in definition or "eqradius" in quantity:
            dimension = "equivalent comparison diameter"
            diameter = str(2 * float(native_um))
            derivation = "2 × source-reported radius; native radius retained"
            role = "pore_body_accommodation" if geometry == "pore_body" else "throat_entry_nominal_transit" if geometry == "pore_throat" else ""
        elif "diameter" in unit or "diameter" in definition or "eqdiameter" in quantity:
            dimension = "source-reported comparison diameter"
            diameter = native_um
            derivation = "Source-reported diameter retained; no conversion"
            role = "pore_body_accommodation" if geometry == "pore_body" else "throat_entry_nominal_transit" if geometry == "pore_throat" else ""
    row.update({"comparison_dimension": dimension, "comparison_diameter_um": diameter,
                "comparison_derivation": derivation, "comparison_role": role})
    rows.append({key: row.get(key, "") for key in VALUE_FIELDS})


def add_attribute(rows: list[dict], **row: str) -> None:
    rows.append({key: row.get(key, "") for key in ATTRIBUTE_FIELDS})


def add_edge(rows: list[dict], **row: str) -> None:
    rows.append({key: row.get(key, "") for key in EDGE_FIELDS})


def first_ingestion(registry: list[dict], values: list[dict], connectivity: list[dict]) -> None:
    measurements = {r["measurement_id"]: r for r in csv.DictReader((FIRST / "measurements.csv").open())}
    samples = {r["sample_id"]: r for r in csv.DictReader((FIRST / "samples.csv").open())}
    for mid, measurement in measurements.items():
        sample = samples[measurement["sample_id"]]
        if mid.endswith(":mip_intrusion"):
            dataset, lithology = "lipnice_granite_mip", "granite"
            add_registry(registry, dataset_id=dataset, source_id="M3-001", source_title="Lipnice granite MIP", source_landing_url="https://doi.org/10.1594/PANGAEA.898001", license="CC-BY-4.0", lithology=lithology, sample_id=sample["sample_id"], sample_state=sample["sample_state"], method="MIP", geometry_class="pore_throat", quantity_name="incremental intrusion porosity", native_size_definition="MIP entry/throat-equivalent source bin", native_unit="µm", weighting_basis="incremental_intruded_porosity", observation_window_or_resolution=measurement["resolution_or_detection_limit_raw"], connectivity_available="no", inclusion_note="Natural core facies; MIP entry equivalent is retained separately from image-derived throats.")
        elif mid.endswith(":pore_body") or mid.endswith(":pore_throat"):
            dataset, lithology = "fontainebleau_berea_pnm", "sandstone"
            add_registry(registry, dataset_id=dataset, source_id="M3-002", source_title="Fontainebleau/Berea pore-network data", source_landing_url="https://doi.org/10.5281/zenodo.1184144", license="record terms; see source", lithology=lithology, sample_id=sample["sample_id"], sample_state=sample["sample_state"], method="micro_CT_plus_PNM", geometry_class=measurement["geometry_class"], quantity_name="EqRadius", native_size_definition="source EqRadius", native_unit="µm radius", weighting_basis="object_count", observation_window_or_resolution=measurement["resolution_or_detection_limit_raw"], connectivity_available="coordination number for pore bodies", inclusion_note="Cases retained separately; Case3B is oil/water-saturated.")
    for row in csv.DictReader((FIRST / "measurement_distribution.csv").open()):
        m = measurements[row["measurement_id"]]
        add_value(values, dataset_id="lipnice_granite_mip", source_id="M3-001", sample_id=m["sample_id"], measurement_id=row["measurement_id"], lithology="granite", method="MIP", geometry_class="pore_throat", quantity_name="incremental intrusion porosity", native_size_definition="MIP entry/throat-equivalent bin lower edge", size_raw=row["bin_lower_raw"], size_unit_raw="µm", size_um=row["bin_lower_um"], weight_raw=row["value_raw"], weighting_basis="incremental_intruded_porosity", source_locator=row["source_column_raw"], observation_window_or_resolution=m["resolution_or_detection_limit_raw"], qc_flags="entry_equivalent_not_pore_body")
    coordination = defaultdict(lambda: [0.0, 0])
    for row in csv.DictReader((FIRST / "network_objects.csv").open()):
        m = measurements[row["measurement_id"]]
        if not row["radius_um"]:
            continue
        add_value(values, dataset_id="fontainebleau_berea_pnm", source_id="M3-002", sample_id=m["sample_id"], measurement_id=row["measurement_id"], lithology="sandstone", method="micro_CT_plus_PNM", geometry_class=row["geometry_class"], quantity_name="EqRadius", native_size_definition="source EqRadius", size_raw=row["radius_raw"], size_unit_raw="µm radius", size_um=row["radius_um"], weight_raw="1", weighting_basis="object_count", source_locator=f"{row['source_file']}:{row['object_id_raw']}", observation_window_or_resolution=m["resolution_or_detection_limit_raw"], qc_flags="resolved_segmented_network;radius_not_diameter")
        if row["geometry_class"] == "pore_body" and row["coordination_number_raw"]:
            coordination[m["sample_id"]][0] += float(row["coordination_number_raw"])
            coordination[m["sample_id"]][1] += 1
    for sample_id, (total, count) in coordination.items():
        connectivity.append(dict(zip(CONNECTIVITY_FIELDS, ["fontainebleau_berea_pnm", "M3-002", sample_id, "sandstone", "micro_CT_plus_PNM", "mean_pore_coordination_number", f"{total/count:.9g}", f"{total/count:.9g}", "count", "Arithmetic mean of source pore-body Coordination Number; source network definition", "source PNM pore-body tables", "resolved_segmented_network;not a whole-rock connectivity metric"])))


def xlsx_rows(path: Path):
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships", "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
    with zipfile.ZipFile(path) as archive:
        shared = []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        for item in root.findall("x:si", ns):
            shared.append("".join(x.text or "" for x in item.findall(".//x:t", ns)))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in book.find("x:sheets", ns):
            name = sheet.attrib["name"]
            target = targets[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
            root = ET.fromstring(archive.read("xl/" + target))
            rows = []
            for row in root.findall(".//x:sheetData/x:row", ns):
                out = {}
                for cell in row.findall("x:c", ns):
                    col = "".join(c for c in cell.attrib["r"] if c.isalpha())
                    value = cell.find("x:v", ns)
                    text = value.text if value is not None else ""
                    if cell.attrib.get("t") == "s" and text:
                        text = shared[int(text)]
                    out[col] = text
                rows.append(out)
            yield name, rows


def carbonate(registry: list[dict], values: list[dict]) -> None:
    archive = RAW / "mendeley_t8rj6b6gwn/carbonate_pnm_statistics.rar"
    # The raw RAR is immutable; its extracted workbook is a temporary working copy.
    workbook = Path("/tmp/m3_carbonate/X-ray micro CT based characterization of pore-throat network for marine carbonates from the South China Sea.xlsx")
    if not workbook.is_file():
        raise SystemExit("Extract carbonate workbook to /tmp/m3_carbonate before processing.")
    for name, rows in xlsx_rows(workbook):
        if not name.startswith("REV2 of ") or not rows:
            continue
        material = name.removeprefix("REV2 of ")
        lithology = "carbonate" if "Carbonate" in material else "sandstone"
        sample_id = "M3-RLD:" + material.replace(" ", "_")
        for geometry, quantity, radius_col, volume_col, length_col in [
            ("pore_body", "Radius of pore", "B", "C", ""),
            ("pore_throat", "Radius of throat", "I", "J", "H"),
        ]:
            mid = sample_id + ":" + geometry
            add_registry(registry, dataset_id="south_china_sea_carbonate_pnm", source_id="M3-RLD-003", source_title="South China Sea carbonate pore-network statistics", source_landing_url="https://doi.org/10.17632/t8rj6b6gwn.1", license="CC-BY-4.0", lithology=lithology, sample_id=sample_id, sample_state="imaged specimen; state not further reported in workbook", method="micro_CT_plus_PNM", geometry_class=geometry, quantity_name=quantity, native_size_definition="source radius in metres", native_unit="m radius", weighting_basis="object_count", observation_window_or_resolution="micro-CT/maximum-ball network; voxel size not reported in workbook", connectivity_available="pore-throat aspect ratio only; no coordination field", inclusion_note="Pore and throat radii, volume, and throat length are separate source columns.")
            for index, row in enumerate(rows[1:], start=2):
                if not row.get(radius_col, "").strip():
                    continue
                add_value(values, dataset_id="south_china_sea_carbonate_pnm", source_id="M3-RLD-003", sample_id=sample_id, measurement_id=mid, lithology=lithology, method="micro_CT_plus_PNM", geometry_class=geometry, quantity_name=quantity, native_size_definition="source radius", size_raw=row[radius_col], size_unit_raw="m radius", size_um=str(float(row[radius_col]) * 1e6), weight_raw="1", weighting_basis="object_count", source_locator=f"{name}!row{index}", observation_window_or_resolution="micro-CT/maximum-ball network; voxel size not reported in workbook", qc_flags="radius_not_diameter")


def basalt(registry: list[dict], values: list[dict]) -> None:
    path = RAW / "mendeley_n72yhbppkj/Pore_ungrooved_Unreacted_PoresizeDist.csv"
    sample_id = "M3-RLD:unreacted_ungrooved_basalt"
    add_registry(registry, dataset_id="unreacted_basalt_microct", source_id="M3-005", source_title="Basalt pore geometry adjacent to fractures", source_landing_url="https://doi.org/10.17632/n72yhbppkj.1", license="CC-BY-4.0", lithology="basalt_volcanic", sample_id=sample_id, sample_state="unreacted; ungrooved half-core", method="micro_CT_plus_PNM", geometry_class="pore_body", quantity_name="EqDiameter", native_size_definition="source EqDiameter", native_unit="mm diameter (article-defined)", weighting_basis="object_count", observation_window_or_resolution="14.99 µm voxel; manual-threshold micro-CT; resolved pores only", connectivity_available="not retained for this unreacted ungrooved table", inclusion_note="Natural basalt baseline before the CO2-fluid experiment; pore bodies only.")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        next(handle)
        for row in csv.DictReader(handle):
            if not row["EqDiameter"]:
                continue
            add_value(values, dataset_id="unreacted_basalt_microct", source_id="M3-005", sample_id=sample_id, measurement_id=sample_id+":pore_body", lithology="basalt_volcanic", method="micro_CT_plus_PNM", geometry_class="pore_body", quantity_name="EqDiameter", native_size_definition="source EqDiameter", size_raw=row["EqDiameter"], size_unit_raw="mm diameter (article-defined)", size_um=str(float(row["EqDiameter"]) * 1000), weight_raw="1", weighting_basis="object_count", source_locator=f"{path.name}:index={row['index']}", observation_window_or_resolution="14.99 µm voxel; manual-threshold micro-CT; resolved pores only", qc_flags="resolved_pores_only;diameter_not_radius")


def ukgeos(registry: list[dict], values: list[dict], connectivity: list[dict]) -> None:
    path = RAW / "figshare_ukgeos_12707840/UKGEOS_PNM_Paper.zip"
    source = "M3-RLD-004"; dataset = "wilmslow_sandstone_microct_pnm"
    with zipfile.ZipFile(path) as archive:
        porosity = archive.read("UKGEOS_PNM_Paper/overall_GG_SF_poro_perm.csv").decode("utf-8-sig")
        by_sample = {r["sample_id"]: r for r in csv.DictReader(io.StringIO(porosity))}
        for code in [f"SF_{n}" for n in range(696, 703)]:
            sample_id = "M3-RLD:" + code
            summary = by_sample[code]
            for geometry, filename, quantity in [("pore_body", "all_pores.csv", "EqRadius"), ("pore_throat", "all_throats.csv", "EqRadius")]:
                mid = sample_id + ":" + geometry
                add_registry(registry, dataset_id=dataset, source_id=source, source_title="UKGEOS Wilmslow Sandstone pore networks", source_landing_url="https://doi.org/10.17637/rh.12707840", license="CC-BY-4.0", lithology="sandstone", sample_id=sample_id, sample_state="core sample; epoxy impregnated for imaging", method="micro_CT_plus_PNM", geometry_class=geometry, quantity_name=quantity, native_size_definition="source EqRadius", native_unit="µm radius", weighting_basis="object_count; all connected and disconnected objects", observation_window_or_resolution="micro-CT/PerGeos; voxel size not stated in archive readme", connectivity_available="total/effective porosity and permeability", inclusion_note="Wilmslow Sandstone Formation; use all-object geometry with separately reported connected fraction.")
                member = f"UKGEOS_PNM_Paper/{code}/{filename}"
                with io.TextIOWrapper(archive.open(member), encoding="utf-8-sig", newline="") as handle:
                    for row in csv.DictReader(handle):
                        radius = row["EqRadius [um]"]
                        identifier = row["Pore ID"] if geometry == "pore_body" else row["Throat ID"]
                        add_value(values, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, lithology="sandstone", method="micro_CT_plus_PNM", geometry_class=geometry, quantity_name=quantity, native_size_definition="source EqRadius", size_raw=radius, size_unit_raw="µm radius", size_um=radius, weight_raw="1", weighting_basis="object_count", source_locator=f"{code}/{filename}:{identifier}", observation_window_or_resolution="micro-CT/PerGeos; voxel size not stated in archive readme", qc_flags="all_objects_connected_and_disconnected;radius_not_diameter")
            for raw, name, unit, definition in [("total_porosity", "total_porosity", "fraction", "micro-CT measured total porosity"), ("effective_porosity", "connected_porosity", "fraction", "micro-CT measured effective/connected porosity"), ("permeability", "permeability", "source_unit_unreported", "PerGeos-derived permeability; CSV header does not state a unit, so no unit is inferred")]:
                value = summary[raw]
                connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, "sandstone", "micro_CT_plus_PNM", name, value, value, unit, definition, "overall_GG_SF_poro_perm.csv:"+code, "method_and_resolution_conditioned"])))


def docx_tables(path: Path) -> list[list[list[str]]]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    tables = []
    for table in root.findall(".//w:tbl", ns):
        rows = []
        for tr in table.findall("./w:tr", ns):
            rows.append([
                "".join(text.text or "" for text in tc.findall(".//w:t", ns)).strip()
                for tc in tr.findall("./w:tc", ns)
            ])
        tables.append(rows)
    return tables


def harvard_shale(registry: list[dict], values: list[dict], connectivity: list[dict], attributes: list[dict]) -> None:
    """Retain raw CTSTA cluster classes separately from the modelled PSD curve."""
    source = "M3-023"; dataset = "harvard_marine_shale_multiscale"
    raw_dir = RAW / "harvard_d1ldso"
    raw_workbooks = [("W23", raw_dir / "W23_analysis.xlsx"), ("J24", raw_dir / "J24_analysis.xlsx")]
    for source_sample, workbook in raw_workbooks:
        sample_id = f"M3-RLD:{source_sample}_marine_shale"
        mid = sample_id + ":ctsta_pore_cluster_size"
        add_registry(registry, dataset_id=dataset, source_id=source, source_title="Marine shale multi-scale pore structures and connectivity domains", source_landing_url="https://doi.org/10.7910/DVN/WBSHKX", license="CC0-1.0", lithology="mudstone_shale", sample_id=sample_id, sample_state="as supplied", method="CTSTA_digital_core_cluster_analysis", geometry_class="matrix_pore", quantity_name="PORE-SIZE", native_size_definition="source CTSTA connected-pore-cluster size class", native_unit="source size-count unit; no physical length unit supplied", weighting_basis="source FRACTION (cluster-size weighted percentage)", observation_window_or_resolution="CTSTA source table; no image resolution supplied", connectivity_available="source intermediate correlation-length workflow", inclusion_note="PORE-SIZE is not labelled as a pore body, pore throat, radius, or diameter; retain it as a native cluster-size class.")
        for sheet, rows in xlsx_rows(workbook):
            if len(rows) < 3:
                continue
            for index, row in enumerate(rows[2:], start=3):
                if not row.get("A", ""):
                    continue
                locator = f"{workbook.name}:{sheet}!row{index}"
                add_value(values, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, lithology="mudstone_shale", method="CTSTA_digital_core_cluster_analysis", geometry_class="matrix_pore", quantity_name="PORE-SIZE", native_size_definition="source CTSTA connected-pore-cluster size class", size_raw=row["A"], size_unit_raw="source size-count unit", size_um="", weight_raw=row.get("D", ""), weighting_basis="source FRACTION (percent)", source_locator=locator, observation_window_or_resolution="CTSTA source table; no image resolution supplied", qc_flags="native_cluster_size_not_physical_length;not_pore_body_or_throat;normalized_size_unavailable")
                for name, value, unit, definition in [
                    ("source_cluster_count", row.get("B", ""), "count", "Source NUMBERS column: number of clusters in the PORE-SIZE class"),
                    ("source_radius_squared", row.get("C", ""), "source unit unresolved", "Source RADIUS^2 column; raw table does not establish a physical radius or diameter convention"),
                    ("source_accumulated_fraction", row.get("E", ""), "percent", "Source ACC-FRACTION column"),
                ]:
                    add_attribute(attributes, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, geometry_class="matrix_pore", object_id_raw=row["A"], attribute_name=name, value_raw=value, unit_raw=unit, definition=definition, source_locator=locator, qc_flags="native_cluster_analysis;unit_or_geometry_unresolved")
    tables = docx_tables(raw_dir / "intermediate_psd.docx")
    for source_sample, table in zip(["W23", "J24"], tables, strict=True):
        sample_id = f"M3-RLD:{source_sample}_marine_shale"
        mid = sample_id + ":modelled_multiscale_pore_cluster_radius"
        header = table[0]
        radius_is_explicit_nm = source_sample == "W23" and header[0] == "R/nm"
        raw_unit = "nm radius" if radius_is_explicit_nm else "R (unit not stated in J24 source table)"
        window = "source intermediate fractal PSD curve; modelled multi-scale domain"
        add_registry(registry, dataset_id=dataset, source_id=source, source_title="Marine shale multi-scale pore structures and connectivity domains", source_landing_url="https://doi.org/10.7910/DVN/D1LDSO", license="CC0-1.0", lithology="mudstone_shale", sample_id=sample_id, sample_state="as supplied", method="fractal_modelled_multiscale_PSD", geometry_class="matrix_pore", quantity_name="R", native_size_definition="source intermediate modelled pore-cluster radius R", native_unit=raw_unit, weighting_basis="source modelled V/nm3", observation_window_or_resolution=window, connectivity_available="source L(R/rmax) model parameter", inclusion_note="A modelled PSD curve, separate from raw CTSTA cluster classes; it is not a pore-throat distribution. Only W23 labels R explicitly in nm.")
        for index, row in enumerate(table[1:], start=2):
            if not row[0] or not row[9]:
                continue
            locator = f"intermediate_psd.docx:{source_sample}:table_row{index}"
            size_um = str(float(row[0]) / 1000) if radius_is_explicit_nm else ""
            flags = "modelled_multiscale_curve;radius_not_diameter;not_pore_throat"
            if row[9] == "-":
                flags += ";source_missing_weight"
            if not radius_is_explicit_nm:
                flags += ";normalized_size_unavailable"
            add_value(values, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, lithology="mudstone_shale", method="fractal_modelled_multiscale_PSD", geometry_class="matrix_pore", quantity_name="R", native_size_definition="source intermediate modelled pore-cluster radius R", size_raw=row[0], size_unit_raw=raw_unit, size_um=size_um, weight_raw=row[9], weighting_basis="source modelled V/nm3", source_locator=locator, observation_window_or_resolution=window, qc_flags=flags)
            add_attribute(attributes, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, geometry_class="matrix_pore", object_id_raw=row[0], attribute_name="modelled_pore_volume", value_raw=row[9], unit_raw="nm3", definition="Source intermediate PSD table V/nm3 column", source_locator=locator, qc_flags="modelled_multiscale_curve")
            add_attribute(attributes, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=mid, geometry_class="matrix_pore", object_id_raw=row[0], attribute_name="source_L_R_over_rmax", value_raw=row[1], unit_raw="dimensionless", definition="Source L(R/rmax) column; article frames correlation length as a connectivity-domain descriptor; no physical correlation length inferred", source_locator=locator, qc_flags="source_model_parameter;not_network_connectivity")
            connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, "mudstone_shale", "fractal_modelled_multiscale_PSD", "source_L_R_over_rmax", row[1], row[1], "dimensionless", "Source intermediate table L(R/rmax); retain as supplied model parameter, not a graph metric or physical length", locator, "source_model_parameter;not_network_connectivity"])))


def f42a_network(registry: list[dict], values: list[dict], connectivity: list[dict], attributes: list[dict], edges: list[dict]) -> None:
    """Ingest the compact Statoil network, leaving the raw 7z archive untouched."""
    source = "M3-024"; dataset = "f42a_quartz_sand_microct_pnm"; sample_id = "M3-RLD:F42A_quartz_sand_pack"
    archive_path = ROOT / "data/interim/m3_f42a/F42A_NetworkAndResults.zip"
    if not archive_path.is_file():
        raise SystemExit("Extract only F42A_NetworkAndResults.zip from the immutable F42A.7z archive to data/interim/m3_f42a before processing.")
    window = "9.996 µm voxel; 300 cubed micro-CT image; extracted Statoil/maximal-ball network"
    for geometry, quantity in [("pore_body", "pore radius"), ("pore_throat", "throat radius")]:
        add_registry(registry, dataset_id=dataset, source_id=source, source_title="F42A Ottawa quartz sand pack extracted pore network", source_landing_url="https://doi.org/10.6084/m9.figshare.1189259.v1", license="CC-BY-4.0", lithology="unconsolidated_sand", sample_id=sample_id, sample_state="laboratory-packed Ottawa F42 quartz sand", method="micro_CT_plus_PNM", geometry_class=geometry, quantity_name=quantity, native_size_definition="Statoil network source radius", native_unit="m radius", weighting_basis="object_count", observation_window_or_resolution=window, connectivity_available="per-pore coordination and explicit throat topology", inclusion_note="Pore and throat radii remain separate; all source network objects are retained, including zero-coordination pore nodes.")
    with zipfile.ZipFile(archive_path) as archive:
        base = "F42A Summary/"
        nodes = [line.split() for line in archive.read(base + "F42A_node1.dat").decode().splitlines()[1:] if line.strip()]
        node2 = [line.split() for line in archive.read(base + "F42A_node2.dat").decode().splitlines() if line.strip()]
        link1_lines = archive.read(base + "F42A_Link1.dat").decode().splitlines()
        link1 = [line.split() for line in link1_lines[1:] if line.strip()]
        link2 = [line.split() for line in archive.read(base + "F42A_Link2.dat").decode().splitlines() if line.strip()]
        results = archive.read(base + "Results_F42A.txt").decode("latin-1")
    node2_by_id = {row[0]: row for row in node2}
    for row in nodes:
        node_id, coordination = row[0], row[4]
        p2 = node2_by_id[node_id]
        locator = f"F42A_node1.dat/F42A_node2.dat:{node_id}"
        add_value(values, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=sample_id+":pore_body", lithology="unconsolidated_sand", method="micro_CT_plus_PNM", geometry_class="pore_body", quantity_name="pore radius", native_size_definition="Statoil node2 pore.radius", size_raw=p2[2], size_unit_raw="m radius", size_um=str(float(p2[2]) * 1e6), weight_raw="1", weighting_basis="object_count", source_locator=locator, observation_window_or_resolution=window, qc_flags="radius_not_diameter;source_network_node")
        connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, "unconsolidated_sand", "micro_CT_plus_PNM", "pore_coordination_number", coordination, coordination, "count", "Source Statoil node1 coordination number; verified against retained link endpoints", locator, "source_network_node;zero_means_isolated_node"])))
        for name, value, unit, definition in [("pore_volume", p2[1], "m3", "Statoil node2 pore.volume"), ("pore_shape_factor", p2[3], "dimensionless", "Statoil node2 pore.shape_factor"), ("pore_clay_volume", p2[4], "m3", "Statoil node2 pore.clay_volume")]:
            add_attribute(attributes, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=sample_id+":pore_body", geometry_class="pore_body", object_id_raw=node_id, attribute_name=name, value_raw=value, unit_raw=unit, definition=definition, source_locator=locator, qc_flags="source_network_node")
    link2_by_id = {row[0]: row for row in link2}
    boundary_throats = 0
    for row in link1:
        edge_id, pore1, pore2, radius, shape_factor, total_length = row
        l2 = link2_by_id[edge_id]
        locator = f"F42A_Link1.dat/F42A_Link2.dat:{edge_id}"
        if int(pore1) <= 0 or int(pore2) <= 0:
            boundary_throats += 1
        add_value(values, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=sample_id+":pore_throat", lithology="unconsolidated_sand", method="micro_CT_plus_PNM", geometry_class="pore_throat", quantity_name="throat radius", native_size_definition="Statoil link1 throat.radius", size_raw=radius, size_unit_raw="m radius", size_um=str(float(radius) * 1e6), weight_raw="1", weighting_basis="object_count", source_locator=locator, observation_window_or_resolution=window, qc_flags="radius_not_diameter;source_network_throat")
        add_edge(edges, dataset_id=dataset, source_id=source, sample_id=sample_id, edge_id_raw=edge_id, pore1_id_raw=pore1, pore2_id_raw=pore2, source_locator=locator, qc_flags="source_network_topology;boundary_endpoint_if_nonpositive")
        for name, value, unit, definition in [("throat_shape_factor", shape_factor, "dimensionless", "Statoil link1 throat.shape_factor"), ("throat_total_length", total_length, "m", "Statoil link1 throat.total_length"), ("throat_pore1_length", l2[3], "m", "Statoil link2 throat.pore1_length"), ("throat_pore2_length", l2[4], "m", "Statoil link2 throat.pore2_length"), ("throat_channel_length", l2[5], "m", "Statoil link2 throat.length"), ("throat_volume", l2[6], "m3", "Statoil link2 throat.volume"), ("throat_clay_volume", l2[7], "m3", "Statoil link2 throat.clay_volume")]:
            add_attribute(attributes, dataset_id=dataset, source_id=source, sample_id=sample_id, measurement_id=sample_id+":pore_throat", geometry_class="pore_throat", object_id_raw=edge_id, attribute_name=name, value_raw=value, unit_raw=unit, definition=definition, source_locator=locator, qc_flags="source_network_throat")
    def result_value(label: str) -> str:
        for line in results.splitlines():
            if line.startswith(label):
                return line.split()[-1].replace(",", "")
        raise ValueError(f"Missing {label} in F42A results")
    degrees = [int(row[4]) for row in nodes]
    sample_metrics = [
        ("pore_node_count", str(len(nodes)), "count", "Number of source network pore nodes"),
        ("throat_edge_count", str(len(link1)), "count", "Number of source network throats"),
        ("mean_pore_coordination_number", f"{sum(degrees)/len(degrees):.9g}", "count", "Arithmetic mean of source node1 coordination numbers, including zero-coordination nodes"),
        ("isolated_pore_fraction", f"{sum(value == 0 for value in degrees)/len(degrees):.9g}", "fraction", "Fraction of source pore nodes with coordination number zero"),
        ("boundary_throat_count", str(boundary_throats), "count", "Throats with a nonpositive source endpoint identifier"),
        ("image_porosity", result_value("Porosity(%)"), "percent", "Results_F42A image porosity"),
        ("average_permeability", result_value("Avg. K"), "mD", "Results_F42A voxel-image permeability"),
        ("network_permeability", result_value("Network K"), "mD", "Results_F42A extracted-network permeability"),
        ("average_formation_factor", result_value("Avg. FF"), "dimensionless", "Results_F42A voxel-image formation factor"),
        ("network_formation_factor", result_value("Network FF"), "dimensionless", "Results_F42A extracted-network formation factor"),
    ]
    for name, value, unit, definition in sample_metrics:
        normalized = str(float(value) / 100) if name == "image_porosity" else value
        connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, "unconsolidated_sand", "micro_CT_plus_PNM", name, value, normalized, unit, definition, "Results_F42A.txt or source network files", "source_network_metric;method_and_resolution_conditioned"])))


def pangaea_rows(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = next(index for index, line in enumerate(lines) if line.startswith("Event\t"))
    return list(csv.DictReader(lines[header:], delimiter="\t"))


def canonical_sample_label(value: str) -> str:
    # Table 2 writes the IODP hole as 304-U1309*, while Table 1 writes the
    # same source sample as 304-1309*.  This is an identifier-only join
    # normalization; the original label remains in the source locator.
    return value.replace("304-U1309", "304-1309").replace(" - ", "-").replace(",", "_").replace(" ", "")


def pangaea_atlantis(registry: list[dict], connectivity: list[dict]) -> None:
    source = "M3-025"; dataset = "atlantis_massif_transport_properties"
    base = ROOT / "data/interim/m3_pangaea_873535/datasets"
    descriptions = pangaea_rows(base / "Exp357_rock-desc.tab")
    physical = pangaea_rows(base / "Exp357_rock-physical.tab")
    by_label = {canonical_sample_label(row["Sample label"]): row for row in descriptions}
    for source_label, description in sorted(by_label.items()):
        lithology_raw = description["Lithology"]
        lithology = "serpentinized_ultramafic" if "serpentinised" in lithology_raw else "mafic_crystalline"
        sample_id = "M3-RLD:" + source_label
        add_registry(registry, dataset_id=dataset, source_id=source, source_title="Atlantis Massif physical properties under confining pressure", source_landing_url="https://doi.pangaea.de/10.1594/PANGAEA.873535", license="CC-BY-3.0", lithology=lithology, sample_id=sample_id, sample_state="natural drilled core", method="wet_dry_bulk_porosity_plus_pressure_dependent_transport", geometry_class="mixed_or_unresolved", quantity_name="bulk porosity and pressure-dependent transport", native_size_definition="not applicable: no pore-size distribution", native_unit="not applicable", weighting_basis="not applicable", observation_window_or_resolution="no pore-size observation window reported", connectivity_available="bulk porosity, permeability, electrical resistivity", inclusion_note=f"Source lithology: {lithology_raw}. Connectivity/transport-only record; never treat as a pore or throat distribution.")
        locator = "Exp357_rock-desc.tab:" + description["Sample label"]
        for name, raw, normalized, unit, definition in [("bulk_porosity", description["Poros [% vol]"], str(float(description["Poros [% vol]"]) / 100), "percent", "Wet-dry-weight-derived bulk porosity; normalized value is fraction"), ("bulk_density", description["Density [g/cm**3]"], description["Density [g/cm**3]"], "g/cm3", "Source bulk density")]:
            connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, lithology, "wet_dry_bulk_porosity_plus_pressure_dependent_transport", name, raw, normalized, unit, definition, locator, "source_bulk_measurement;not_pore_size"])))
    for index, row in enumerate(physical, start=2):
        source_label = canonical_sample_label(row["Sample label"])
        description = by_label[source_label]
        lithology = "serpentinized_ultramafic" if "serpentinised" in description["Lithology"] else "mafic_crystalline"
        sample_id = "M3-RLD:" + source_label
        condition = f"confining_pressure={row['P [MPa] (confining pressure)']} MPa;pore_pressure={row['P [MPa] (pore pressure)']} MPa"
        locator = f"Exp357_rock-physical.tab:row{index};{condition}"
        metrics = [
            ("permeability", row["k [10**-12 m**2]"], str(float(row["k [10**-12 m**2]"]) * 1e-12) if row["k [10**-12 m**2]"] else "", "10^-12 m2", "Source permeability; normalized value is m2"),
            ("electrical_resistivity", row["Resist electr [Ohm m]"], row["Resist electr [Ohm m]"], "Ohm m", "Source electrical resistivity"),
            ("p_wave_velocity", row["Vp [m/s]"], row["Vp [m/s]"], "m/s (source header)", "Source Vp; magnitude is retained without unit reinterpretation"),
            ("s_wave_velocity", row["Vs [m/s]"], row["Vs [m/s]"], "m/s (source header)", "Source Vs; magnitude is retained without unit reinterpretation"),
            ("p_wave_compression_flag", row["Compression Flag (of p-wave)"], row["Compression Flag (of p-wave)"], "source flag", "Source P-wave compression flag"),
            ("s_wave_compression_flag", row["Compression Flag (of s-wave)"], row["Compression Flag (of s-wave)"], "source flag", "Source S-wave compression flag"),
        ]
        for name, raw, normalized, unit, definition in metrics:
            if raw:
                connectivity.append(dict(zip(CONNECTIVITY_FIELDS, [dataset, source, sample_id, lithology, "pressure_dependent_transport", name, raw, normalized, unit, definition + "; " + condition, locator, "source_pressure_series;not_pore_size"])))


def provenance() -> list[dict]:
    sources = [
        ("M3-001", "pangaea_898001/pangaea_898001.tab", "https://doi.org/10.1594/PANGAEA.898001", "CC-BY-4.0"),
        ("M3-002", "zenodo_1184144/*.csv", "https://doi.org/10.5281/zenodo.1184144", "record terms; see source"),
        ("M3-RLD-003", "mendeley_t8rj6b6gwn/carbonate_pnm_statistics.rar", "https://doi.org/10.17632/t8rj6b6gwn.1", "CC-BY-4.0"),
        ("M3-005", "mendeley_n72yhbppkj/Pore_ungrooved_Unreacted_PoresizeDist.csv", "https://doi.org/10.17632/n72yhbppkj.1", "CC-BY-4.0"),
        ("M3-RLD-004", "figshare_ukgeos_12707840/UKGEOS_PNM_Paper.zip", "https://doi.org/10.17637/rh.12707840", "CC-BY-4.0"),
        ("M3-023", "harvard_wbshkx/J24_R-S.tab;harvard_wbshkx/J24_R-n.tab;harvard_wbshkx/W23_R-n.tab;harvard_wbshkx/W23_R-S.xlsx;harvard_wbshkx/PLS.docx", "https://doi.org/10.7910/DVN/WBSHKX", "CC0-1.0"),
        ("M3-023-companion", "harvard_d1ldso/J24_analysis.xlsx;harvard_d1ldso/W23_analysis.xlsx;harvard_d1ldso/intermediate_psd.docx", "https://doi.org/10.7910/DVN/D1LDSO", "CC0-1.0"),
        ("M3-024", "figshare_f42a/F42A.7z", "https://doi.org/10.6084/m9.figshare.1189259.v1", "CC-BY-4.0"),
        ("M3-025", "pangaea_873535/PANGAEA_873535.zip", "https://doi.pangaea.de/10.1594/PANGAEA.873535", "CC-BY-3.0"),
    ]
    rows=[]
    for sid, locators, url, license_ in sources:
        paths = sorted((RAW / "zenodo_1184144").glob("*.csv")) if sid == "M3-002" else [RAW / piece.strip() for piece in locators.split(";")]
        rows.append({"source_id":sid,"landing_url":url,"license":license_,"raw_locator":locators,"raw_sha256":";".join(sha256(p) for p in paths),"retrieval_or_existing_local":"local immutable acquisition; see first-ingestion manifest where applicable"})
    return rows


def main() -> None:
    registry: list[dict] = []; values: list[dict] = []; connectivity: list[dict] = []
    attributes: list[dict] = []; edges: list[dict] = []
    first_ingestion(registry, values, connectivity); carbonate(registry, values); basalt(registry, values); ukgeos(registry, values, connectivity)
    harvard_shale(registry, values, connectivity, attributes)
    f42a_network(registry, values, connectivity, attributes, edges)
    pangaea_atlantis(registry, connectivity)
    write("reference_lithology_dataset_v1.csv", REGISTRY_FIELDS, registry)
    write("geometry_values.csv", VALUE_FIELDS, values)
    write("connectivity_metrics.csv", CONNECTIVITY_FIELDS, connectivity)
    write("source_measurement_attributes.csv", ATTRIBUTE_FIELDS, attributes)
    write("network_edges.csv", EDGE_FIELDS, edges)
    write("source_provenance.csv", ["source_id","landing_url","license","raw_locator","raw_sha256","retrieval_or_existing_local"], provenance())
    manifest={"run_utc":datetime.now(timezone.utc).isoformat(),"registry_rows":len(registry),"geometry_rows":len(values),"connectivity_rows":len(connectivity),"attribute_rows":len(attributes),"edge_rows":len(edges),"design":"Representative method-labelled v1; geometry classes remain separate; raw third-party files remain immutable and gitignored."}
    (OUT / "processing_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
