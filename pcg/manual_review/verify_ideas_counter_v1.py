"""Read-only positive actual-counter and adversarial scope regression checks."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
import gzip
import json
from pcg.migration import core, physics, review_counter_scope_v9
from .new_ideas_v1 import OUT

def main():
    root = core.REPO / 'pcg/results/approved-ideas-orbit-qualified-final-v1'
    original = core.read(root / 'counterexamples.json')
    checks = []
    for item in original:
        if not item['adjudication']['invalidates_design']:
            continue
        evidence = item['evidence']
        case = core.read(root / 'physics' / (evidence['batch'] + '.input.json'))['cases'][evidence['index']]
        raw = json.loads(gzip.decompress((root / evidence['output']).read_bytes()))['results'][evidence['index']]
        args = [case, raw, item['causalCheck'], item['externalOutcome'], item['adjudication'], {'ok': True}]
        result = review_counter_scope_v9.classify(*args)
        assert result['scope'] == 'outside_contract_alternative' and not result['invalidates_design'] and not result['accepted_module_solution']
        checks.append(dict(id=item['id'], actualRaw=evidence, positive=True))
        mutations = {
            'wrong_design': lambda a: a[0]['approved_implementation'].update(designVersion='wrong'),
            'not_counter': lambda a: a[0].pop('migration_counter'),
            'probe': lambda a: a[0].update(migration_probe={'kind': 'fixture'}),
            'harm': lambda a: a[1].update(hp=4),
            'reset': lambda a: a[1].update(returns=1),
            'forbidden_capability': lambda a: a[1].update(air_jumps=1),
            'independent_refusal': lambda a: a[2]['reasons'].append('real_damage'),
            'tampered_outside_frames': lambda a: a[2]['causal'].update(outsideFrames=[]),
            'failed_outcome': lambda a: a[3].update(ok=False),
            'bad_baseline': lambda a: a[5].update(ok=False),
        }
        for name, mutate in mutations.items():
            altered = copy.deepcopy(args)
            mutate(altered)
            judgment = review_counter_scope_v9.classify(*altered)
            assert judgment == altered[4] and judgment['invalidates_design'], name
            checks.append(dict(id=item['id'], negative=name, rejected=True))
    assert len(checks) == 22
    core.write(OUT / 'counter-scope-regression.json', dict(passed=True, simulationTrials=0, preservedRaw=True, source=physics.artifact(core.REPO / 'pcg/migration/review_counter_scope_v9.py'), checks=checks))
    print('COUNTER_SCOPE_REGRESSION_PASS', len(checks))
if __name__ == '__main__':
    main()
