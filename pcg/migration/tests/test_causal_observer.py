"""Actual saved Godot traces plus adversarial checks of causal attribution.

Archived raw files may be restored for these integration tests. Mutated copies
exercise measurement rejection only; they never certify new playable content.
"""
import copy
import gzip
import json
import unittest
from pathlib import Path
from pcg.migration import core,physics,causal_observer
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification

PREFIXES=('8c90c97e8fc1','490a5f1478c3','12ca61f568f3')
ROOT=core.REPO/'pcg/results'
AVAILABLE=all((ROOT/('foundation-migration-full-quality-v1-'+p)/'counterexamples.json').exists()for p in PREFIXES)


def actual(prefix):
    folder=ROOT/('foundation-migration-full-quality-v1-'+prefix)
    row=next(r for r in core.read(folder/'counterexamples.json')if'ground-preopen'in r['id'])
    ev=row['evidence'];batch=next(b for b in core.read(folder/'batches.json')if b['batch']==ev['batch'])
    packed=folder/batch['gzip_path']
    if core.sha(packed)!=batch['gzip_sha256']:raise AssertionError('real raw gzip hash mismatch')
    data=gzip.decompress(packed.read_bytes())
    import hashlib
    if hashlib.sha256(data).hexdigest()!=batch['raw_output_sha256']:raise AssertionError('real raw output hash mismatch')
    raw=json.loads(data)['results'][ev['index']]
    inp=folder/'physics'/(batch['batch']+'.input.json')
    execution=core.read(folder/batch['execution'])
    if core.sha(inp)!=execution['input_sha256']or execution['exit_code']:raise AssertionError('real execution input binding mismatch')
    case=core.read(inp)['cases'][ev['index']]
    return case,raw,physics.checked_purpose(physics.author_for(case),case,raw)


@unittest.skipUnless(AVAILABLE,'Restore archived actual migration raw files for causal integration tests')
class ActualCausalEpisodeTests(unittest.TestCase):
    def test_all_three_real_counter_traces_meet_original_causal_assertion(self):
        for prefix in PREFIXES:
            with self.subTest(prefix=prefix):
                case,raw,old=actual(prefix);outcome=physics._same_outcome(case,raw)
                self.assertTrue(counter_classification(case,raw,old,outcome)['invalidates_design'])
                before=copy.deepcopy(raw);check=causal_observer.correct(case,raw,old)
                self.assertTrue(check['ok'],check['reasons']);self.assertEqual(raw,before)
                self.assertFalse(counter_classification(case,raw,check,outcome)['invalidates_design'])
                self.assertIsNone(counter_classification(case,raw,check,outcome)['cost_comparison'])
                proof=check['causal']['observerCorrections'][0]['proof']
                self.assertFalse(proof['rawTraceFiltered']);self.assertEqual(proof['shotId'],2)

    def test_air_event_without_actual_accepted_shot_is_insufficient(self):
        case,raw,old=actual(PREFIXES[0]);raw=copy.deepcopy(raw)
        for frame in raw['frames']:frame['accepted']=[a for a in frame['accepted']if a.get('serial')!=2]
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_ground_shot_that_leaves_ground_does_not_become_air_fired(self):
        case,raw,old=actual(PREFIXES[0]);raw=copy.deepcopy(raw)
        next(f for f in raw['frames']if f['frame']==88)['grounded']=True
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_antipinch_extension_cannot_substitute_for_solved_window(self):
        case,raw,old=actual(PREFIXES[0]);case=copy.deepcopy(case);case['latches'][0]['open_seconds']=.1
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_unmatched_projectile_direction_does_not_bind_bell_open(self):
        case,raw,old=actual(PREFIXES[0]);raw=copy.deepcopy(raw)
        for event in raw['plains']['events']:
            if event['type']=='projectile_impact'and event['frame']==93:event['direction']=[1,0]
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_actual_gate_must_be_open_for_every_body_overlap_frame(self):
        case,raw,old=actual(PREFIXES[0]);raw=copy.deepcopy(raw)
        for bell in raw['frames'][105]['plains']['bells']:bell['open']=False
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_later_propulsion_does_not_count_as_same_low_ray_recovery(self):
        case,raw,old=actual(PREFIXES[2]);raw=copy.deepcopy(raw)
        raw['frames'][76]['accepted'].append(dict(type='air_jump'))
        self.assertEqual(causal_observer.correct(case,raw,old),old)

    def test_correction_keeps_other_original_failure_reasons(self):
        case,raw,old=actual(PREFIXES[0]);old=copy.deepcopy(old);old['reasons'].append('player_harm')
        check=causal_observer.correct(case,raw,old)
        self.assertEqual(check['reasons'],['player_harm']);self.assertFalse(check['ok'])

    def test_extra_buttons_without_actual_episode_are_not_permission(self):
        case,raw,old=actual(PREFIXES[0]);raw=copy.deepcopy(raw)
        raw['plains']['events']=[e for e in raw['plains']['events']if e['type']!='bell_open']
        raw['shots']=100;raw['jumps']=100
        check=causal_observer.correct(case,raw,old)
        self.assertTrue(counter_classification(case,raw,check,physics._same_outcome(case,raw))['invalidates_design'])

if __name__=='__main__':unittest.main()
