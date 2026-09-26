"""Versioned scientific-QC overlays for the immutable 2026-09-14 census.

This module never rewrites raw or normalized source values.  Its outputs name
each analytical layer explicitly: source-normalized, manually verified overlay,
and conservative species-level canonical value.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import io
import json
import math
import os
from pathlib import Path
import re
from statistics import fmean, median, stdev

os.environ.setdefault("MPLCONFIGDIR", "/tmp/subsurface-life-real-estate-mpl")

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

from .acquisition import digest, json_bytes
from .plotting import viridis_colors


COMPLEX_CLASSES = {
    "pleomorphic", "filamentous", "branched", "stalked_appendaged",
    "aggregate_chain_forming", "spore_related_measurement",
    "multiple_conflicting_observations", "ambiguous_or_unparsable",
}
THRESHOLDS = (0.2, 0.3, 0.5, 1.0, 2.0, 5.0)
PERCENTILES = (1, 5, 10, 25, 50, 75, 90, 95, 99)

# Manually verified primary-description overlays.  These are intentionally few:
# every other suspect stays uncorrected until a source value is independently
# available.  The source quotation is a structured transcription, not a copy of
# the source document.
MANUAL_VERIFICATIONS = {
    "140751:0": {
        "source_used": "Original species description / protologue (accessible full-text copy)",
        "source_identifier": "doi:10.1099/ijsem.0.002298",
        "source_url": "https://www.researchgate.net/publication/319405575_Croceitalea_marina_sp_nov_isolated_from_marine_particles_of_Yellow_Sea_and_emended_description_of_the_genera_Croceitalea",
        "source_value": "Cells are rods, 0.4–0.6 µm wide and 1.4–3.0 µm long.",
        "outcome": "corrected_unit", "corrected_width_min_um": 0.4,
        "corrected_width_max_um": 0.6, "corrected_length_min_um": 1.4,
        "corrected_length_max_um": 3.0,
        "reason": "The protologue states µm; the immutable BacDive source row states nm.",
        "confidence": "high",
        "reviewer_note": "Analytical overlay only; raw BacDive value remains unchanged.",
    },
    "141099:0": {
        "source_used": "Original species description / protologue (accessible full-text copy)",
        "source_identifier": "doi:10.1099/ijsem.0.002442",
        "source_url": "https://www.researchgate.net/publication/320574229_Nioella_aestuarii_sp_nov_of_the_family_Rhodobacteraceae_isolated_from_tidal_flat",
        "source_value": "Cells are rods, 0.8–1.0 µm wide and 1.8–2.0 µm long.",
        "outcome": "corrected_unit", "corrected_width_min_um": 0.8,
        "corrected_width_max_um": 1.0, "corrected_length_min_um": 1.8,
        "corrected_length_max_um": 2.0,
        "reason": "The protologue states µm; the immutable BacDive source row states mm.",
        "confidence": "high",
        "reviewer_note": "Analytical overlay only; raw BacDive value remains unchanged.",
    },
}


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _csv_bytes(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True)
                         if isinstance(value, (dict, list)) else value
                         for key, value in row.items()})
    return stream.getvalue().encode("utf-8")


def _write(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def _raw_units(row: dict, axis: str) -> str:
    return " ".join(str(row.get(key) or "") for key in
                    (f"cell_{axis}_raw", f"cell_{axis}_unit_raw")).lower()


def _has_unit(text: str, abbreviation: str, word: str) -> bool:
    return bool(re.search(rf"(?<![a-z]){abbreviation}(?![a-z])|{word}", text))


def eligibility(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return eligible source observations and a row for every excluded width."""
    eligible, excluded = [], []
    for row in rows:
        if row.get("width_min_um") is None:
            continue
        blocking = sorted(COMPLEX_CLASSES & set(row.get("morphology_classes", [])))
        if not blocking:
            eligible.append(row)
            continue
        excluded.append({
            "observation_id": row["observation_id"], "bacdive_id": row["bacdive_id"],
            "species_name_raw_bacdive": row.get("species_name"),
            "raw_morphology": json.dumps(row.get("morphology_observation_raw"), ensure_ascii=False),
            "cell_shape_raw": row.get("cell_shape_raw"),
            "cell_length_raw": row.get("cell_length_raw"), "cell_width_raw": row.get("cell_width_raw"),
            "length_min_um": row.get("length_min_um"), "length_max_um": row.get("length_max_um"),
            "width_min_um": row.get("width_min_um"), "width_max_um": row.get("width_max_um"),
            "morphology_classes": row.get("morphology_classes", []), "qc_flags": row.get("qc_flag", []),
            "exclusion_reason": [f"provisional_{label}" for label in blocking],
            "eligibility_definition": "Parsed width excluded because a provisional complex, conflicting, or ambiguous morphology class is present.",
        })
    return eligible, excluded


