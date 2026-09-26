"""Offline deterministic normalization, QC summaries, and run provenance."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import uuid
import io
import json
from pathlib import Path
import platform
import subprocess

from .acquisition import Cache, digest, json_bytes
from .normalization import missing, normalize_record
from .lpsn import LpsnSnapshot
from .morphology import classify_strain


def csv_bytes(rows):
    if not rows:
        return b''
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else v
                         for k, v in row.items()})
    return stream.getvalue().encode('utf-8')


def qc(rows, manifest):
    strains = defaultdict(list)
    for row in rows:
        strains[row['bacdive_id']].append(row)
    type_strains = {k: v for k, v in strains.items() if v[0]['type_strain_status'] == 'yes'}
    counts = {}
    for label, key in [('shape', 'cell_shape_raw'), ('length', 'cell_length_raw'), ('width', 'cell_width_raw'),
                       ('normalized_length', 'length_min_um'), ('normalized_width', 'width_min_um')]:
        counts[label] = sum(any(not missing(r[key]) for r in rr) for rr in type_strains.values())
    counts['both_length_width_same_observation'] = sum(any(not missing(r['cell_length_raw']) and not missing(r['cell_width_raw']) for r in rr) for rr in type_strains.values())
    counts['both_normalized_same_observation'] = sum(any(r['length_min_um'] is not None and r['width_min_um'] is not None for r in rr) for rr in type_strains.values())
    counts['both_length_width_any_observation'] = sum(any(not missing(r['cell_length_raw']) for r in rr) and any(not missing(r['cell_width_raw']) for r in rr) for rr in type_strains.values())
    species = defaultdict(list)
    designations = defaultdict(set)
    for bid, rr in type_strains.items():
        # Use the preserved BacDive species label even when taxonomy conflicts.
        species_label = rr[0]['taxonomy_raw'].get('species')
        if isinstance(species_label, str) and species_label:
            species[species_label].append(bid)
        cc = rr[0]['type_strain_designations']['culture_collection_numbers']
        if isinstance(cc, str):
            for designation in cc.split(','):
                if designation.strip():
                    designations[designation.strip()].add(bid)
    raw = {}
    normalized = {}
    for axis in ('length', 'width'):
        raw[axis] = dict(sorted(Counter(json.dumps(r[f'cell_{axis}_raw'], ensure_ascii=False, sort_keys=True) for r in rows).items()))
        for bound in ('min', 'max'):
            key = f'{axis}_{bound}_um'
            values = sorted(r[key] for r in rows if r[key] is not None)
            histogram = Counter(str(v) for v in values)
            normalized[key] = {'count': len(values), 'min': min(values) if values else None,
                               'max': max(values) if values else None,
                               'value_counts': dict(sorted(histogram.items()))}
    flags = Counter(f for row in rows for f in row['qc_flag'])
    return {
        'scope': manifest['selection'], 'index_candidates': manifest['index_count'],
        'selected_ids': len(manifest['selected_ids']), 'retrieved_strains': len(strains),
        'confirmed_bacdive_type_strains': len(type_strains),
        'nomenclaturally_validated_strains': sum(rr[0]['nomenclature_validation_status'] in ('validated_name_and_type', 'validated_name_type_unconfirmed') for rr in strains.values()),
        'lpsn_name_and_type_supported_strains': sum(rr[0]['nomenclature_validation_status'] == 'validated_name_and_type' for rr in strains.values()),
        'lpsn_validation_status_counts': dict(Counter(rr[0]['nomenclature_validation_status'] for rr in strains.values())),
        'lpsn_validation_flag_counts_strains': dict(sorted(Counter(f for rr in strains.values() for f in rr[0].get('lpsn_validation_flags', [])).items())),
        'missing_requested_ids': manifest['missing_ids'], 'unexpected_ids': manifest['unexpected_ids'],
        'observation_rows': len(rows), 'actual_morphology_observations': sum(r['observation_present'] for r in rows),
        'missing_observation_placeholders': sum(not r['observation_present'] for r in rows),
        'type_strain_coverage': counts,
        'type_strain_missingness': {k: {'missing': len(type_strains) - v,
           'fraction': (len(type_strains) - v) / len(type_strains) if type_strains else None} for k, v in counts.items()},
        'domains': dict(Counter(rr[0]['domain'] or 'unknown' for rr in strains.values())),
        'duplicate_species_grouping_basis': 'original BacDive species label; no synonym collapse',
        'duplicate_species_type_strain_relationships': {k: sorted(v) for k, v in sorted(species.items()) if len(v) > 1},
        'shared_culture_collection_designations': {k: sorted(v) for k, v in sorted(designations.items()) if len(v) > 1},
        'multiple_observations_per_strain': {k: len(v) for k, v in strains.items() if len(v) > 1},
        'raw_dimension_value_counts': raw, 'normalized_dimension_distributions': normalized,
        'shape_value_counts': dict(sorted(Counter(str(r['cell_shape_raw']) for r in rows).items())),
        'qc_flag_counts_observation_rows': dict(sorted(flags.items())),
        'parsing_failure_rows': [r['observation_id'] for r in rows if any(f.endswith(('_unparsed', '_malformed', '_reversed_range', '_nonpositive', '_axis_conflict', '_numeric_overflow')) for f in r['qc_flag'])],
        'ambiguous_measurement_rows': [r['observation_id'] for r in rows if any(f in ('shape_review', 'complex_morphology_context', 'multiple_cell_shapes', 'width_exceeds_length_review') or f.endswith(('_unknown_unit', '_missing_unit', '_conflicting_units')) for f in r['qc_flag'])],
        'extreme_measurement_rows': [r['observation_id'] for r in rows if any(f.endswith('_extreme_review') for f in r['qc_flag'])],
        'extreme_review_threshold_um': {'below': 0.05, 'above': 100, 'purpose': 'provisional review triggers, not biological exclusion limits'},
    }


def report_text(summary):
    s = summary
    lines = ['# Morphology QC report', '',
        'This is an acquisition/normalization QC summary, not a population distribution estimate.', '',
        f"Selection: `{s['scope']}` from {s['index_candidates']:,} cached source-index candidates.",
        f"Retrieved {s['retrieved_strains']} strains; {s['confirmed_bacdive_type_strains']} have BacDive type-strain status yes.",
        f"LPSN CSV name validation: {s['nomenclaturally_validated_strains']} strains; name plus type-deposit support: {s['lpsn_name_and_type_supported_strains']}.",
        f"Validation states: {s['lpsn_validation_status_counts']}.",
        f"Rows: {s['observation_rows']}; actual observations: {s['actual_morphology_observations']}; missing-observation placeholders: {s['missing_observation_placeholders']}.", '',
        '| Type-strain coverage | Present | Missing |', '| --- | ---: | ---: |']
    for k, v in s['type_strain_coverage'].items():
        lines.append(f"| {k} | {v} | {s['type_strain_missingness'][k]['missing']} |")
    lines += ['', f"Strains with multiple observations: {len(s['multiple_observations_per_strain'])}.",
        f"Duplicate species/type-strain groups: {len(s['duplicate_species_type_strain_relationships'])}; shared deposit identifiers: {len(s['shared_culture_collection_designations'])}.",
        f"Parsing-failure rows: {len(s['parsing_failure_rows'])}; ambiguous-morphology/unit rows: {len(s['ambiguous_measurement_rows'])}; extreme-measurement rows: {len(s['extreme_measurement_rows'])}.",
        f"Missing requested IDs: {s['missing_requested_ids']}; unexpected IDs: {s['unexpected_ids']}.", '',
        '| Normalized bound (µm) | Observations | Minimum | Maximum |', '| --- | ---: | ---: | ---: |']
    for key, v in s['normalized_dimension_distributions'].items():
        lines.append(f"| {key} | {v['count']} | {v['min']} | {v['max']} |")
    lines += ['', '## Interpretation and review', '',
        '- Counts use distinct BacDive IDs for strain coverage. Bounds count individual observations; they are not independent species samples.',
        '- Separate observations are never averaged or combined to manufacture a length/width pair.',
        '- Missing and ambiguous data remain present. No outliers are removed. Values below 0.05 or above 100 µm trigger review only.',
        '- Complex morphology/context flags require review before using numeric dimensions in any geometric model; no diameter is calculated.',
        '- LPSN CSV checks distinguish name/status support from type-deposit overlap; current-name preferences and all discrepancies are retained without renaming. Culture availability is not established.',
        '- The cached source index may lag the provider database. This run covers only its documented selection.',
        '- See qc.json for raw-value frequencies, normalized bound frequencies, missingness fractions, duplicate groups, and all flag counts; qc_records.csv links each flag to its observation.', '']
    return '\n'.join(lines)


def process(manifest_path, output_dir, lpsn_csv=None, lpsn_provenance=None):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_bytes())
    cache = Cache(manifest['raw_dir'])
    _, index_meta = cache.read(manifest['index_key'])
    for key in manifest.get('index_keys', []):
        cache.read(key)
    rows, seen = [], set()
    inputs = [{'path': str(cache.root / manifest['index_key'] / 'response.json'), **index_meta}]
    for key in manifest['response_keys']:
        payload, meta = cache.read(key)
        raw_path = str(cache.root / key / 'response.json')
        inputs.append({'path': raw_path, **meta})
        for bid, record in sorted(payload['results'].items(), key=lambda item: int(item[0])):
            if bid in seen:
                raise ValueError(f'Duplicate source record across responses: {bid}; inspect manifest')
            seen.add(bid)
            if manifest.get('processing_population') and record.get('Name and taxonomic classification', {}).get('type strain') != 'yes':
                continue
            rows.extend(normalize_record(record, meta, raw_path, bid))
    rows.sort(key=lambda r: (int(r['source_record_identifier']), r['observation_index'] if r['observation_index'] is not None else -1))
    if (lpsn_csv is None) != (lpsn_provenance is None):
        raise ValueError('LPSN CSV and provenance must be supplied together')
    snapshot = LpsnSnapshot(lpsn_csv, lpsn_provenance) if lpsn_csv else None
    validation, candidates = {}, []
    if snapshot:
        inputs.append({'path': str(snapshot.path), **snapshot.provenance,
                       'provenance_path': str(snapshot.provenance_path),
                       'provenance_sha256': digest(snapshot.provenance_path.read_bytes())})
        for row in rows:
            bid = row['bacdive_id']
            if bid not in validation:
                fields, matches = snapshot.validate(row)
                validation[bid] = fields
                candidates.extend(matches)
            row.update(validation[bid])
            row['qc_flag'] = sorted((set(row['qc_flag']) - {'nomenclature_unverified'}) | set(row['lpsn_validation_flags']))
    by_strain = defaultdict(list)
    for row in rows:
        by_strain[row['bacdive_id']].append(row)
    for group in by_strain.values():
        classify_strain(group)
    summary = qc(rows, manifest)
    summary['all_bacdive_records_considered'] = len(seen)
    summary['all_records_type_status_counts'] = manifest.get('type_status_counts_all_records')
    if snapshot:
        summary['lpsn_snapshot'] = snapshot.summary
    outputs = {
        'observations.jsonl': b''.join((json.dumps(r, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode() for r in rows),
        'observations.csv': csv_bytes(rows),
        'qc.json': json_bytes(summary),
        'qc_records.csv': csv_bytes([{k: r[k] for k in ('observation_id', 'bacdive_id', 'qc_flag', 'qc_notes', 'raw_response_path')} for r in rows]),
        'QC_REPORT.md': report_text(summary).encode(),
    }
    if snapshot:
        outputs['lpsn_candidates.jsonl'] = b''.join((json.dumps(c, sort_keys=True, ensure_ascii=False) + '\n').encode() for c in candidates)
        validation_rows = [{'bacdive_id': bid, **fields} for bid, fields in validation.items()]
        outputs['lpsn_validation.csv'] = csv_bytes(validation_rows)
        outputs['lpsn_registry_qc.json'] = json_bytes(snapshot.summary)
    output = Path(output_dir)
    # Refuse a destination within raw storage, including symlink-resolved paths.
    if output.resolve().is_relative_to(Path('data/raw').resolve()) or output.resolve().is_relative_to(cache.root.resolve()):
        raise ValueError('Processed outputs cannot be written inside raw storage')
    if snapshot and output.resolve().is_relative_to(snapshot.path.parent.resolve()):
        raise ValueError('Processed outputs cannot be written inside LPSN raw storage')
    if not snapshot and (output / 'lpsn_validation.csv').exists():
        raise ValueError('Use a separate output directory for BacDive-only results')
    output.mkdir(parents=True, exist_ok=True)
    for name, body in outputs.items():
        (output / name).write_bytes(body)
    root = Path(__file__).resolve().parents[2]
    tracked_code = sorted(list((root / 'src').rglob('*.py')) + list((root / 'scripts').glob('*.py')) + [root / 'pyproject.toml'])
    provenance = {'schema_version': 1, 'manifest_path': str(manifest_path),
        'manifest_sha256': digest(manifest_path.read_bytes()), 'python': platform.python_version(),
        'platform': platform.platform(), 'runtime_dependencies': [], 'randomness': 'none',
        'git_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'git_status': subprocess.check_output(['git', 'status', '--short'], cwd=root, text=True),
        'code_sha256': {str(p.relative_to(root)): digest(p.read_bytes()) for p in tracked_code},
        'command': ['python3', 'scripts/process_bacdive.py', '--manifest', str(manifest_path), '--output-dir', str(output)],
        'inputs': inputs, 'outputs_sha256': {k: digest(v) for k, v in outputs.items()},
        'note': 'Deterministic processing manifest; acquisition timestamps are in inputs. Execution receipt is separate.'}
    provenance['schema_version'] = 2 if snapshot else 1
    if snapshot:
        provenance['command'] += ['--lpsn-csv', str(lpsn_csv), '--lpsn-provenance', str(lpsn_provenance)]
    else:
        provenance['command'] += ['--without-lpsn']
    (output / 'processing_manifest.json').write_bytes(json_bytes(provenance))
    receipts = output / 'run_receipts'
    receipts.mkdir(exist_ok=True)
    receipt = {'executed_at_utc': datetime.now(timezone.utc).isoformat(),
               'processing_manifest_sha256': digest(json_bytes(provenance)),
               'processing_manifest': provenance}
    with (receipts / (uuid.uuid4().hex + '.json')).open('xb') as f:
        f.write(json_bytes(receipt))
    print(report_text(summary))
    return summary
