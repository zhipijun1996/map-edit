#!/usr/bin/env python3
"""Verify preserved batch bytes and every manifest inside the compact aggregate."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(unpack=None):
    raw = (ROOT / 'results/benchmark.json').read_bytes()
    aggregate = json.loads(raw)
    provenance = json.loads((ROOT / 'results/provenance.json').read_text())
    hashes = provenance['outputs']
    assert sha(raw) == hashes['runs.json'], 'Aggregated original batch drift'
    source = json.loads((ROOT / 'source-manifest.json').read_text())
    for file, expected in source['files'].items():
        assert sha((ROOT / file).read_bytes()) == expected, 'Frozen source drift: ' + file
    assert len(aggregate['runs']) == 240
    expected_grid = {(region, algorithm, str(seed)) for region in ['plains', 'forest']
                     for algorithm in ['A', 'B', 'C', 'C_random'] for seed in range(30)}
    actual = {(r['region'], r['algorithm'], r['seed']) for r in aggregate['runs']}
    assert actual == expected_grid, 'Incomplete or wrong seed grid'
    failures = []
    for run in aggregate['runs']:
        name = f"manifests/{run['region']}-{run['algorithm']}-{run['seed']}.json"
        encoded = json.dumps(run, ensure_ascii=False, indent=2).encode()
        assert sha(encoded) == hashes[name], 'Manifest bytes drift: ' + name
        assert run['physics']['status'] == 'unverified'
        if not run['layout']['ok']:
            failures.append(run['id'])
        if unpack:
            path = unpack / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
    assert set(failures) == {'plains-C-14', 'forest-B-28', 'forest-C-17'}
    for name in ['summary.json', 'results.csv']:
        assert sha((ROOT / 'results' / name).read_bytes()) == hashes[name]
    assert sha((ROOT / 'results/component-tests.txt').read_bytes()) == provenance['tests']['log_sha256']
    return {'runs': len(actual), 'preserved_layout_failures': failures,
            'all_original_manifest_hashes_match': True, 'physics': 'unverified',
            'code_sha256': sha((ROOT / 'mapgen.py').read_bytes())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unpack', type=Path, help='Reconstruct original manifests under a separate fresh directory')
    args = parser.parse_args()
    if args.unpack and args.unpack.exists():
        parser.error('Unpack destination must not exist')
    print(json.dumps(verify(args.unpack), ensure_ascii=False))
