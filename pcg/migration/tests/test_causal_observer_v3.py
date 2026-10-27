"""Read-only regression against the real saved recipes-v5 support-removal trace."""
import copy,gzip,hashlib,json,unittest
from functools import lru_cache
from pcg.migration import core,physics,causal_observer_v2,causal_observer_v3 as observer
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification

RUN=core.REPO/'pcg/results/foundation-migration-core-bottom-quality-v1-b4634207ffe0'
AVAILABLE=(RUN/'counterexamples.json').is_file()

@lru_cache(maxsize=1)
def actual():
    row=next(r for r in core.read(RUN/'counterexamples.json')if'ground-preopen'in r['id'])
    ev=row['evidence'];batch=next(b for b in core.read(RUN/'batches.json')if b['batch']==ev['batch'])
    packed=RUN/batch['gzip_path'];data=gzip.decompress(packed.read_bytes())
    assert core.sha(packed)==batch['gzip_sha256']and hashlib.sha256(data).hexdigest()==batch['raw_output_sha256']
    inp=RUN/'physics'/(batch['batch']+'.input.json');execution=core.read(RUN/batch['execution'])
    assert execution['exit_code']==0 and core.sha(inp)==execution['input_sha256']
    case=core.read(inp)['cases'][ev['index']];raw=json.loads(data)['results'][ev['index']]
    assert case['id']==raw['id']
    author=physics.author_for(case);old=physics.checked_purpose(author,case,raw)
    assert causal_observer_v2._assertion_source(author)==observer.SOURCE
    return case,raw,old

@unittest.skipUnless(AVAILABLE,'Restore saved actual migration trace for observer integration tests')
class ActualSupportV3(unittest.TestCase):
    def test_actual_second_shot_removes_actual_support_and_whole_body_crosses(self):
        case,raw,old=actual();before=copy.deepcopy(raw);previous=copy.deepcopy(old)
        self.assertEqual(old['reasons'],['self_support_removal_missing'])
        outcome=physics._same_outcome(case,raw)
        self.assertTrue(counter_classification(case,raw,old,outcome)['invalidates_design'])
        corrected=observer.correct(case,raw,old,assertion_source=observer.SOURCE)
        self.assertTrue(corrected['ok']);self.assertEqual(raw,before);self.assertEqual(old,previous)
        self.assertFalse(counter_classification(case,raw,corrected,outcome)['invalidates_design'])
        proof=corrected['causal']['observerCorrections'][-1]['proof']
        self.assertEqual(proof['shotId'],2);self.assertEqual(proof['shotFrame'],102)
        self.assertEqual(proof['impactFrame'],110);self.assertEqual(proof['actualSupportLostFrame'],111)
        self.assertEqual(proof['wholeBodyBelowGateFrame'],122)
        self.assertEqual(proof['bodySize'],[24,36]);self.assertFalse(proof['rawTraceFiltered'])
        self.assertTrue(proof['extraActionsDoNotConferPermission'])
        self.assertEqual(proof['assertionSourceSha256'],core.sha(core.REPO/observer.SOURCE))
    def test_recipes_v7_or_other_family_cannot_claim_v5_exception(self):
        case,raw,old=actual()
        self.assertEqual(observer.correct(case,raw,old,assertion_source=causal_observer_v2.TRAPDOOR_SOURCE),old)
        changed=copy.deepcopy(case);changed['family']='gate-brake-return'
        self.assertEqual(observer.correct(changed,raw,old,assertion_source=observer.SOURCE),old)
    def test_unrelated_challenge_failure_remains_failed(self):
        case,raw,old=actual();old=copy.deepcopy(old);old['reasons'].extend(['player_harm','reward_transaction_mismatch'])
        corrected=observer.correct(case,raw,old,assertion_source=observer.SOURCE)
        self.assertFalse(corrected['ok']);self.assertEqual(corrected['reasons'],['player_harm','reward_transaction_mismatch'])
    def test_coincident_bank_prevents_own_gate_support_attribution(self):
        case,raw,old=actual();case=copy.deepcopy(case);case['platforms'].append([300,438,60,20])
        self.assertEqual(observer.correct(case,raw,old,assertion_source=observer.SOURCE),old)
    def test_support_not_lost_cannot_be_excused_by_more_shots(self):
        case,raw,old=actual();raw=copy.deepcopy(raw);raw['shots']=99
        for f in raw['frames']:
            if f['frame']>=111:f['grounded']=True
        corrected=observer.correct(case,raw,old,assertion_source=observer.SOURCE)
        self.assertEqual(corrected,old)
        self.assertTrue(counter_classification(case,raw,corrected,dict(ok=True),baseline=dict(shots=1,jumps=0,ticks=106))['invalidates_design'])
    def test_center_below_gate_is_insufficient_without_whole_body_clearance(self):
        case,raw,old=actual();raw=copy.deepcopy(raw)
        for f in raw['frames']:
            if f['frame']>=111:f['y']=450
        self.assertEqual(observer.correct(case,raw,old,assertion_source=observer.SOURCE),old)
    def test_gate_must_remain_open_at_every_actual_body_overlap(self):
        case,raw,old=actual();raw=copy.deepcopy(raw)
        for f in raw['frames']:
            if f['frame']==115:
                for b in f.get('plains',{}).get('bells',[]):
                    if b['id']=='bridge-key':b['open']=False
        self.assertEqual(observer.correct(case,raw,old,assertion_source=observer.SOURCE),old)
    def test_current_counter_pipeline_uses_bound_original_v5_source(self):
        case,raw,_=actual();judgment=physics._counter_judgment(case,raw,physics.author_for(case))
        self.assertTrue(judgment['causalCheck']['ok']);self.assertFalse(judgment['adjudication']['invalidates_design'])
        self.assertEqual(judgment['causalCheck']['causal']['observerCorrections'][-1]['proof']['method'],'pcg/actual-causal-episode-observer/v3')

if __name__=='__main__':unittest.main()
