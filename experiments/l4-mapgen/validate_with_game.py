#!/usr/bin/env python3
"""Cross-check experimental graphs with the game's existing design validator.

This is a design projection, not module composition or Runtime Map admission.
Permanently opened flags project to synthetic monotonic capabilities. The reused
fixture's rooms/challenges supply schema context only, not physics evidence.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(graph, fixture):
    data = copy.deepcopy(fixture)
    data['id'] = 'l4-research-projected-design'
    data['status'] = 'design_only'
    catalog = {v['id']: v for v in data['capabilities']['catalog']}
    flags = {'worldflag:' + v for node in graph['nodes'] for v in node['opens']}
    abilities = set(graph['initial_abilities']) | {v for node in graph['nodes'] for v in node['grants']}
    for ability in flags | abilities:
        catalog[ability] = {'id': ability, 'implemented': True,
                            'source': 'synthetic monotonic graph projection, not a real ability grant' if ability in flags else 'research graph; no gameplay admission'}
    data['capabilities']['catalog'] = list(catalog.values())
    initial = list(dict.fromkeys(['move'] + graph['initial_abilities']))
    data['capabilities']['guaranteed'] = initial
    future = set(data['capabilities']['future'])
    data['capabilities']['optional'] = sorted(set(catalog) - set(initial) - future)
    build = copy.deepcopy(data['capabilities']['supported_builds'][0])
    build['abilities'] = initial
    data['capabilities']['supported_builds'] = [build]
    for challenge in data['challenges']:
        challenge['supported_builds'] = [build['id']]
    room = data['rooms'][0]['id']
    nodes = []
    for node in graph['nodes']:
        x, y = node.get('ideal', [0, 0])
        nodes.append({'id': node['id'], 'identity': node.get('intent', node['role']), 'position': {'x': x, 'y': y},
                      'grants': node['grants'] + ['worldflag:' + s for s in node['opens']],
                      'reward': str(node['reward']), 'return_policy': 'one_way_exit' if node['id'] == graph['goal'] else 'return',
                      'rooms': [room]})
    edges = []
    for edge in graph['edges']:
        required = edge['requires'] + (['worldflag:' + edge['switch']] if edge['switch'] else [])
        role = 'main' if edge['purpose'] == 'main' else 'shortcut' if 'shortcut' in edge['purpose'] else 'reward'
        row = {'id': edge['id'], 'from': edge['from'], 'to': edge['to'], 'requires': required,
               'weapon_ids': [], 'role': role, 'challenge_ids': [], 'choice_value': edge['purpose']}
        edges.append(row)
        if edge['bidirectional']:
            reverse = copy.deepcopy(row)
            reverse.update(id=edge['id'] + '/reverse', **{'from': edge['to'], 'to': edge['from']})
            edges.append(reverse)
    data['topology'] = {'entry': graph['entry'], 'goal': graph['goal'], 'nodes': nodes, 'edges': edges}
    # Fixture route recommendations do not describe this new graph.
    data['pacing']['strategies'] = [{'id': 'graph-validation-only', 'node_ids': [edges[0]['from'], edges[0]['to']],
                                     'pressure_budget': 'unmeasured', 'interaction_budget': 'unmeasured', 'return_cost': 'unmeasured'}]
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--expected-commit', required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    game = a.game.resolve()
    head = subprocess.check_output(['git', '-C', str(game), 'rev-parse', 'HEAD'], text=True).strip()
    if head != a.expected_commit:
        raise ValueError('Unexpected game source commit')
    source = game / 'tools/level_design_contracts.py'
    fixture_path = game / 'tests/fixtures/level_design_v2/plains_design.json'
    spec = importlib.util.spec_from_file_location('game_level_design_contracts', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = json.loads(fixture_path.read_text())
    raw = json.loads(a.runs.read_text())
    runs = raw['runs'] if 'runs' in raw else [raw]
    rows = []
    for run in runs:
        graph = run.get('exploration_graph')
        if graph is None:
            rows.append({'id': run['id'], 'status': 'not_run', 'reason': 'no_graph'})
            continue
        errors = module.validate_design(project(graph, fixture))
        rows.append({'id': run['id'], 'status': 'passed' if not errors else 'failed', 'errors': errors})
    result = {'schema': 'map-notes/game-design-validator-crosscheck/v1', 'source_commit': head,
              'validator_sha256': sha(source), 'fixture_sha256': sha(fixture_path), 'runs_sha256': sha(a.runs),
              'scope': 'existing game design validator on graph projection; no Runtime or physics proof',
              'projection_limits': ['permanent open flags become synthetic monotonic capability variables',
                                    'fixture rooms/challenges provide schema context only',
                                    'game validator requires return-to-entry except goal; experiment permits entry OR goal escape'],
              'rows': rows, 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows)}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, ensure_ascii=False))
    return bool(result['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