def suspect_reasons(row: dict) -> list[str]:
    """Non-destructive triggers for source verification, across both axes."""
    width, length = _raw_units(row, "width"), _raw_units(row, "length")
    reasons = []
    if _has_unit(width, "nm", "nanomet") or _has_unit(length, "nm", "nanomet"):
        reasons.append("source_unit_nm")
    if _has_unit(width, "mm", "millimet") or _has_unit(length, "mm", "millimet"):
        reasons.append("source_unit_mm")
    if row.get("width_min_um") is not None and row["width_min_um"] < 0.1:
        reasons.append("width_below_0_1_um")
    if row.get("width_max_um") is not None and row["width_max_um"] > 5:
        reasons.append("width_above_5_um")
    if row.get("length_max_um") is not None and row["length_max_um"] > 50:
        reasons.append("length_above_50_um")
    if (row.get("width_min_um") is not None and row.get("length_max_um") is not None
            and row["width_min_um"] > row["length_max_um"]):
        reasons.append("width_exceeds_length")
    if any(flag.endswith("_extreme_review") or flag == "width_exceeds_length_review"
           for flag in row.get("qc_flag", [])):
        reasons.append("existing_extreme_scale_flag")
    if ((row.get("width_min_um") is not None or row.get("length_min_um") is not None)
            and COMPLEX_CLASSES & set(row.get("morphology_classes", []))):
        reasons.append("complex_morphology_dimension_context")
    return reasons


def _reference(row: dict) -> tuple[str | None, str | None]:
    for item in row.get("source_reference", []):
        identifier = item.get("doi/url") or item.get("pubmed")
        if identifier:
            return str(identifier), item.get("title")
    return None, None


