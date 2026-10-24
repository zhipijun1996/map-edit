import copy,json,tempfile,unittest
from pathlib import Path
from prototype.factory.core.quality import POLICY,BehaviorArchive,digest,gate,module_hash,constraint_distance
from prototype.factory.core.feedback import FeedbackError,ingest,repair_job,decide,validate

def stats(n=12,good=12):return {level:dict(trials=n,purpose_valid=good,safe_stable=good)for level in ('clean','mild','moderate')}
def catalog():
 d=dict(schema='pcg/factory-catalog/v1',review_modules=[dict(uid='a'*64,module_sha256='b'*64)],quality_policy=POLICY,candidates=[dict(uid='a'*64,admission={'status':'awaiting_human_review'})]);d['catalog_sha256']=digest(d);return d
def submission(c=None):
 c=c or catalog()
 return dict(schema='pcg/human-feedback/v1',source_kind='human_self_report',catalog_sha256=c['catalog_sha256'],candidate_uid='a'*64,module_sha256='b'*64,reviewer_code='tester_A',input_device='keyboard_mouse',skill=3,fun=4,clarity=4,fairness=4,replay_value=4,difficulty=3,flags=[],notes='',manual_attempts=[dict(mode='manual',module_sha256='b'*64,frames=120,input_events=2)])

class Admission(unittest.TestCase):
 def test_lucky_phase_does_not_qualify(self):
  s=stats();s['clean']['purpose_valid']=1
  self.assertEqual(gate(s,[],True)['status'],'rework')
 def test_arrival_without_intended_actions_does_not_qualify(self):
  s=stats();s['moderate']['purpose_valid']=0
  self.assertEqual(gate(s,[],True)['status'],'rework')
 def test_small_pilot_cannot_lower_sample_floor(self):self.assertIn('insufficient_clean_trials',gate(stats(4,4),[],True)['reasons'])
 def test_all_technical_passes_still_require_human(self):
  g=gate(stats(),[],True);self.assertEqual(g['status'],'awaiting_human_review');self.assertFalse(g['offline_approved']);self.assertFalse(g['formal_game_ready'])
 def test_counterexample_requires_design_review(self):self.assertEqual(gate(stats(),[{'word':['ground_jump']}],True)['status'],'rework')
 def test_precision_lane_is_not_a_claim_of_human_expert_difficulty(self):
  s=stats();s['mild']['purpose_valid']=9;s['moderate']['purpose_valid']=5
  self.assertEqual(gate(s,[],True,requested_tier='precision_review')['engineering_tier'],'precision_review')
 def test_regular_failure_is_not_relabelled_precision(self):
  s=stats();s['mild']['purpose_valid']=9;s['moderate']['purpose_valid']=5
  self.assertEqual(gate(s,[],True)['status'],'rework')
 def test_real_previous_failure_is_not_promoted(self):
  path=Path(__file__).resolve().parents[3]/'results/dynamic-evaluation-v1/summary.json'
  if not path.exists():self.skipTest('optional historical evidence missing')
  old=json.load(open(path));row=next(x for x in old['per_module']if x['id']=='ferry-v4-double')
  self.assertEqual(gate(row['stats'],row['shortcuts'],True)['status'],'rework')
 def test_extra_executed_action_has_positive_violation(self):
  c=dict(word=['ground_jump'],family='thorn_wall');r=dict(safe=True,settled_goal=True,plan_completed=True,minimum_goal_distance=0)
  d=constraint_distance(c,r,dict(ok=False,uninterrupted=True),['ground_jump','air_jump'])
  self.assertGreater(d['word_edit_loss'],0);self.assertGreater(d['total'],0)
 def test_infeasible_cannot_displace_feasible_elite(self):
  a=BehaviorArchive();e=dict(uid='first',features={'cell':[1,'word',0,0]},discovery=stats(4,4),quality=.9,violation=0)
  a.insert(e);bad=copy.deepcopy(e);bad.update(uid='bad',quality=1.,violation=1);bad['discovery']['clean']['purpose_valid']=1;a.insert(bad)
  self.assertEqual(next(iter(a.feasible.values()))['uid'],'first');self.assertEqual(len(a.infeasible),1)
 def test_changed_geometry_invalidates_module_hash(self):
  c={'platforms':[[0,0,100,50]],'title':'sample'};h=module_hash(c);c['title']='renamed';self.assertEqual(h,module_hash(c));c['platforms'][0][2]+=1;self.assertNotEqual(h,module_hash(c))

class HumanLoop(unittest.TestCase):
 def test_replay_is_not_human_play(self):
  s=submission();s['manual_attempts'][0]['mode']='replay'
  with self.assertRaises(FeedbackError):validate(s,catalog())
 def test_unsuccessful_manual_play_can_be_rated(self):self.assertEqual(validate(submission(),catalog())['fun'],4)
 def test_stale_module_and_catalog_rejected(self):
  for key in ('module_sha256','catalog_sha256'):
   s=submission();s[key]='c'*64
   with self.assertRaises(FeedbackError):validate(s,catalog())
 def test_boolean_rating_is_not_integer(self):
  s=submission();s['fun']=True
  with self.assertRaises(FeedbackError):validate(s,catalog())
 def test_synthetic_records_cannot_enter_real_store(self):
  s=submission();s['source_kind']='synthetic_test'
  with self.assertRaises(FeedbackError):validate(s,catalog())
 def test_feedback_import_does_not_approve(self):
  with tempfile.TemporaryDirectory()as d:
   c=catalog();store=ingest(Path(d)/'store.json',[submission()],c)
   self.assertEqual(store['decisions'],[])
   with self.assertRaises(FeedbackError):decide(store,c,'a'*64,'retain','curator','yes',human_confirmed=True)
 def test_test_store_cannot_make_repair_jobs_or_approvals(self):
  with tempfile.TemporaryDirectory()as d:
   c=catalog();s=submission(c);s['source_kind']='synthetic_test';store=ingest(Path(d)/'store.json',[s],c,test_mode=True)
   with self.assertRaises(FeedbackError):repair_job(store,c)
   with self.assertRaises(FeedbackError):decide(store,c,'a'*64,'retain','curator','test',human_confirmed=True)
 def test_feedback_returns_bound_repair_target(self):
  with tempfile.TemporaryDirectory()as d:
   c=catalog();s=submission(c);s['flags']=['excessive_wait'];store=ingest(Path(d)/'store.json',[s],c);job=repair_job(store,c)
   self.assertEqual(job['tasks'][0]['module_sha256'],'b'*64);self.assertEqual(job['tasks'][0]['target'],'excessive_wait')
 def test_tampered_catalog_is_rejected(self):
  c=catalog();c['quality_policy']=dict(POLICY,minimum_human_reviewers=0)
  with self.assertRaises(FeedbackError):validate(submission(),c)
 def test_duplicate_import_is_idempotent(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'store.json';c=catalog();s=submission(c);ingest(p,[s],c);store=ingest(p,[s],c);self.assertEqual(len(store['submissions']),1)

if __name__=='__main__':unittest.main()
