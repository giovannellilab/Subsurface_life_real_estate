"""Immutable, verified HTTP cache and BacDive type-strain acquisition (stdlib)."""
from __future__ import annotations

import hashlib
from http.client import IncompleteRead
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = 'https://api.bacdive.dsmz.de/v2/'
SPARQL = 'https://sparql.dsmz.de/api/bacdive'
TYPE_QUERY = '''PREFIX d3o: <https://purl.dsmz.de/schema/>
SELECT DISTINCT ?id WHERE {
  ?strain a d3o:Strain; d3o:isTypeStrain "1"; d3o:hasBacDiveID ?id .
} ORDER BY ?id'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


class Cache:
    """Publish complete response + metadata directories; never replace a cache hit."""

    def __init__(self, root, delay=1.0, attempts=4, opener=urlopen, sleep=time.sleep):
        self.root = Path(root)
        self.delay, self.attempts = delay, attempts
        self.opener, self.sleep = opener, sleep

    def read(self, key):
        entry = self.root / key
        meta = json.loads((entry / 'metadata.json').read_bytes())
        body = (entry / 'response.json').read_bytes()
        if digest(body) != meta['sha256'] or len(body) != meta['bytes']:
            raise ValueError(f'Cache integrity failure: {entry}; preserve it and use a new snapshot')
        return json.loads(body), meta

    def get(self, url, accept='application/json'):
        key = digest((accept + '\n' + url).encode())
        if (self.root / key).exists():
            payload, meta = self.read(key)
            if meta['url'] != url:
                raise ValueError('Cache URL mismatch')
            return payload, meta, key
        self.root.mkdir(parents=True, exist_ok=True)
        for attempt in range(self.attempts):
            self.sleep(self.delay)
            try:
                req = Request(url, headers={'Accept': accept,
                    'User-Agent': 'SubsurfaceLifeRealEstate/0.1 (academic morphology acquisition)'})
                with self.opener(req, timeout=60) as response:
                    body = response.read()
                    json.loads(body)  # Never publish HTML/error or incomplete JSON as success.
                    meta = {'url': url, 'final_url': response.geturl(),
                            'retrieval_date': datetime.now(timezone.utc).isoformat(),
                            'status': response.status, 'bytes': len(body), 'sha256': digest(body),
                            'content_type': response.headers.get('Content-Type'),
                            'etag': response.headers.get('ETag'),
                            'last_modified': response.headers.get('Last-Modified')}
                break
            except (HTTPError, URLError, TimeoutError, ConnectionError, IncompleteRead) as exc:
                if isinstance(exc, HTTPError) and exc.code not in (408, 429, 500, 502, 503, 504):
                    raise
                if attempt + 1 == self.attempts:
                    raise
                wait = 2 ** attempt
                if isinstance(exc, HTTPError) and exc.headers.get('Retry-After'):
                    retry = exc.headers['Retry-After']
                    try:
                        wait = max(wait, float(retry))
                    except ValueError:
                        wait = max(wait, (parsedate_to_datetime(retry) - datetime.now(timezone.utc)).total_seconds())
                # Long Retry-After instructions are respected by stopping; resume later.
                if wait > 60:
                    raise RuntimeError(f'Server requests waiting {wait}s; resume later') from exc
                self.sleep(wait)
        staging = Path(tempfile.mkdtemp(prefix='.pending-', dir=self.root))
        try:
            (staging / 'response.json').write_bytes(body)
            (staging / 'metadata.json').write_bytes(json_bytes(meta))
            try:
                os.rename(staging, self.root / key)
            except OSError:
                if not (self.root / key).is_dir():
                    raise
                self.read(key)  # Concurrent successful acquisition wins, unchanged.
        finally:
            if staging.exists():
                shutil.rmtree(staging)  # Only unpublished staging bytes.
        payload, meta = self.read(key)
        return payload, meta, key


def acquire(raw_dir, manifest_path, limit=100):
    cache = Cache(raw_dir)
    index_url = SPARQL + '?' + urlencode({'query': TYPE_QUERY})
    index, _, index_key = cache.get(index_url, 'application/sparql-results+json')
    ids = sorted({int(row['id']['value']) for row in index['results']['bindings']})
    if not ids:
        raise ValueError('Type-strain index is empty; investigate source schema')
    if limit is not None:
        if limit < 1:
            raise ValueError('Sample size must be positive')
        n = min(limit, len(ids))
        selected = [ids[i * len(ids) // n] for i in range(n)]
    else:
        selected = ids
    keys, retrieved = [], set()
    for start in range(0, len(selected), 100):
        batch = selected[start:start + 100]
        url = API + 'fetch/' + ';'.join(map(str, batch))
        seen = set()
        while url:
            if url in seen or not url.startswith(API):
                raise ValueError('Unexpected/cyclic pagination URL')
            seen.add(url)
            payload, _, key = cache.get(url)
            if not isinstance(payload.get('results'), dict):
                raise ValueError('Unexpected BacDive response schema')
            retrieved.update(int(i) for i in payload['results'])
            keys.append(key)
            url = payload.get('next')
        print(f'Fetched/cached {min(start + 100, len(selected))}/{len(selected)} selected IDs', flush=True)
    manifest = {'schema_version': 1, 'source': 'BacDive', 'raw_dir': str(Path(raw_dir)),
                'index_key': index_key, 'index_count': len(ids),
                'selection': 'all_indexed_type_strains' if limit is None else 'evenly_spaced_sorted_ids',
                'sample_limit': limit, 'selected_ids': selected, 'response_keys': keys,
                'missing_ids': sorted(set(selected) - retrieved),
                'unexpected_ids': sorted(retrieved - set(selected))}
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json_bytes(manifest)
    if path.exists() and path.read_bytes() != content:
        raise ValueError('Manifest already exists with different content; choose another path')
    if not path.exists():
        with path.open('xb') as f:
            f.write(content)
    return manifest
