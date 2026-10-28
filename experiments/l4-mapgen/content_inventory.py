#!/usr/bin/env python3
"""Read Map Notes' pinned content; never turn missing requirements into approval."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root=ROOT, game=None):
    library = root / 'library'
    raw = (library / 'catalog.json').read_bytes()
    catalog = json.loads(raw)
    rows = []
    for entry in catalog['modules']:
        # Paths come from a validated catalogue, still check before filesystem use.
        path = (root / entry['file'].removeprefix('./')).resolve()
        if not path.is_relative_to((library / 'modules').resolve()):
            raise ValueError('Module path outside library')
        content = path.read_bytes()
        if sha(content) != entry['contentSha256']:
            raise ValueError('Module content drift: ' + entry['id'])
        module = json.loads(content)
        source = module['source']
        if source['commit'] != catalog['sourceCommit']:
            raise ValueError('Mixed source commit: ' + entry['id'])
        original = source.get('original', {})
        ports = []
        for role in ('entry', 'exit'):
            candidates = original.get(role + '_ports') or ([original[role + '_port']] if original.get(role + '_port') else [])
            for port in candidates:
                ports.append({'role': role, 'raw': port, 'state_semantics': 'grounded_contract_requires_runtime_confirmation'})
        bounds = original.get('world_bounds')
        platforms = original.get('platforms')
        req = module.get('capabilityRequirements', {'status': 'unspecified'})
        latest = None
        if game is not None:
            source_path = Path(source['path'])
            if source_path.is_absolute() or '..' in source_path.parts:
                raise ValueError('Unsafe game source path')
            old = library / 'source' / source_path
            current = game / source_path
            latest = {'path': str(source_path), 'snapshot_present': old.is_file(), 'current_present': current.is_file()}
            if old.is_file() and current.is_file():
                latest.update(snapshot_sha256=sha(old.read_bytes()), current_sha256=sha(current.read_bytes()),
                              identical_source_bytes=old.read_bytes() == current.read_bytes())
        rows.append({'id': entry['id'], 'category': entry['category'], 'collection': entry.get('collection'),
                     'source_path': source['path'], 'module_content_sha256': sha(content),
                     'source_kind': source.get('kind'), 'bounds_world_units': bounds,
                     'collision_rectangles_world_units': platforms, 'ports': ports,
                     'capability_requirements': req, 'difficulty': module.get('difficulty'),
                     'integration': entry.get('integration'), 'current_source_comparison': latest,
                     'map_admission': 'unverified', 'physics_transfer_evidence': None,
                     'automatic_template_admission': False,
                     'admission_reason': 'No complete capability, transfer, occupied-clearance and multi-port map proof inferred from a sketch.'})
    status = Counter(r['capability_requirements']['status'] for r in rows)
    return {'schema': 'map-notes/map-content-inventory/v1', 'artifact_kind': 'content_inventory_not_admitted_catalog',
            'source_repository': catalog['sourceRepository'], 'source_commit': catalog['sourceCommit'],
            'catalog_sha256': sha(raw), 'module_count': len(rows), 'capability_status_counts': dict(status),
            'rated_difficulty_count': sum(r['difficulty'] is not None and r['difficulty'].get('score') is not None for r in rows),
            'has_resource_ports': sum(bool(r['ports']) for r in rows),
            'automatic_template_count': 0, 'modules': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, help='Optional pinned game checkout for byte comparison only')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = inventory(game=args.game.resolve() if args.game else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in data.items() if k != 'modules'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
