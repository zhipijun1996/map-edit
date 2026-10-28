"""Recipe registration on the existing multiport production orchestrator."""
import argparse
import importlib
import json
from pathlib import Path

from pcg.prototype.creative_batches.plains50_ports.produce_v2 import run

HERE = Path(__file__).parent


def external_outcome(case, result):
    # These static junctions have no mandatory chest/shot transaction. A walk
    # route to the same port is allowed; the rule checker owns causal claims.
    after = -1
    visits = []
    for port_id in case['route_spec'].get('via_ports', []):
        point = next(p['position'] for p in case['ports'] if p['id'] == port_id)
        visit = next((f for f in result.get('frames', [])
                      if f['frame'] > after and f.get('grounded')
                      and abs(f['x'] - point[0]) <= 30
                      and abs(f['y'] - point[1]) <= 1), None)
        visits.append(dict(port=port_id, frame=visit['frame'] if visit else None))
        if visit is None:
            return dict(ok=False, required_via_visits=visits,
                        reason='different external visit sequence')
        after = visit['frame']
    return dict(ok=bool(result.get('ok')), required_reward_ids=[],
                required_via_visits=visits,
                coins=result.get('workshop', {}).get('coins', 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--rules', required=True, help='Versioned Python recipe module')
    args = parser.parse_args()
    rules = importlib.import_module(args.rules)
    protocol = json.loads((HERE / 'protocol-v1.json').read_text())
    run(args.name, recipe_module=rules, export_script=HERE / 'export_v1.mjs',
        protocol_config=protocol, outcome_checker=external_outcome,
        extra_sources=[Path(__file__), HERE / 'protocol-v1.json'] +
                      [Path(p) for p in getattr(rules, 'SOURCE_DEPENDENCIES', [])])


if __name__ == '__main__':
    main()