def verification_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Create all-review and correction-only overlays without source mutation."""
    reviews, corrections = [], []
    for row in rows:
        reasons = suspect_reasons(row)
        if not reasons:
            continue
        source_id, title = _reference(row)
        manual = MANUAL_VERIFICATIONS.get(row["observation_id"])
        if manual:
            review = dict(manual)
        else:
            review = {
                "source_used": "BacDive cited-reference metadata; primary text not independently verified in this run",
                "source_identifier": source_id,
                "source_url": None,
                "source_value": None,
                "outcome": "unresolved" if source_id else "source_unavailable",
                "corrected_width_min_um": None, "corrected_width_max_um": None,
                "corrected_length_min_um": None, "corrected_length_max_um": None,
                "reason": "Automated triage identified a review trigger; no analytical replacement is justified without a verified source value.",
                "confidence": "low",
                "reviewer_note": "Raw and normalized BacDive values are retained unchanged.",
            }
        result = {
            "observation_id": row["observation_id"], "bacdive_id": row["bacdive_id"],
            "species_name_raw_bacdive": row.get("species_name"),
            "review_triggers": reasons, "cell_shape_raw": row.get("cell_shape_raw"),
            "cell_length_raw": row.get("cell_length_raw"), "cell_length_unit_raw": row.get("cell_length_unit_raw"),
            "cell_width_raw": row.get("cell_width_raw"), "cell_width_unit_raw": row.get("cell_width_unit_raw"),
            "source_normalized_length_min_um": row.get("length_min_um"),
            "source_normalized_length_max_um": row.get("length_max_um"),
            "source_normalized_width_min_um": row.get("width_min_um"),
            "source_normalized_width_max_um": row.get("width_max_um"),
            "morphology_classes": row.get("morphology_classes", []), "qc_flags": row.get("qc_flag", []),
            "bacdive_source_references": row.get("source_reference", []),
            "cited_reference_title": title, **review,
        }
        reviews.append(result)
        if manual:
            corrections.append(result)
    return reviews, corrections


def _embedded_taxonomy(row: dict) -> dict:
    embedded = row.get("lpsn_cross_reference") or {}
    raw = row.get("taxonomy_raw") or {}
    source = "bacdive_embedded_lpsn" if embedded else "bacdive_original_fallback"
    flags = []
    if embedded and raw.get("species") and embedded.get("species") and raw["species"] != embedded["species"]:
        flags.append("embedded_lpsn_species_differs_from_bacdive_original")
    values = {}
    for key in ("domain", "phylum", "class", "order", "family", "genus"):
        values[key] = embedded.get(key) or raw.get(key)
        if not values[key]:
            flags.append(f"harmonized_{key}_unavailable")
    if values["domain"] not in {"Bacteria", "Archaea"}:
        flags.append("harmonized_domain_unconfirmed")
    accepted = row.get("lpsn_linked_name") or row.get("lpsn_csv_name") or row.get("species_name")
    if row.get("nomenclature_validation_status") in {"name_unmatched", "name_ambiguous"}:
        flags.append("accepted_name_unconfirmed")
    if row.get("lpsn_linked_name"):
        accepted_source = "lpsn_record_link"
    elif row.get("lpsn_csv_name"):
        accepted_source = "lpsn_exact_name_match"
    else:
        accepted_source = "bacdive_original_fallback"
    return {"accepted_species_name": accepted, "accepted_name_source": accepted_source,
            "taxonomy_source": source, "taxonomy_flags": sorted(flags), **values}


def harmonized_taxonomy(rows: list[dict]) -> tuple[dict[str, dict], list[dict]]:
    """One preserved-hierarchy row per BacDive strain."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["bacdive_id"]].append(row)
    mapping, output = {}, []
    for bid, rr in sorted(grouped.items(), key=lambda item: int(item[0])):
        row = rr[0]
        harmonized = _embedded_taxonomy(row)
        result = {
            "bacdive_id": bid, "species_name_raw_bacdive": row.get("species_name"),
            "lpsn_matched_name": row.get("lpsn_csv_name"), "lpsn_linked_current_name": row.get("lpsn_linked_name"),
            "nomenclature_validation_status": row.get("nomenclature_validation_status"),
            "lpsn_status_raw": row.get("lpsn_csv_status_raw"),
            "original_bacdive_domain": (row.get("taxonomy_raw") or {}).get("domain"),
            "original_bacdive_phylum": (row.get("taxonomy_raw") or {}).get("phylum"),
            "original_bacdive_class": (row.get("taxonomy_raw") or {}).get("class"),
            "original_bacdive_order": (row.get("taxonomy_raw") or {}).get("order"),
            "original_bacdive_family": (row.get("taxonomy_raw") or {}).get("family"),
            "original_bacdive_genus": (row.get("taxonomy_raw") or {}).get("genus"),
            **{f"harmonized_{key}": value for key, value in harmonized.items()
               if key in {"domain", "phylum", "class", "order", "family", "genus"}},
            "accepted_species_name": harmonized["accepted_species_name"],
            "accepted_name_source": harmonized["accepted_name_source"],
            "taxonomy_source": harmonized["taxonomy_source"], "taxonomy_flags": harmonized["taxonomy_flags"],
        }
        mapping[bid] = result
        output.append(result)
    return mapping, output


def _shape_category(value: object) -> str:
    text = str(value or "").lower()
    if not text:
        return "unusual_or_unresolved"
    if re.search(r"filament|hypha|mycel", text): return "filamentous"
    if "branch" in text: return "branched"
    if re.search(r"spir|helic", text): return "spiral_or_helical"
    if "vibrio" in text: return "vibrio"
    if re.search(r"curved|curve", text): return "curved_rod"
    if re.search(r"cocc|spher", text): return "coccoid_or_spherical"
    if re.search(r"rod|bacill", text): return "rod"
    if re.search(r"pleomorph|variable", text): return "pleomorphic"
    return "unusual_or_unresolved"


