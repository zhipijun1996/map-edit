"""Explain an exact Challenge Specification lookup in the original library."""
import argparse
import json
from pathlib import Path

from pcg.prototype.creative_batches.plains_workshop.catalog_v2 import query as original_query

REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / 'generation/workshop/junctions-v1/manifest.json'
PRIOR = REPO / 'generation/workshop/plains50-v1/manifest.json'


def differences(wanted, known, prefix=''):
    ignored = {'id', 'budget', 'map_seed'} if not prefix else set()
    out = []
    for key in sorted(set(wanted) | set(known)):
        if key in ignored:
            continue
        field = prefix + key
        if key not in wanted or key not in known:
            out.append(dict(field=field, reason='explicit constraint missing or unsupported',
                            requested=wanted.get(key, 'UNKNOWN'), supported=known.get(key, 'UNKNOWN')))
        elif isinstance(wanted[key], dict) and isinstance(known[key], dict):
            out += differences(wanted[key], known[key], field + '.')
        elif wanted[key] != known[key]:
            out.append(dict(field=field, reason='outside this exact verified interface',
                            requested=wanted[key], supported=known[key]))
    return out


def query(spec):
    if not isinstance(spec, dict):
        return dict(status='unsatisfied', conflicts=[dict(field='challenge_specification',reason='JSON object required')],
                    searched=dict(junction_versions=0, geometry_search=False), new_physics_cases=0)
    result = original_query(spec, PRIOR, [MANIFEST])
    if result['status'] == 'supported_candidate':
        return result
    modules = json.loads(MANIFEST.read_text())['modules']
    close = [m for m in modules if m['specification']['required_family'] == spec.get('required_family')]
    result['interface_conflicts'] = [dict(id=m['id'], contentVersion=m['contentVersion'],
                                          differences=differences(spec, m['specification'])) for m in close]
    result['searched'].update(junction_versions=len(modules), exact_interfaces_compared=len(close),
                              geometry_search=False, untested_relations_accepted=False)
    result['negotiable'] = ['Use one explicitly listed verified interface without changing its constraints',
                            'Author a new bounded geometry/control adaptation and repeat original physics gates',
                            'Request an untested direction separately; UNKNOWN cannot be negotiated into path']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--spec', type=Path)
    group.add_argument('--examples', action='store_true')
    args = parser.parse_args()
    result = ([m['specification'] for m in json.loads(MANIFEST.read_text())['modules']]
              if args.examples else query(json.loads(args.spec.read_text())))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if isinstance(result, dict) and result['status'] == 'unsatisfied':
        raise SystemExit(2)
