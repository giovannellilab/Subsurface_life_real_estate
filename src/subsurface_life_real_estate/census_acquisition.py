"""Full v2-only discovery and immutable acquisition; no web-page scraping."""
import json
import re
from pathlib import Path
from urllib.parse import quote

from .acquisition import API, Cache, json_bytes
from .lpsn import LpsnSnapshot


def publish_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json_bytes(value)
    if path.exists():
        if path.read_bytes() != body:
            raise ValueError(f'Immutable manifest differs: {path}; choose a new path')
    else:
        with path.open('xb') as f:
            f.write(body)


def discover(cache, url):
    ids, keys, seen, expected = set(), [], set(), None
    while url:
        if not url.startswith(API) or url in seen:
            raise ValueError('Non-v2 or cyclic population pagination')
        seen.add(url)
        url = re.sub(r'%(?![0-9a-fA-F]{2})', '%25', url)
        result, _, key = cache.get(url)
        if not isinstance(result.get('results'), list):
            raise ValueError('Unexpected population index schema')
        if expected is None:
            expected = result['count']
        if result['count'] != expected:
            raise ValueError('Population count changed while paginating; preserve snapshot for review')
        ids.update(int(i) for i in result['results'])
        keys.append(key)
        url = result['next']
        if len(keys) % 100 == 0:
            print(f'Index progress {len(ids)}/{expected}', flush=True)
    if len(ids) != expected:
        raise ValueError(f'Incomplete population index: {len(ids)} != {expected}')
    return sorted(ids), keys


def census_acquire(raw_dir, manifest_path, lpsn_csv, lpsn_provenance, delay=0.5):
    """Union all culture-index records with all taxa in the offline LPSN GSS."""
    cache = Cache(raw_dir, delay=delay)
    registry = LpsnSnapshot(lpsn_csv, lpsn_provenance)
    root = Path(manifest_path).parent
    discovery_file = root / 'discovery.json'
    if discovery_file.exists():
        discovery = json.loads(discovery_file.read_bytes())
        if discovery['lpsn_sha256'] != registry.provenance['sha256'] or discovery['raw_dir'] != str(raw_dir):
            raise ValueError('Discovery source mismatch')
        for key in discovery['index_keys']:
            cache.read(key)
    else:
        # Supported culturecollection search_type=contains; '%' matches all indexed deposits.
        # Supplement with EVERY GSS genus, including orphaned species' genus components,
        # so LPSN taxa without a deposit in this index are not silently missed.
        all_ids, keys = discover(cache, API + 'culturecollectionno/%25?search_type=contains')
        culture_count = len(all_ids)
        ids = set(all_ids)
        genera = sorted({e['raw']['genus_name'] for e in registry.rows if e['raw']['genus_name']})
        genus_counts, new_ids = {}, set()
        for i, genus in enumerate(genera):
            found, page_keys = discover(cache, API + 'taxon/' + quote(genus, safe=''))
            genus_counts[genus] = len(found)
            new_ids.update(set(found) - set(all_ids))
            ids.update(found)
            keys.extend(page_keys)
            if i % 50 == 0 or i + 1 == len(genera):
                print(f'Genus discovery {i+1}/{len(genera)}; unique IDs {len(ids)}; supplemental IDs {len(new_ids)}', flush=True)
        discovery = {'schema_version': 1, 'raw_dir': str(raw_dir), 'index_keys': keys,
            'selected_ids': sorted(ids), 'culture_index_count': culture_count,
            'lpsn_genus_count': len(genera), 'genus_counts': genus_counts,
            'supplemental_ids': sorted(new_ids), 'lpsn_sha256': registry.provenance['sha256'],
            'scope': 'all v2 culture-index records plus all genus queries from full local LPSN GSS'}
        publish_json(discovery_file, discovery)
    ids = discovery['selected_ids']
    response_keys, type_ids, status_counts, record_ids = [], [], {}, set()
    for start in range(0, len(ids), 100):
        batch = ids[start:start+100]
        url = API + 'fetch/' + ';'.join(map(str, batch))
        seen = set()
        returned = set()
        while url:
            if not url.startswith(API) or url in seen:
                raise ValueError('Non-v2 or cyclic detail pagination')
            seen.add(url)
            payload, _, key = cache.get(url)
            if not isinstance(payload.get('results'), dict):
                raise ValueError('Unexpected detail schema')
            response_keys.append(key)
            for bid, record in payload['results'].items():
                if int(bid) in record_ids:
                    raise ValueError('Duplicate detail record across responses')
                returned.add(int(bid)); record_ids.add(int(bid))
                status = record.get('Name and taxonomic classification', {}).get('type strain')
                status_counts[str(status)] = status_counts.get(str(status), 0) + 1
                if status == 'yes':
                    type_ids.append(int(bid))
            url = payload.get('next')
        if returned != set(batch):
            raise ValueError(f'Missing or unexpected IDs in batch {start}: {set(batch)^returned}')
        if start % 1000 == 0 or start + 100 >= len(ids):
            print(f'Details {min(start+100,len(ids))}/{len(ids)}; type strains {len(type_ids)}', flush=True)
    manifest = {'schema_version': 3, 'source': 'BacDive v2', 'raw_dir': str(raw_dir),
        'index_keys': discovery['index_keys'], 'index_key': discovery['index_keys'][0],
        'index_count': len(ids), 'selection': 'full_v2_culture_index_and_lpsn_genera',
        'selected_ids': ids, 'response_keys': response_keys, 'type_strain_ids': sorted(type_ids),
        'type_status_counts_all_records': status_counts,
        'missing_ids': [], 'unexpected_ids': [], 'discovery': discovery,
        'processing_population': 'all returned records with explicit type strain yes'}
    publish_json(manifest_path, manifest)
    return manifest