def _primary_description(row: dict) -> bool:
    species = str(row.get("species_name") or "").lower().split()
    for reference in row.get("source_reference", []):
        title = str(reference.get("title") or "").lower()
        if "sp. nov" in title and all(part in title for part in species[:2]):
            return True
    return False


def _canonical_category(row: dict, corrections: dict[str, dict]) -> tuple[int, str]:
    correction = corrections.get(row["observation_id"])
    if correction and correction["confidence"] == "high":
        return 0, "verified_primary_description"
    if _primary_description(row):
        return 1, "likely_primary_species_description_from_citation_title"
    if _reference(row)[0]:
        return 2, "bacdive_structured_morphology_with_cited_reference"
    return 3, "unresolved_no_cited_morphology_source"


def _corrected(row: dict, correction: dict | None) -> dict:
    values = {axis: row.get(axis) for axis in (
        "width_min_um", "width_max_um", "length_min_um", "length_max_um")}
    if correction and correction["confidence"] == "high":
        for axis in values:
            if correction.get(f"corrected_{axis}") is not None:
                values[axis] = correction[f"corrected_{axis}"]
    return values


def species_table(rows: list[dict], mapping: dict[str, dict], eligible: list[dict], corrections: list[dict]) -> list[dict]:
    """Build one analytical row per harmonized species without averaging."""
    overlays = {row["observation_id"]: row for row in corrections}
    all_species, candidates = defaultdict(list), defaultdict(list)
    for row in rows:
        all_species[mapping[row["bacdive_id"]]["accepted_species_name"]].append(row)
    for row in eligible:
        candidates[mapping[row["bacdive_id"]]["accepted_species_name"]].append(row)
    output = []
    for species in sorted(all_species, key=lambda value: (str(value).lower(), str(value))):
        source_rows = all_species[species]
        candidate_rows = candidates[species]
        bids = sorted({row["bacdive_id"] for row in source_rows}, key=int)
        candidate_details = []
        for row in candidate_rows:
            priority, category = _canonical_category(row, overlays)
            corrected = _corrected(row, overlays.get(row["observation_id"]))
            source_id, _ = _reference(row)
            candidate_details.append((priority, category, row, corrected, source_id))
        canonical, reason = None, "no_analysis_eligible_numerical_width"
        if candidate_details:
            best = min(item[0] for item in candidate_details)
            finalists = [item for item in candidate_details if item[0] == best]
            signatures = {(item[3]["width_min_um"], item[3]["width_max_um"], item[3]["length_min_um"], item[3]["length_max_um"])
                          for item in finalists}
            if len(signatures) == 1:
                canonical = sorted(finalists, key=lambda item: item[2]["observation_id"])[0]
                reason = "unique_best_priority_values" if len(finalists) == 1 else "identical_best_priority_values"
            else:
                reason = "multiple_nonidentical_best_priority_observations"
        tax_rows = [mapping[bid] for bid in bids]
        taxonomy_flags = sorted({flag for tax in tax_rows for flag in tax["taxonomy_flags"]})
        row = {
            "accepted_species_name": species, "bacdive_ids": bids,
            "bacdive_type_strain_record_count": len(bids),
            "source_morphology_observation_count": sum(value["observation_present"] for value in source_rows),
            "analysis_eligible_width_observation_count": len(candidate_rows),
            "canonical_selection_status": "canonical" if canonical else "unresolved",
            "canonical_selection_reason": reason,
            "canonical_source_category": canonical[1] if canonical else None,
            "canonical_source_identifier": canonical[4] if canonical else None,
            "canonical_observation_id": canonical[2]["observation_id"] if canonical else None,
            "canonical_bacdive_id": canonical[2]["bacdive_id"] if canonical else None,
            "shape_raw": canonical[2]["cell_shape_raw"] if canonical else None,
            "shape_category": _shape_category(canonical[2]["cell_shape_raw"]) if canonical else "unusual_or_unresolved",
            "source_width_min_um": canonical[2]["width_min_um"] if canonical else None,
            "source_width_max_um": canonical[2]["width_max_um"] if canonical else None,
            "source_length_min_um": canonical[2]["length_min_um"] if canonical else None,
            "source_length_max_um": canonical[2]["length_max_um"] if canonical else None,
            "corrected_width_min_um": canonical[3]["width_min_um"] if canonical else None,
            "corrected_width_max_um": canonical[3]["width_max_um"] if canonical else None,
            "corrected_length_min_um": canonical[3]["length_min_um"] if canonical else None,
            "corrected_length_max_um": canonical[3]["length_max_um"] if canonical else None,
            "correction_status": (canonical and overlays.get(canonical[2]["observation_id"], {}).get("outcome")) or "uncorrected",
            "correction_confidence": (canonical and overlays.get(canonical[2]["observation_id"], {}).get("confidence")) or None,
            "canonical_nomenclature_validation_status": canonical[2]["nomenclature_validation_status"] if canonical else None,
            "nomenclature_confidence": sorted({tax["nomenclature_validation_status"] for tax in tax_rows}),
            "harmonized_domain": sorted({tax["harmonized_domain"] for tax in tax_rows if tax["harmonized_domain"]}),
            "harmonized_phylum": sorted({tax["harmonized_phylum"] for tax in tax_rows if tax["harmonized_phylum"]}),
            "taxonomy_flags": taxonomy_flags,
            "canonical_qc_flags": canonical[2]["qc_flag"] if canonical else [],
            "canonical_morphology_classes": canonical[2]["morphology_classes"] if canonical else [],
        }
        if canonical:
            row["source_width_midpoint_um"] = (row["source_width_min_um"] + row["source_width_max_um"]) / 2
            row["corrected_width_midpoint_um"] = (row["corrected_width_min_um"] + row["corrected_width_max_um"]) / 2
            row["source_length_midpoint_um"] = (row["source_length_min_um"] + row["source_length_max_um"]) / 2 if row["source_length_min_um"] is not None else None
            row["corrected_length_midpoint_um"] = (row["corrected_length_min_um"] + row["corrected_length_max_um"]) / 2 if row["corrected_length_min_um"] is not None else None
        else:
            for key in ("source_width_midpoint_um", "corrected_width_midpoint_um", "source_length_midpoint_um", "corrected_length_midpoint_um"):
                row[key] = None
        output.append(row)
    return output


