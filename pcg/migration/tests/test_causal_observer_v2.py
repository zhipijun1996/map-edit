"""Actual four Macro counters and one original bridge-support counter."""
import copy
import gzip
import hashlib
import json
import unittest
from pathlib import Path
from pcg.migration import core,physics,causal_observer_v2 as observer
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification

CONFIGS=(('foundation-migration-macro-core-167dcb6ec336-preflight-v1',observer.MACRO_SOURCE),
         ('foundation-migration-macro-core-04a93aeaf9d4-preflight-v1',observer.MACRO_SOURCE),
         ('foundation-migration-core-bottom-quality-v1-b4634207ffe0',observer.TRAPDOOR_SOURCE))
AVAILABLE=all((core.REPO/'pcg/results'/name/'counterexamples.json').exists()for name,_ in CONFIGS)


def actuals():
    values=[]
    for name,source in CONFIGS:
        root=core.REPO/'pcg/results'/name;batches={b['batch']:b for b in core.read(root/'batches.json')}
        for row in core.read(root/'counterexamples.json'):
            if'ground-preopen'not in row['id']:continue
            if source==observer.MACRO_SOURCE and row['probe']['originalRouteId']not in('outbound','cache'):continue
            ev=row['evidence'];batch=batches[ev['batch']];packed=root/batch['gzip_path'];data=gzip.decompress(packed.read_bytes())
            assert core.sha(packed)==batch['gzip_sha256']and hashlib.sha256(data).hexdigest()==batch['raw_output_sha256']
            inp=root/'physics'/(batch['batch']+'.input.json');execution=core.read(root/batch['execution'])
            assert not execution['exit_code']and core.sha(inp)==execution['input_sha256']
            case=core.read(inp)['cases'][ev['index']];raw=json.loads(data)['results'][ev['index']]
            check=physics.checked_purpose(physics.author_for(case),case,raw)
            values.append((case,raw,check,source))
    return values


@unittest.skipUnless(AVAILABLE,'Restore actual saved migration raw artifacts for observer integration tests')
class EpisodeV2Tests(unittest.TestCase):
    def test_five_real_counters_pass_original_classifier_after_actual_attribution(self):
        values=actuals();self.assertEqual(len(values),5)
        for case,raw,old,source in values:
            with self.subTest(id=case['id']):
                before=copy.deepcopy(raw);outcome=physics._same_outcome(case,raw)
                self.assertTrue(counter_classification(case,raw,old,outcome)['invalidates_design'])
                corrected=observer.correct(case,raw,old,assertion_source=source)
                self.assertTrue(corrected['ok'],corrected['reasons'])
                self.assertEqual(raw,before)
                self.assertFalse(counter_classification(case,raw,corrected,outcome)['invalidates_design'])
                proof=corrected['causal']['observerCorrections'][-1]['proof']
                self.assertEqual(proof['shotId'],2);self.assertFalse(proof['rawTraceFiltered'])

    def test_macro_body_must_cross_before_original_timer_expires(self):
        case,raw,old,source=actuals()[0];case=copy.deepcopy(case);case['latches'][0]['open_seconds']=.1
        self.assertEqual(observer.correct(case,raw,old,assertion_source=source),old)

    def test_macro_other_braking_and_reward_failures_are_never_removed(self):
        case,raw,old,source=actuals()[0];old=copy.deepcopy(old);old['reasons']+=['brake_below_lip_missing','reward_transaction_mismatch']
        corrected=observer.correct(case,raw,old,assertion_source=source)
        self.assertEqual(corrected['reasons'],['brake_below_lip_missing','reward_transaction_mismatch']);self.assertFalse(corrected['ok'])

    def test_source_and_route_scope_cannot_be_renamed_to_get_permission(self):
        case,raw,old,source=actuals()[0]
        self.assertEqual(observer.correct(case,raw,old,assertion_source=observer.TRAPDOOR_SOURCE),old)
        case=copy.deepcopy(case);case['route_spec']['id']='return'
        self.assertEqual(observer.correct(case,raw,old,assertion_source=source),old)

    def test_trapdoor_needs_actual_closed_gate_support_not_coincident_bank(self):
        case,raw,old,source=actuals()[-1];case=copy.deepcopy(case);case['platforms'].append([300,438,60,20])
        self.assertEqual(observer.correct(case,raw,old,assertion_source=source),old)

    def test_trapdoor_support_must_disappear_after_the_bound_bell_hit(self):
        case,raw,old,source=actuals()[-1];raw=copy.deepcopy(raw)
        for frame in raw['frames']:
            if frame['frame']>=110:frame['grounded']=True
        self.assertEqual(observer.correct(case,raw,old,assertion_source=source),old)

    def test_trapdoor_actual_body_must_descend_through_removed_span(self):
        case,raw,old,source=actuals()[-1];raw=copy.deepcopy(raw)
        for frame in raw['frames']:
            if frame['frame']>=111:frame['x']=1000
        self.assertEqual(observer.correct(case,raw,old,assertion_source=source),old)

    def test_new_wrapper_keeps_exact_actual_runtime_source(self):
        root=core.REPO/'pcg/results/foundation-migration-macro-core-167dcb6ec336-preflight-v1'
        first=core.read(root/'batches.json')[0]
        cases=core.read(root/'physics'/(first['batch']+'.input.json'))['cases']
        doc={'generationContract':{'generation':{'migration':{}}}}
        before=[str(physics.runner_for(c,physics.author_for(c)))for c in cases]
        _,after,records=observer.bind(doc,cases)
        actual=[str(physics.runner_for(c,physics.author_for(c)))for c in after]
        self.assertEqual(actual,before);self.assertEqual(len(records),4)

if __name__=='__main__':unittest.main()
