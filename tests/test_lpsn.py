"""Synthetic offline GSS schema, matching, status, and integration tests."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from subsurface_life_real_estate.acquisition import digest, json_bytes
from subsurface_life_real_estate.lpsn import LpsnSnapshot, REQUIRED
from subsurface_life_real_estate.normalization import normalize_record
from subsurface_life_real_estate.processing import process
import test_pipeline as fixtures


def entry(rid='1', genus='Synthetic', species='example', status='VP; sp. nov.; validly published under the ICNP; correct name', types='DSM 1', link='', subsp=''):
    return dict(genus_name=genus, sp_epithet=species, subsp_epithet=subsp,
                reference='Synthetic test reference', status=status, authors='Test author',
                address='https://example.org/taxon/' + rid, risk_grp='',
                nomenclatural_type=types, record_no=rid, record_lnk=link)


def snapshot(tmp, rows):
    path = Path(tmp) / 'lpsn.csv'
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    meta = Path(tmp) / 'lpsn.provenance.json'
    meta.write_bytes(json_bytes({'sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size,
        'filename': path.name, 'download_date': '2026-09-14'}))
    return LpsnSnapshot(path, meta)


def observation(name='Synthetic example', deposits='DSM 1', embedded=None):
    record = fixtures.record({'cell length': '2 µm'})
    record['Name and taxonomic classification']['species'] = name
    if embedded:
        record['Name and taxonomic classification']['LPSN'] = {'species': embedded}
    record['Literature'] = {'culture collection no.': deposits}
    return normalize_record(record, fixtures.META, 'raw')[0]


class LpsnTests(unittest.TestCase):
    def test_exact_name_and_deposit_preserve_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = entry()
            s = snapshot(tmp, [original])
            row = observation(deposits='dsm   1')
            before = json_bytes(row)
            fields, candidates = s.validate(row)
            self.assertEqual(fields['nomenclature_validation_status'], 'validated_name_and_type')
            self.assertEqual(fields['lpsn_csv_row_raw'], original)
            self.assertEqual(fields['lpsn_matching_deposit_keys'], ['DSM1'])
            self.assertEqual(json_bytes(row), before)
            self.assertEqual(candidates[0]['csv_record_ordinal'], 1)

    def test_synonym_link_does_not_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry(status='validly published under the ICNP; synonym', link='2'), entry(rid='2', genus='Newgenus')])
            row = observation(embedded='Newgenus example')
            fields, candidates = s.validate(row)
            self.assertEqual(fields['lpsn_csv_name'], 'Synthetic example')
            self.assertEqual(fields['lpsn_linked_name'], 'Newgenus example')
            self.assertIn('lpsn_not_current_correct_name', fields['lpsn_validation_flags'])
            self.assertIn('lpsn_bacdive_embedded_name_disagreement', fields['lpsn_validation_flags'])
            self.assertEqual(len(candidates), 2)

    def test_illegitimate_rejected_unknown_status(self):
        for status in ['validly published under the ICNP, illegitimate name',
                       'validly published under the ICNP, rejected name',
                       'inaccurate spelling', 'new unknown status', 'not validly published under the ICNP']:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                fields, _ = snapshot(tmp, [entry(status=status)]).validate(observation())
                self.assertEqual(fields['nomenclature_validation_status'], 'nomenclatural_status_review')
                self.assertIn('lpsn_nomenclatural_status_review', fields['lpsn_validation_flags'])

    def test_name_only_does_not_validate_strain(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry()])
            f, _ = s.validate(observation(deposits='DSM 2'))
            self.assertFalse(f['lpsn_type_deposit_match'])
            self.assertEqual(f['nomenclature_validation_status'], 'validated_name_type_unconfirmed')
            f, _ = s.validate(observation(deposits=None))
            self.assertIsNone(f['lpsn_type_deposit_match'])

    def test_deposit_only_and_embedded_name_do_not_replace_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry()])
            f, c = s.validate(observation(name='Other organism', embedded='Synthetic example'))
            self.assertEqual(f['nomenclature_validation_status'], 'name_unmatched')
            self.assertIsNone(f['lpsn_csv_record_no'])
            self.assertTrue(c[0]['embedded_lpsn_name_exact'])
            self.assertEqual(c[0]['matching_deposit_keys'], ['DSM1'])

    def test_ambiguous_name_and_genus_type_not_deposit(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry(), entry(rid='2'), entry(rid='3', species='', types='1')])
            f, _ = s.validate(observation())
            self.assertEqual(f['nomenclature_validation_status'], 'name_ambiguous')
            self.assertEqual(len(s.summary['duplicate_name_groups']), 1)
            self.assertNotIn('1', s.by_deposit)

    def test_subspecies_separate_rank_and_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry(), entry(rid='2', subsp='minor', types='CIP 1.2')])
            f, _ = s.validate(observation(name='Synthetic example subsp. minor', deposits='CIP 12'))
            self.assertEqual(f['lpsn_csv_record_no'], '2')
            self.assertFalse(f['lpsn_type_deposit_match'])
            f, _ = s.validate(observation(name='Synthetic example subsp. minor', deposits='CIP 1.2'))
            self.assertTrue(f['lpsn_type_deposit_match'])

    def test_pending_type_and_missing_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry(types='PENDING', link='999')])
            f, _ = s.validate(observation())
            self.assertIsNone(f['lpsn_type_deposit_match'])
            self.assertIn('lpsn_record_link_unresolved', f['lpsn_validation_flags'])
            self.assertEqual(len(s.summary['unresolved_record_links']), 1)

    def test_checksum_duplicate_ids_and_missing_schema_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = snapshot(tmp, [entry()])
            s.path.write_bytes(b'corrupted synthetic fixture')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                LpsnSnapshot(s.path, s.provenance_path)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                snapshot(tmp, [entry(), entry()])
        with tempfile.TemporaryDirectory() as tmp:
            row = entry(); del row['status']
            with self.assertRaisesRegex(ValueError, 'headers'):
                snapshot(tmp, [row])

    def test_integration_idempotent_and_counts_strains_not_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Two morphology observations for one strain; no deposit supplied by fixture.
            manifest, raw = fixtures.Processing().make_manifest(tmp)
            source_dir = Path(tmp) / 'lpsn_raw'
            source_dir.mkdir()
            s = snapshot(source_dir, [entry()])
            before = {p: p.read_bytes() for p in raw.rglob('*.json')}
            original_csv = s.path.read_bytes()
            out = Path(tmp) / 'processed'
            with patch('sys.stdout', new=io.StringIO()):
                q = process(manifest, out, s.path, s.provenance_path)
                first = {p.name: p.read_bytes() for p in out.iterdir() if p.is_file()}
                process(manifest, out, s.path, s.provenance_path)
            self.assertEqual(q['nomenclaturally_validated_strains'], 1)
            self.assertEqual(q['lpsn_name_and_type_supported_strains'], 0)
            self.assertEqual(first, {p.name: p.read_bytes() for p in out.iterdir() if p.is_file()})
            self.assertEqual(before, {p: p.read_bytes() for p in raw.rglob('*.json')})
            self.assertEqual(original_csv, s.path.read_bytes())
            rows = [json.loads(line) for line in (out / 'observations.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertNotIn('nomenclature_unverified', rows[0]['qc_flag'])
            prov = json.loads((out / 'processing_manifest.json').read_text())
            self.assertEqual(prov['inputs'][-1]['sha256'], s.provenance['sha256'])


if __name__ == '__main__':
    unittest.main()