def _summary(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "minimum": None, "maximum": None, "mean": None, "median": None,
                "standard_deviation": None, "percentiles": {},
                "fractions_at_or_below": {str(value): None for value in THRESHOLDS}}
    array = np.asarray(values, dtype=float)
    return {"n": len(values), "minimum": float(array.min()), "maximum": float(array.max()),
            "mean": float(fmean(values)), "median": float(median(values)),
            "standard_deviation": float(stdev(values)) if len(values) > 1 else 0.0,
            "percentiles": {str(value): float(np.percentile(array, value)) for value in PERCENTILES},
            "fractions_at_or_below": {str(value): float((array <= value).mean()) for value in THRESHOLDS}}


def _domain(species: dict) -> str:
    values = set(species.get("harmonized_domain", []))
    return next(iter(values)) if len(values) == 1 else "unreported"


def species_distributions(species: list[dict], variant: str) -> tuple[dict, list[dict]]:
    """Return three species-weighted distributions and long-form ECDF rows."""
    prefix = "source" if variant == "uncorrected" else "corrected"
    selected = [row for row in species if row["canonical_selection_status"] == "canonical"]
    if variant == "formal_name_and_type_verified_corrections":
        selected = [row for row in selected
                    if row["canonical_nomenclature_validation_status"] == "validated_name_and_type"]
        prefix = "corrected"
    if variant == "primary_only":
        selected = [row for row in selected if row["canonical_source_category"] in {
            "verified_primary_description", "likely_primary_species_description_from_citation_title"}]
        prefix = "corrected"
    measures = {"width_min_um": f"{prefix}_width_min_um",
                "width_midpoint_um": f"{prefix}_width_midpoint_um",
                "width_max_um": f"{prefix}_width_max_um"}
    distributions, ecdf = {}, []
    for label, key in measures.items():
        values = [row for row in selected if row.get(key) is not None]
        distributions[label] = {
            "all_prokaryotes": _summary([row[key] for row in values]),
            "Bacteria": _summary([row[key] for row in values if _domain(row) == "Bacteria"]),
            "Archaea": _summary([row[key] for row in values if _domain(row) == "Archaea"]),
            "analytical_variant": variant,
            "unit": "species-level canonical values; one row per accepted/harmonized species",
        }
        for rank, row in enumerate(sorted(values, key=lambda item: (item[key], item["accepted_species_name"])), 1):
            ecdf.append({"analytical_variant": variant, "measure": label,
                         "accepted_species_name": row["accepted_species_name"], "value_um": row[key],
                         "species_rank": rank, "ecdf": rank / len(values),
                         "canonical_source_category": row["canonical_source_category"]})
    return distributions, ecdf


