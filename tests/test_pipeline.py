"""Synthetic, offline behavior tests. No external source content is distributed."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from subsurface_life_real_estate.acquisition import Cache, acquire, digest, json_bytes
from subsurface_life_real_estate.normalization import dimension, normalize_record
from subsurface_life_real_estate.processing import process, qc


def record(cells=None):
    return {'General': {'BacDive-ID': 1},
            'Name and taxonomic classification': {'species': 'Synthetic example',
                'genus': 'Synthetic', 'domain': 'Bacteria', 'type strain': 'yes'},
            'Morphology': {} if cells is None else {'cell morphology': cells},
            'Reference': [{'@id': 7, 'title': 'Synthetic reference'}]}


META = {'url': 'https://example.org/1', 'retrieval_date': '2026-09-14T00:00:00+00:00', 'sha256': 'test'}


class Response(io.BytesIO):
    status = 200
    headers = {'Content-Type': 'application/json'}

    def geturl(self):
        return 'https://example.org/1'


class Dimensions(unittest.TestCase):
    def test_units(self):
        for raw, expected in [('500 nm', .5), ('0.002 mm', 2), ('2 μm', 2), ('2 um', 2), ('2 micrometres', 2)]:
            with self.subTest(raw=raw):
                self.assertEqual(dimension(raw)['min'], expected)
                self.assertEqual(dimension(raw)['max'], expected)

    def test_ranges(self):
        for raw in ['0.4–0.6 µm wide', '0.4-0.6 µm', '0.4 to 0.6 µm', '0.4 µm—0.6 µm']:
            with self.subTest(raw=raw):
                d = dimension(raw)
                self.assertEqual((d['min'], d['max']), (.4, .6))
        self.assertEqual(dimension('1.5–3.0 µm long')['max'], 3)

    def test_explicit_field(self):
        self.assertEqual(dimension(500, 'nm')['min'], .5)
        self.assertEqual(dimension('0.5', 'µm')['unit_basis'], 'explicit_field')

    def test_missing(self):
        for v in (None, ''):
            self.assertEqual(dimension(v)['flags'], ['missing'])
        self.assertEqual(dimension('0.5')['flags'], ['missing_unit'])

    def test_malformed_and_ambiguous(self):
        for v in ['about 2 µm', '<2 µm', '1,5 µm', '2 ± 1 µm', '2x3 µm', 'filaments 20 µm', 'NaN', 'inf', '-1 µm']:
            self.assertIsNone(dimension(v)['min'])
            self.assertIn('unparsed', dimension(v)['flags'])
        for v in ({'value': 2}, [2, 3], True):
            self.assertEqual(dimension(v)['flags'], ['malformed'])

    def test_conflicting_unknown_units(self):
        self.assertEqual(dimension('2 µm', 'mm')['flags'], ['conflicting_units'])
        self.assertEqual(dimension('2', 'm')['flags'], ['unknown_unit'])
        self.assertEqual(dimension('2 nm-3 µm')['flags'], ['conflicting_units'])

    def test_invalid_ranges(self):
        self.assertEqual(dimension('3-2 µm')['flags'], ['reversed_range'])
        self.assertEqual(dimension('0 µm')['flags'], ['nonpositive'])

    def test_axis_conflict(self):
        self.assertEqual(dimension('2 µm wide', axis='length')['flags'], ['axis_conflict'])
        self.assertEqual(dimension('2 µm LONG', axis='width')['flags'], ['axis_conflict'])

    def test_numeric_overflow(self):
        self.assertEqual(dimension('9' * 400 + ' µm')['flags'], ['numeric_overflow'])

    def test_extreme_retained(self):
        d = dimension('200 µm')
        self.assertEqual(d['max'], 200)
        self.assertIn('extreme_review', d['flags'])


class Normalization(unittest.TestCase):
    def test_multiple_and_raw_preservation(self):
        cells = [{'@ref': 7, 'cell length': '1–2 µm', 'cell shape': 'rod-shaped'},
                 {'@ref': 7, 'cell width': '0.5 µm', 'cell shape': 'coccus-shaped'}]
        r = record(cells)
        original = copy.deepcopy(r)
        rows = normalize_record(r, META, 'raw')
        self.assertEqual(r, original)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['morphology_observation_raw'], cells[0])
        self.assertEqual(rows[0]['cell_length_raw'], '1–2 µm')
        self.assertIsNone(rows[0]['width_min_um'])
        self.assertIsNone(rows[1]['length_min_um'])
        self.assertEqual(rows[0]['source_reference'][0]['title'], 'Synthetic reference')
        self.assertIn('multiple_cell_shapes', rows[0]['qc_flag'])

    def test_empty_morphology_retained(self):
        rows = normalize_record(record(), META, 'raw')
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]['observation_present'])
        self.assertIsNone(rows[0]['morphology_observation_raw'])

    def test_malformed_observation_retained(self):
        rows = normalize_record(record(['bad', {'cell length': ['2', '3']}]), META, 'raw')
        self.assertEqual(rows[0]['morphology_observation_raw'], 'bad')
        self.assertIn('malformed_observation', rows[0]['qc_flag'])
        self.assertIn('length_malformed', rows[1]['qc_flag'])

    def test_taxonomy_conflict(self):
        r = record()
        r['Name and taxonomic classification'].update({'phylum': 'Old', 'LPSN': {'phylum': 'New'}})
        row = normalize_record(r, META, 'raw')[0]
        self.assertIsNone(row['phylum'])
        self.assertIn('phylum_taxonomy_conflict', row['qc_flag'])
        self.assertEqual(row['taxonomy_raw']['phylum'], 'Old')

    def test_complex_and_missing_reference(self):
        row = normalize_record(record({'cell shape': 'filament-shaped', 'cell length': '200 µm', '@ref': 88}), META, 'raw')[0]
        self.assertIn('complex_morphology_context', row['qc_flag'])
        self.assertIn('morphology_reference_unresolved', row['qc_flag'])
        self.assertEqual(row['length_max_um'], 200)

    def test_suspicious_axis_order_retained(self):
        row = normalize_record(record({'cell length': '1 µm', 'cell width': '2 µm'}), META, 'raw')[0]
        self.assertIn('width_exceeds_length_review', row['qc_flag'])
        self.assertEqual(row['width_min_um'], 2)

    def test_no_type_or_nomenclature_inference(self):
        r = record()
        del r['Name and taxonomic classification']['type strain']
        row = normalize_record(r, META, 'raw')[0]
        self.assertIsNone(row['type_strain_status'])
        self.assertIn('nomenclature_unverified', row['qc_flag'])
        self.assertIn('type_strain_not_confirmed', row['qc_flag'])


class Acquisition(unittest.TestCase):
    def test_cache_reuse_and_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def opener(*args, **kwargs):
                calls.append(1)
                return Response(b'{"value": 1}')
            cache = Cache(tmp, delay=0, opener=opener)
            first = cache.get('https://example.org/1')
            before = {p: p.read_bytes() for p in Path(tmp).rglob('*.json')}
            self.assertEqual(first, cache.get('https://example.org/1'))
            self.assertEqual(len(calls), 1)
            self.assertEqual(before, {p: p.read_bytes() for p in Path(tmp).rglob('*.json')})
            body = Path(tmp) / first[2] / 'response.json'
            body.write_bytes(b'{}')  # Corrupt synthetic fixture, never real data.
            with self.assertRaisesRegex(ValueError, 'integrity'):
                cache.get('https://example.org/1')
            self.assertEqual(len(calls), 1)

    def test_retry_and_invalid_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def opener(*args, **kwargs):
                calls.append(1)
                if len(calls) == 1:
                    raise URLError('temporary')
                return Response(b'{}')
            cache = Cache(tmp, delay=0, opener=opener, sleep=lambda _: None)
            cache.get('https://example.org/1')
            self.assertEqual(len(calls), 2)
        with tempfile.TemporaryDirectory() as tmp:
            cache = Cache(tmp, delay=0, opener=lambda *a, **kw: Response(b'<html>error</html>'))
            with self.assertRaises(json.JSONDecodeError):
                cache.get('https://example.org/1')
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_nonretryable_and_retry_after(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fail(*args, **kwargs):
                raise HTTPError('https://example.org', 403, 'forbidden', {}, None)
            with self.assertRaises(HTTPError):
                Cache(tmp, delay=0, opener=fail).get('https://example.org')
            def throttled(*args, **kwargs):
                raise HTTPError('https://example.org', 429, 'wait', {'Retry-After': '120'}, None)
            with self.assertRaisesRegex(RuntimeError, 'resume later'):
                Cache(tmp, delay=0, opener=throttled).get('https://example.org')

    def test_full_acquisition_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            batches = []
            def get(cache, url, accept='application/json'):
                if 'query=' in url:
                    payload = {'results': {'bindings': [{'id': {'value': str(i)}} for i in range(1, 206)]}}
                else:
                    ids = url.rsplit('/', 1)[-1].split(';')
                    batches.append(len(ids))
                    payload = {'results': {i: record() for i in ids}, 'next': None}
                return payload, {}, digest(url.encode())
            with patch.object(Cache, 'get', get), patch('sys.stdout', new=io.StringIO()):
                m = acquire(Path(tmp) / 'raw', Path(tmp) / 'manifest.json', None)
            self.assertEqual(batches, [100, 100, 5])
            self.assertEqual(m['selected_ids'], list(range(1, 206)))
            self.assertEqual(m['missing_ids'], [])

    def test_acquisition_selection_pagination_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            requests = []
            def get(cache, url, accept='application/json'):
                requests.append(url)
                if 'query=' in url:
                    payload = {'results': {'bindings': [{'id': {'value': str(i)}} for i in range(1, 5)]}}
                elif 'page=2' in url:
                    payload = {'results': {'3': record()}, 'next': None}
                else:
                    payload = {'results': {'1': record()}, 'next': 'https://api.bacdive.dsmz.de/v2/fetch/1;3?page=2'}
                return payload, {}, digest(url.encode())
            with patch.object(Cache, 'get', get):
                m = acquire(Path(tmp) / 'raw', Path(tmp) / 'manifest.json', 2)
                self.assertEqual(m['selected_ids'], [1, 3])
                self.assertEqual(m['missing_ids'], [])
                self.assertEqual(len(m['response_keys']), 2)
                self.assertEqual(m, acquire(Path(tmp) / 'raw', Path(tmp) / 'manifest.json', 2))
                with self.assertRaisesRegex(ValueError, 'different content'):
                    acquire(Path(tmp) / 'raw', Path(tmp) / 'manifest.json', None)


class Processing(unittest.TestCase):
    def make_manifest(self, tmp):
        raw = Path(tmp) / 'raw'
        payload = {'results': {'1': record([{'@ref': 7, 'cell length': '2 µm'}, {'@ref': 7, 'cell width': '0.5 µm'}])}}
        cache = Cache(raw, delay=0, opener=lambda *a, **kw: Response(json_bytes(payload)))
        _, _, key = cache.get('https://example.org/1')
        manifest = {'raw_dir': str(raw), 'index_key': key, 'response_keys': [key], 'selected_ids': [1], 'selection': 'synthetic', 'index_count': 1, 'missing_ids': [], 'unexpected_ids': []}
        p = Path(tmp) / 'manifest.json'
        p.write_bytes(json_bytes(manifest))
        return p, raw

    def test_idempotent_and_no_pair_fabrication(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, raw = self.make_manifest(tmp)
            before = {str(p): p.read_bytes() for p in raw.rglob('*.json')}
            output = Path(tmp) / 'processed'
            with patch('sys.stdout', new=io.StringIO()):
                summary = process(manifest, output)
                first = {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()}
                process(manifest, output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()})
            self.assertEqual(before, {str(p): p.read_bytes() for p in raw.rglob('*.json')})
            self.assertEqual(summary['type_strain_coverage']['both_length_width_same_observation'], 0)
            self.assertEqual(summary['type_strain_coverage']['both_length_width_any_observation'], 1)

    def test_raw_output_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, raw = self.make_manifest(tmp)
            with self.assertRaisesRegex(ValueError, 'raw storage'):
                process(manifest, raw / 'oops')

    def test_duplicate_relationships(self):
        r = record()
        r['Literature'] = {'culture collection no.': 'TEST 1'}
        rows = normalize_record(r, META, 'raw')
        r['General']['BacDive-ID'] = 2
        rows += normalize_record(r, META, 'raw')
        m = {'selection': 'synthetic', 'index_count': 2, 'selected_ids': [1, 2], 'missing_ids': [], 'unexpected_ids': []}
        s = qc(rows, m)
        self.assertEqual(s['duplicate_species_type_strain_relationships']['Synthetic example'], ['1', '2'])
        self.assertEqual(s['shared_culture_collection_designations']['TEST 1'], ['1', '2'])


if __name__ == '__main__':
    unittest.main()
