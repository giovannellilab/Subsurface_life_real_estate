"""Evidence-based morphology review classes, never a geometric model."""
import json
import re

PATTERNS = {
    'pleomorphic': r'pleomorph|variable[ -]shap',
    'filamentous': r'filament|hypha|mycel',
    'branched': r'branch',
    'stalked_appendaged': r'stalk|prosthec|appendage|flagell|pilus|pili\b',
    'aggregate_chain_forming': r'aggregat|chain|cluster|rosette|multicell',
}


def classify_strain(rows):
    shapes = {r['cell_shape_raw'] for r in rows if isinstance(r['cell_shape_raw'], str) and r['cell_shape_raw']}
    multiple_observations = sum(r["observation_present"] for r in rows) > 1
    conflicts = len(shapes) > 1
    for axis in ('length', 'width'):
        intervals = [(r[f'{axis}_min_um'], r[f'{axis}_max_um']) for r in rows if r[f'{axis}_min_um'] is not None]
        if len(intervals) > 1 and max(a for a, b in intervals) > min(b for a, b in intervals):
            conflicts = True
    for row in rows:
        raw = row['morphology_observation_raw']
        # Only this structured observation drives a morphology class. Broader strain
        # context is retained separately; spore-forming ability != spore measurement.
        text = json.dumps(raw, ensure_ascii=False).lower()
        classes = [label for label, pattern in PATTERNS.items() if re.search(pattern, text)]
        measurement_text = ' '.join(str(row[k]) for k in ('cell_length_raw','cell_width_raw'))
        if re.search(r'spore', measurement_text, re.I) or (row.get('cell_shape_raw') and re.search(r'spore', str(row['cell_shape_raw']), re.I)):
            classes.append('spore_related_measurement')
        if conflicts:
            classes.append('multiple_conflicting_observations')
        if multiple_observations:
            classes.append('multiple_observations')
        length = row['length_min_um'] is not None
        width = row['width_min_um'] is not None
        if length and width:
            numeric = 'straightforward_numerical_morphology'
        elif length or width:
            numeric = 'numerical_but_incomplete_morphology'
        else:
            numeric = 'ambiguous_or_unparsable'
        # Complex classes retain converted values, but are not labeled straightforward.
        classes.append(numeric if not classes or numeric != 'straightforward_numerical_morphology' else 'numerical_complex_morphology')
        if any(f.endswith(('_unparsed', '_malformed', '_missing_unit', '_unknown_unit', '_conflicting_units', '_reversed_range', '_nonpositive', '_numeric_overflow')) for f in row['qc_flag']):
            classes.append('ambiguous_or_unparsable')
        row['morphology_classes'] = sorted(set(classes))
        row['morphology_classification_basis'] = 'Structured observation keywords and within-strain shape/disjoint-range differences; provisional review classes'