def _cramers_v(table: np.ndarray, statistic: float) -> float | None:
    denominator = table.sum() * min(table.shape[0] - 1, table.shape[1] - 1)
    return float(math.sqrt(statistic / denominator)) if denominator else None


def reporting_bias(rows: list[dict], mapping: dict[str, dict]) -> tuple[list[dict], dict]:
    """Recalculate coverage using the harmonized, explicitly sourced taxonomy."""
    strains = defaultdict(list)
    for row in rows:
        strains[row["bacdive_id"]].append(row)
    groups = defaultdict(list)
    for bid, rr in strains.items():
        phylum = mapping[bid]["harmonized_phylum"] or "unreported"
        groups[phylum].append(rr)
    retained = {group: values for group, values in groups.items() if len(values) >= 50}
    other = [entry for group, values in groups.items() if group not in retained for entry in values]
    if other:
        retained["Other / small groups"] = other
    coverage = []
    for group, records in sorted(retained.items()):
        total = len(records)
        morphology = sum(any(row["observation_present"] for row in record) for record in records)
        width = sum(any(row["width_min_um"] is not None for row in record) for record in records)
        coverage.append({"rank": "harmonized_phylum", "group": group, "eligible_type_strains": total,
                         "with_any_structured_morphology": morphology,
                         "with_normalized_width": width,
                         "morphology_coverage_fraction": morphology / total,
                         "width_coverage_fraction": width / total})
    table = np.array([[row["with_any_structured_morphology"], row["eligible_type_strains"] - row["with_any_structured_morphology"]]
                      for row in coverage], dtype=int)
    result = {"taxonomy_basis": "BacDive embedded LPSN hierarchy when present; original BacDive fallback otherwise",
              "minimum_phylum_group_size": 50, "groups": len(coverage),
              "interpretation": "Descriptive source-coverage association; no biological or causal interpretation."}
    if len(table) >= 2 and np.all(table.sum(axis=0) > 0):
        test = chi2_contingency(table, correction=False)
        result.update({"chi_square": float(test.statistic), "degrees_of_freedom": int(test.dof),
                       "p_value": float(test.pvalue), "cramers_v": _cramers_v(table, test.statistic),
                       "minimum_expected_frequency": float(test.expected_freq.min())})
    domains = defaultdict(list)
    for bid, rr in strains.items():
        domains[mapping[bid]["harmonized_domain"] or "unreported"].append(rr)
    result["domain_coverage"] = {domain: {"strains": len(records),
        "with_any_structured_morphology": sum(any(row["observation_present"] for row in record) for record in records),
        "with_normalized_width": sum(any(row["width_min_um"] is not None for row in record) for record in records)}
        for domain, records in sorted(domains.items())}
    return coverage, result


def _year(row: dict) -> int | None:
    raw = row.get("lpsn_csv_row_raw") or {}
    years = re.findall(r"(?:18|19|20)\d{2}", str(raw.get("authors") or ""))
    return int(years[0]) if years else None


