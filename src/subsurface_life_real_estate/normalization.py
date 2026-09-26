"""Conservative dimension parsing and lossless long-form morphology extraction."""
from __future__ import annotations

from decimal import Decimal
import json
import math
import re

UNITS = {'um': Decimal('1'), 'µm': Decimal('1'), 'μm': Decimal('1'),
         'nm': Decimal('0.001'), 'mm': Decimal('1000'),
         'micrometre': Decimal('1'), 'micrometres': Decimal('1'),
         'micrometer': Decimal('1'), 'micrometers': Decimal('1')}
NUMBER = r'(?:\d+(?:\.\d+)?|\.\d+)'
UNIT = r'(?:µm|μm|um|nm|mm|micrometres?|micrometers?)'
DIMENSION = re.compile(rf'^\s*({NUMBER})\s*({UNIT})?\s*(?:(?:-|–|—|to)\s*({NUMBER})\s*({UNIT})?)?\s*(?:(wide|long|in diameter))?\s*$', re.I)
COMPLEX = re.compile(r'filament|pleomorph|branch|appendage|spore|aggregat|hypha|prosthec|stalk|variable|chain|cluster|budding|flagell', re.I)
SIMPLE_SHAPES = {'rod-shaped', 'coccus-shaped', 'coccoid', 'coccus', 'rod', 'rods',
                 'cocci', 'spherical', 'oval', 'oval-shaped', 'ovoid', 'short rod-shaped'}


def missing(value):
    return value is None or value == ''


def dimension(raw, unit=None, axis=None):
    """Return min/max µm, unit evidence, and flags; never infer an absent unit."""
    result = {'min': None, 'max': None, 'unit_basis': None, 'flags': []}
    if missing(raw):
        result['flags'] = ['missing']
        return result
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        result['flags'] = ['malformed']
        return result
    match = DIMENSION.fullmatch(str(raw))
    if not match:
        result['flags'] = ['unparsed']
        return result
    a, ua, b, ub, descriptor = match.groups()
    descriptor = descriptor.lower() if descriptor else None
    if (axis == 'length' and descriptor in ('wide', 'in diameter')) or (axis == 'width' and descriptor == 'long'):
        result['flags'] = ['axis_conflict']
        return result
    units = [u.lower() for u in (ua, ub) if u]
    if not missing(unit):
        if not isinstance(unit, str) or unit.strip().lower() not in UNITS:
            result['flags'] = ['unknown_unit']
            return result
        units.append(unit.strip().lower())
    if not units:
        result['flags'] = ['missing_unit']
        return result
    if len({UNITS[u] for u in units}) != 1:
        result['flags'] = ['conflicting_units']
        return result
    factor = UNITS[units[0]]
    lo, hi = Decimal(a) * factor, Decimal(b or a) * factor
    result['unit_basis'] = 'explicit_inline' if ua or ub else 'explicit_field'
    if lo > hi:
        result['flags'] = ['reversed_range']
        return result
    if lo <= 0:
        result['flags'] = ['nonpositive']
        return result
    if not math.isfinite(float(lo)) or not math.isfinite(float(hi)):
        result['flags'] = ['numeric_overflow']
        return result
    result['min'], result['max'] = float(lo), float(hi)
    if lo < Decimal('0.05') or hi > Decimal('100'):
        result['flags'].append('extreme_review')
    return result


