"""Offline LPSN GSS validation; preserve source rows and conflicting evidence."""
from collections import Counter, defaultdict
import csv
import io
import json
from pathlib import Path
import re

from .acquisition import digest

REQUIRED = {'genus_name', 'sp_epithet', 'subsp_epithet', 'reference', 'status',
            'authors', 'address', 'risk_grp', 'nomenclatural_type', 'record_no', 'record_lnk'}


def name_key(value):
    """Normalize whitespace only; do not resolve spelling, case, or synonyms."""
    return ' '.join(value.split()) if isinstance(value, str) else ''


def taxon_name(row):
    name = ' '.join(x for x in (row['genus_name'], row['sp_epithet']) if x)
    if row['subsp_epithet']:
        name += ' subsp. ' + row['subsp_epithet']
    return name_key(name)


def deposit_key(value):
    """Case/whitespace normalization only; retain punctuation and leading zeros."""
    return re.sub(r'\s+', '', value).upper()


def deposits(value, delimiter):
    if not isinstance(value, str):
        return {}
    return {deposit_key(v.strip()): v.strip() for v in value.split(delimiter)
            if v.strip() and v.strip().upper() != 'PENDING'}


def status_evidence(status):
    tokens = {s.strip() for s in re.split('[;,]', status)}
    valid = True if 'validly published under the ICNP' in tokens else None
    adverse = any(x in status.lower() for x in (
        'illegitimate', 'rejected', 'inaccurate spelling', 'misspelling',
        'inappropriate correction', 'in need of a replacement'))
    return valid, adverse, 'correct name' in tokens