def publication_year_bias(rows: list[dict], mapping: dict[str, dict]) -> dict:
    """Exploratory, explicitly low-confidence age/coverage association."""
    strains = defaultdict(list)
    for row in rows:
        strains[row["bacdive_id"]].append(row)
    observations = []
    for bid, records in strains.items():
        year = _year(records[0])
        if year is not None:
            observations.append((year, int(any(row["observation_present"] for row in records)), bid))
    by_decade = defaultdict(lambda: [0, 0])
    for year, available, _ in observations:
        bucket = f"{year // 10 * 10}s"
        by_decade[bucket][0] += 1; by_decade[bucket][1] += available
    result = {"year_basis": "first four-digit year in matched local LPSN author string; not independently verified as description/publication year",
              "usable_strains": len(observations),
              "decade_coverage": [{"decade": decade, "strains": values[0], "with_morphology": values[1],
                                    "coverage_fraction": values[1] / values[0]}
                                   for decade, values in sorted(by_decade.items())]}
    if len(observations) >= 3 and len({available for _, available, _ in observations}) == 2:
        stat = spearmanr([year for year, _, _ in observations], [available for _, available, _ in observations])
        result["spearman_year_vs_morphology_availability"] = {"rho": float(stat.statistic), "p_value": float(stat.pvalue)}
    return result


def morphology_summary(rows: list[dict], eligible: list[dict]) -> list[dict]:
    grouped = defaultdict(lambda: {"observation_rows": 0, "with_numeric_width": 0, "analysis_eligible_width": 0})
    eligible_ids = {row["observation_id"] for row in eligible}
    for row in rows:
        category = _shape_category(row.get("cell_shape_raw"))
        group = grouped[category]
        group["observation_rows"] += 1
        group["with_numeric_width"] += int(row.get("width_min_um") is not None)
        group["analysis_eligible_width"] += int(row["observation_id"] in eligible_ids)
    notes = {
        "coccoid_or_spherical": "Potentially eligible for a later cross-sectional width model.",
        "rod": "Potentially eligible for a later cross-sectional width model.",
        "curved_rod": "Potentially eligible only after a later geometry decision.",
        "vibrio": "Potentially eligible only after a later geometry decision.",
        "spiral_or_helical": "Requires separate geometry treatment.", "filamentous": "Requires separate geometry treatment.",
        "branched": "Requires separate geometry treatment.", "pleomorphic": "Requires separate geometry treatment.",
        "unusual_or_unresolved": "Requires review before geometric use.",
    }
    output = [{"summary_type": "shape_category", "category": category, **values,
               "future_geometry_note": notes.get(category, "Requires review before geometric use.")}
              for category, values in sorted(grouped.items())]
    class_counts = Counter(label for row in rows for label in row.get("morphology_classes", []))
    class_eligible = Counter(label for row in eligible for label in row.get("morphology_classes", []))
    class_notes = {
        "filamentous": "Requires separate geometry treatment.",
        "pleomorphic": "Requires separate geometry treatment.",
        "branched": "Requires separate geometry treatment.",
        "stalked_appendaged": "Requires separate geometry treatment.",
        "aggregate_chain_forming": "Requires separate geometry treatment.",
        "spore_related_measurement": "Requires separate geometry treatment.",
        "multiple_conflicting_observations": "Excluded from analysis-eligible width summaries.",
        "ambiguous_or_unparsable": "Excluded from analysis-eligible width summaries.",
    }
    for label, count in sorted(class_counts.items()):
        output.append({"summary_type": "provisional_morphology_class", "category": label,
                       "observation_rows": count, "with_numeric_width": None,
                       "analysis_eligible_width": class_eligible[label],
                       "future_geometry_note": class_notes.get(label, "Review label; no geometry implied.")})
    return output


def _plot_species_ecdf(ecdf: list[dict], path: Path) -> None:
    measures = ("width_min_um", "width_midpoint_um", "width_max_um")
    colors = dict(zip(measures, viridis_colors(len(measures))))
    fig, axis = plt.subplots(figsize=(7, 5))
    for measure in measures:
        values = [row for row in ecdf if row["measure"] == measure]
        axis.step([row["value_um"] for row in values], [row["ecdf"] for row in values], where="post",
                  label=measure.replace("_um", "").replace("_", " "), color=colors[measure])
    axis.set_xscale("log"); axis.set_xlabel("Canonical species width (µm; logarithmic scale)")
    axis.set_ylabel("Empirical cumulative fraction"); axis.set_title("Species-weighted width ECDFs")
    axis.grid(alpha=.25); axis.legend(); fig.tight_layout(); fig.savefig(path, dpi=180); plt.close(fig)