def entries(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def normalize_record(record, meta, raw_path, record_key=None):
    tax = record.get('Name and taxonomic classification', {})
    general = record.get('General', {})
    morphology = record.get('Morphology', {})
    lpsn = tax.get('LPSN', {})
    if not isinstance(lpsn, dict):
        lpsn = {}  # Original remains in taxonomy_raw; flag below.
    record_id = str(general.get('BacDive-ID', record_key or 'unknown'))
    base_flags = ['nomenclature_unverified']
    if record_key is not None and record_id != str(record_key):
        base_flags.append('record_id_conflict')
    status = tax.get('type strain')
    if status != 'yes':
        base_flags.append('type_strain_not_confirmed')
    names = {}
    for field in ('species', 'genus', 'domain', 'phylum'):
        v, lv = tax.get(field), lpsn.get(field)
        if not missing(v) and not missing(lv) and v != lv:
            base_flags.append(f'{field}_taxonomy_conflict')
            names[field] = None
        else:
            names[field] = v if not missing(v) else lv
    if names['domain'] not in ('Bacteria', 'Archaea'):
        base_flags.append('domain_unconfirmed')
    if not lpsn:
        base_flags.append('lpsn_cross_reference_missing')
    refs = entries(record.get('Reference'))
    cells = entries(morphology.get('cell morphology'))
    shapes = {json.dumps(c.get('cell shape'), sort_keys=True) for c in cells
              if isinstance(c, dict) and not missing(c.get('cell shape'))}
    if len(shapes) > 1:
        base_flags.append('multiple_cell_shapes')
    # A missing observation gets one explicit placeholder, so missing strains survive.
    observations = cells if cells else [None]
    result = []
    for index, observation in enumerate(observations):
        flags = list(base_flags)
        obs = observation if isinstance(observation, dict) else {}
        if observation is None:
            flags.append('no_cell_morphology')
        elif not isinstance(observation, dict):
            flags.append('malformed_observation')
        shape, length, width = (obs.get(k) for k in ('cell shape', 'cell length', 'cell width'))
        if missing(shape):
            flags.append('shape_missing')
        elif not isinstance(shape, str) or shape.strip().lower() not in SIMPLE_SHAPES:
            flags.append('shape_review')
        # Inspect structured morphology context, not primary-literature text.
        if COMPLEX.search(json.dumps(morphology, ensure_ascii=False)):
            flags.append('complex_morphology_context')
        if obs.get('text_mined') or obs.get('text mined'):
            flags.append('database_text_mined')
        source_ids = entries(obs.get('@ref'))
        matched = [r for r in refs if isinstance(r, dict) and str(r.get('@id')) in {str(x) for x in source_ids}]
        if not source_ids:
            flags.append('morphology_reference_missing')
        elif len({str(r.get('@id')) for r in matched}) != len({str(x) for x in source_ids}):
            flags.append('morphology_reference_unresolved')
        ln = dimension(length, obs.get('cell length unit'), 'length')
        wd = dimension(width, obs.get('cell width unit'), 'width')
        if ln['max'] is not None and wd['min'] is not None and wd['min'] > ln['max']:
            flags.append('width_exceeds_length_review')
        flags += ['length_' + f for f in ln['flags']] + ['width_' + f for f in wd['flags']]
        row = {
            'observation_id': f'{record_id}:{index}' if cells else f'{record_id}:missing',
            'observation_index': index if cells else None,
            'observation_present': bool(cells),
            'species_name': names['species'], 'genus': names['genus'],
            'domain': names['domain'], 'phylum': names['phylum'],
            'bacdive_id': record_id, 'type_strain_status': status,
            'type_strain_designations': {'designation': tax.get('strain designation'),
                'culture_collection_numbers': record.get('Literature', {}).get('culture collection no.')},
            'lpsn_identifier': lpsn.get('id'), 'lpsn_cross_reference': lpsn or None,
            'nomenclature_validation_status': 'unverified_bacdive_type_strain_candidate',
            'taxonomy_raw': tax, 'cell_shape_raw': shape,
            'cell_length_raw': length, 'cell_width_raw': width,
            'cell_length_unit_raw': obs.get('cell length unit'),
            'cell_width_unit_raw': obs.get('cell width unit'),
            'length_min_um': ln['min'], 'length_max_um': ln['max'],
            'width_min_um': wd['min'], 'width_max_um': wd['max'],
            'length_unit_basis': ln['unit_basis'], 'width_unit_basis': wd['unit_basis'],
            'source_reference': matched, 'source_reference_ids': source_ids,
            'source_database': 'BacDive', 'source_record_identifier': record_id,
            'source_record_doi': general.get('doi'), 'source_url': meta['url'],
            'retrieval_date': meta['retrieval_date'], 'raw_response_path': raw_path,
            'raw_response_sha256': meta['sha256'], 'morphology_observation_raw': observation,
            'morphology_context_raw': morphology,
            'qc_flag': sorted(set(flags)),
            'qc_notes': 'Review flags; no values imputed, averaged, or removed. '
                        'Complex-context flags do not establish that the measured cell is a spore or filament.',
        }
        result.append(row)
    return result