class LpsnSnapshot:
    def __init__(self, csv_path, provenance_path):
        self.path = Path(csv_path)
        self.provenance_path = Path(provenance_path)
        self.provenance = json.loads(self.provenance_path.read_bytes())
        body = self.path.read_bytes()
        if digest(body) != self.provenance['sha256'] or len(body) != self.provenance['bytes']:
            raise ValueError('LPSN checksum/size mismatch; preserve raw file and investigate')
        if self.path.name != self.provenance['filename']:
            raise ValueError('LPSN filename differs from registered provenance')
        reader = csv.DictReader(io.StringIO(body.decode('utf-8-sig'), newline=''))
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames) or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError('Unsupported LPSN CSV headers')
        self.by_id, self.by_name, self.by_deposit = {}, defaultdict(list), defaultdict(set)
        ranks, tokens = Counter(), Counter()
        self.rows = []
        for ordinal, row in enumerate(reader, 1):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'Malformed LPSN CSV record {ordinal}')
            rid = row['record_no']
            if not re.fullmatch(r'\d+', rid) or rid in self.by_id:
                raise ValueError(f'Missing/invalid/duplicate LPSN record_no at CSV record {ordinal}')
            rank = 'subspecies' if row['subsp_epithet'] else 'species' if row['sp_epithet'] else 'genus'
            entry = {'csv_record_ordinal': ordinal, 'name': taxon_name(row), 'rank': rank, 'raw': row}
            self.rows.append(entry)
            self.by_id[rid] = entry
            ranks[rank] += 1
            tokens.update(s.strip() for s in row['status'].split(';'))
            # Genus nomenclatural_type is a taxon ID, never a strain designation.
            if rank != 'genus':
                self.by_name[entry['name']].append(rid)
                for dep in deposits(row['nomenclatural_type'], ';'):
                    self.by_deposit[dep].add(rid)
        self.summary = {'rows': len(self.rows), 'ranks': dict(ranks),
            'columns': reader.fieldnames, 'status_token_counts': dict(sorted(tokens.items())),
            'duplicate_name_groups': {n: ids for n, ids in self.by_name.items() if len(ids) > 1},
            'unresolved_record_links': [{'record_no': e['raw']['record_no'], 'record_lnk': e['raw']['record_lnk']}
                for e in self.rows if e['raw']['record_lnk'] and e['raw']['record_lnk'] not in self.by_id],
            'source_csv': str(self.path), 'source_sha256': digest(body)}

    def validate(self, row):
        """Return additive validation fields and candidate rows for one strain."""
        tax = row['taxonomy_raw']
        # Species is checked at exactly the stated rank; no author stripping or fuzzy match.
        original = name_key(tax.get('species'))
        embedded = name_key((row.get('lpsn_cross_reference') or {}).get('species'))
        collection = deposits(row['type_strain_designations'].get('culture_collection_numbers'), ',')
        primary_ids = self.by_name.get(original, [])
        embedded_ids = self.by_name.get(embedded, [])
        deposit_ids = set().union(*(self.by_deposit.get(d, set()) for d in collection)) if collection else set()
        candidate_ids = set(primary_ids) | set(embedded_ids) | deposit_ids
        candidates = []
        for rid in sorted(candidate_ids, key=int):
            e = self.by_id[rid]
            match_deposits = sorted(set(collection) & set(deposits(e['raw']['nomenclatural_type'], ';')))
            candidates.append({'bacdive_id': row['bacdive_id'], 'lpsn_record_no': rid,
                'lpsn_name': e['name'], 'lpsn_rank': e['rank'],
                'csv_record_ordinal': e['csv_record_ordinal'],
                'bacdive_name_exact': rid in primary_ids, 'embedded_lpsn_name_exact': rid in embedded_ids,
                'matching_deposit_keys': match_deposits, 'lpsn_row_raw': e['raw']})
        flags = []
        if original and embedded and original != embedded:
            flags.append('lpsn_bacdive_embedded_name_disagreement')
        chosen = self.by_id[primary_ids[0]] if len(primary_ids) == 1 else None
        valid, adverse, correct = None, False, None
        type_match, matching, state = None, [], 'name_unmatched'
        if not primary_ids:
            flags.append('lpsn_name_unmatched')
        elif len(primary_ids) > 1:
            state = 'name_ambiguous'
            flags.append('lpsn_name_ambiguous')
        else:
            raw = chosen['raw']
            valid, adverse, correct = status_evidence(raw['status'])
            matching = sorted(set(collection) & set(deposits(raw['nomenclatural_type'], ';')))
            available = bool(collection) and bool(deposits(raw['nomenclatural_type'], ';'))
            type_match = bool(matching) if available else None
            if valid is not True or adverse:
                flags.append('lpsn_nomenclatural_status_review')
            if correct is not True:
                flags.append('lpsn_not_current_correct_name')
            if type_match is not True:
                flags.append('lpsn_type_deposit_no_overlap' if available else 'lpsn_type_deposit_missing')
            if raw['record_lnk'] and raw['record_lnk'] not in self.by_id:
                flags.append('lpsn_record_link_unresolved')
            if valid is True and not adverse:
                state = 'validated_name_and_type' if type_match is True and row['type_strain_status'] == 'yes' else 'validated_name_type_unconfirmed'
            else:
                state = 'nomenclatural_status_review'
        if deposit_ids - set(primary_ids):
            flags.append('lpsn_deposit_other_taxa')
        raw = chosen['raw'] if chosen else None
        linked = self.by_id.get(raw['record_lnk']) if raw and raw['record_lnk'] else None
        fields = {
            'nomenclature_validation_status': state,
            'lpsn_csv_record_no': raw['record_no'] if raw else None,
            'lpsn_csv_name': chosen['name'] if chosen else None,
            'lpsn_csv_status_raw': raw['status'] if raw else None,
            'lpsn_validly_published_icnp': valid,
            'lpsn_current_correct_name': correct,
            'lpsn_type_deposit_match': type_match,
            'lpsn_matching_deposit_keys': matching,
            'lpsn_csv_address': raw['address'] if raw else None,
            'lpsn_csv_record_lnk': raw['record_lnk'] if raw else None,
            'lpsn_linked_name': linked['name'] if linked else None,
            'lpsn_linked_row_raw': linked['raw'] if linked else None,
            'lpsn_csv_row_raw': raw,
            'lpsn_csv_record_ordinal': chosen['csv_record_ordinal'] if chosen else None,
            'lpsn_csv_path': str(self.path), 'lpsn_csv_sha256': self.provenance['sha256'],
            'lpsn_download_date': self.provenance['download_date'],
            'lpsn_candidate_record_nos': [c['lpsn_record_no'] for c in candidates],
            'lpsn_validation_flags': sorted(flags),
        }
        return fields, candidates