def run_scientific_qc(observations_path: str | Path, output_dir: str | Path) -> dict:
    """Write deterministic scientific-QC products into a new versioned directory."""
    source = Path(observations_path)
    rows = _jsonl(source)
    eligible, exclusions = eligibility(rows)
    reviews, corrections = verification_rows(rows)
    mapping, taxonomy = harmonized_taxonomy(rows)
    species = species_table(rows, mapping, eligible, corrections)
    distributions = {}
    ecdf = []
    for variant in ("uncorrected", "high_confidence_verified_corrections",
                    "formal_name_and_type_verified_corrections", "primary_only"):
        values, curve = species_distributions(species, variant)
        distributions[variant] = values; ecdf.extend(curve)
    observation_values = [row["width_min_um"] for row in eligible]
    sensitivity = {"observation_level_analysis_eligible": _summary(observation_values),
                   "species_weighted_uncorrected": distributions["uncorrected"]["width_min_um"]["all_prokaryotes"],
                   "species_weighted_high_confidence_verified_corrections": distributions["high_confidence_verified_corrections"]["width_min_um"]["all_prokaryotes"],
                   "species_weighted_formal_name_and_type_verified_corrections": distributions["formal_name_and_type_verified_corrections"]["width_min_um"]["all_prokaryotes"],
                   "species_weighted_primary_only": distributions["primary_only"]["width_min_um"]["all_prokaryotes"]}
    coverage, bias = reporting_bias(rows, mapping)
    year_bias = publication_year_bias(rows, mapping)
    morphology = morphology_summary(rows, eligible)
    output = Path(output_dir)
    products = {
        "analysis_eligibility_exclusions.csv": _csv_bytes(exclusions),
        "suspect_value_verification.csv": _csv_bytes(reviews),
        "correction_overlay.csv": _csv_bytes(corrections),
        "harmonized_taxonomy.csv": _csv_bytes(taxonomy),
        "species_analytical_table.csv": _csv_bytes(species),
        "species_width_ecdf.csv": _csv_bytes(ecdf),
        "species_width_distributions.json": json_bytes(distributions),
        "sensitivity_analysis.json": json_bytes(sensitivity),
        "harmonized_taxonomy_coverage.csv": _csv_bytes(coverage),
        "reporting_bias.json": json_bytes({"harmonized_taxonomy": bias, "publication_year": year_bias}),
        "morphology_class_summary.csv": _csv_bytes(morphology),
    }
    for name, body in products.items(): _write(output / name, body)
    plots = output / "plots"; plots.mkdir(parents=True, exist_ok=True)
    _plot_species_ecdf([row for row in ecdf if row["analytical_variant"] == "formal_name_and_type_verified_corrections"], plots / "species_width_ecdfs.png")
    summary = {"source_observations_sha256": digest(source.read_bytes()),
               "normalized_width_observations": sum(row.get("width_min_um") is not None for row in rows),
               "normalized_width_strains": len({row["bacdive_id"] for row in rows if row.get("width_min_um") is not None}),
               "analysis_eligible_width_observations": len(eligible),
               "analysis_eligible_width_strains": len({row["bacdive_id"] for row in eligible}),
               "excluded_normalized_width_observations": len(exclusions),
               "suspect_observations_reviewed": len(reviews),
               "verification_outcomes": dict(sorted(Counter(row["outcome"] for row in reviews).items())),
               "canonical_species_with_width": sum(row["canonical_selection_status"] == "canonical" for row in species),
               "species_rows": len(species), "sensitivity_width_min": sensitivity,
               "outputs_sha256": {name: digest(body) for name, body in products.items()}}
    _write(output / "scientific_qc_summary.json", json_bytes(summary))
    return summary
