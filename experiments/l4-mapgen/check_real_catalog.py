#!/usr/bin/env python3
"""Necessary port-capacity probe against the real pinned Resource inventory.

Optimistically ignores content role and capabilities. Failure therefore blocks
DIRECT one-resource-per-node substitution, not all possible Macro compositions.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
from mapgen import strict_catalog_feasibility


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    inv = json.loads(a.inventory.read_text())
    runs = json.loads(a.runs.read_text())['runs']
    roles = sorted({n['role'] for run in runs for n in run['exploration_graph']['nodes']})
    templates = []
    for module in inv['modules']:
        if not module['ports']:
            continue
        templates.append({'id': module['id'], 'roles': roles,
                          'usage': (module.get('integration') or {}).get('usage', 'unverified'),
                          'ports': [{'id': str(port['raw'].get('port_id', i)), 'type': 'grounded'}
                                    for i, port in enumerate(module['ports'])]})
    probes = []
    for name, pool in [('all_declared_resources', templates),
                       ('reviewed_formal_resources', [t for t in templates if t['usage'] == 'formal'])]:
        rows = []
        for run in runs:
            probe = strict_catalog_feasibility(run['exploration_graph'], {'templates': pool})
            rows.append({'id': run['id'], 'direct_substitution_ok': probe['ok'], 'errors': probe['errors']})
        probes.append({'pool': name, 'templates': len(pool),
                       'port_count_distribution': dict(Counter(str(len(t['ports'])) for t in pool)),
                       'passed': sum(r['direct_substitution_ok'] for r in rows),
                       'failed': sum(not r['direct_substitution_ok'] for r in rows), 'rows': rows})
    out = {'schema': 'map-notes/real-resource-port-capacity-probe/v1',
           'source_commit': inv['source_commit'], 'catalog_sha256': inv['catalog_sha256'],
           'resource_templates_with_explicit_ports': len(templates),
           'port_count_distribution': dict(Counter(str(len(t['ports'])) for t in templates)),
           'scope': 'Necessary count check for direct ONE Resource per graph node with dedicated ports; no full Macro feasibility conclusion',
           'optimistic_assumptions': ['Every resource allowed every role', 'No capability rejection applied', 'Port type grounded based on Resource runtime contract'],
           'unknowns': ['Dictionary/factory Macro ports are not inferred', 'Composed multi-exit hubs need separate transfer evidence', 'Shared port routing may need an explicitly modeled junction'],
           'automatic_admission': False, 'probes': probes}
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({**{k: v for k, v in out.items() if k != 'probes'},
                      'probes': [{k: v for k, v in x.items() if k != 'rows'} for x in probes]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
