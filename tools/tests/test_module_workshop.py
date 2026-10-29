import copy, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import module_workshop as w
from publish_design_review import seal_design
class WorkflowTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=w.ROOT;w.ROOT=Path(self.tmp.name)
  w.write(w.IDEAS,dict(schema='pcg/module-workshop-ideas/v1',rows=[]))
  w.write('feedback/manual-review/implementation-handoff-v1.json',dict(rows=[],revision=1,policy=dict(productionApproval=False)))
  w.write('feedback/manual-review/received-design-decisions-v1.json',dict(rows=[],history=[]))
 def tearDown(self):w.ROOT=self.old;self.tmp.cleanup()
 def intake(self):
  self.raw='  原话\n保留空白 <script> ';w.intake(dict(drafts=[dict(id='idea-abcdef',sourceType='human_idea',title='测试',verbatim=self.raw,stage='IDEA')]))
 def design(self):
  return seal_design(dict(schema='pcg/module-design/v1',id='idea-abcdef',reviewStage='design',bounds=dict(x=0,y=0,w=256,h=256),ports=[dict(id='A',position=[0,192],face='LEFT')],intendedRoutes=[]))
 def prepare(self):
  self.intake();d=self.design();file='generation/module-workshop/ideas/idea-abcdef/design.json';w.write(file,d);data=w.read(w.IDEAS);data['rows'][0].update(stage='DESIGN_REVIEW',design=dict(file=file,sha256=w.digest(file),version=d['designVersion']));w.write(w.IDEAS,data);return d
 def test_raw_intake_stable_and_no_invented_approval(self):
  self.intake();r=w.read(w.IDEAS)['rows'][0];self.assertEqual(r['verbatim'],self.raw);self.assertEqual(r['humanApproval'],'UNKNOWN');self.assertFalse(r['productionApproval'])
  with self.assertRaises(ValueError):w.intake(dict(drafts=[dict(id='idea-abcdef',sourceType='human_idea',verbatim='不同原话')]))
 def test_intake_rejects_implied_implementation(self):
  with self.assertRaises(ValueError):w.intake(dict(drafts=[dict(id='idea-abcdef',sourceType='human_idea',verbatim='test',stage='ARCHIVED')]))
 def test_stale_receipt_cannot_enter_handoff(self):
  self.prepare()
  with self.assertRaises(ValueError):w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='保留',designVersion='sha256:old',decision='KEEP'))
  self.assertEqual(w.read('feedback/manual-review/implementation-handoff-v1.json')['rows'],[])
 def test_keep_enters_existing_handoff_only(self):
  d=self.prepare();w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='这个保留',designVersion=d['designVersion'],decision='KEEP'));r=w.read(w.IDEAS)['rows'][0];self.assertEqual(r['stage'],'READY_FOR_IMPLEMENTATION');h=w.read('feedback/manual-review/implementation-handoff-v1.json');self.assertEqual(h['rows'][0]['designVersion'],d['designVersion']);self.assertEqual(h['rows'][0]['status'],'READY_FOR_IMPLEMENTATION');self.assertFalse(h['policy']['productionApproval']);self.assertFalse((w.ROOT/'modules').exists())
 def test_changed_bytes_revoke_old_hash(self):
  d=self.prepare();w.write('generation/module-workshop/ideas/idea-abcdef/design.json',{**d,'extra':'changed'})
  with self.assertRaises(ValueError):w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='保留',designVersion=d['designVersion'],decision='KEEP'))
 def test_discard_keeps_design_and_does_not_enter_handoff(self):
  d=self.prepare();w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='废弃',designVersion=d['designVersion'],decision='DISCARD'));self.assertEqual(w.read(w.IDEAS)['rows'][0]['stage'],'DISCARDED');self.assertEqual(w.read('feedback/manual-review/implementation-handoff-v1.json')['rows'],[])
 def test_published_variant_requires_exact_binding(self):
  d=self.prepare();data=w.read(w.IDEAS);variant=copy.deepcopy(d);variant['bounds']['h']=384;variant=seal_design(variant);file='generation/module-workshop/ideas/idea-abcdef/variant.json';w.write(file,variant);data['rows'][0]['designVariants']=[data['rows'][0]['design'],dict(file=file,sha256=w.digest(file),version=variant['designVersion'])];w.write(w.IDEAS,data)
  w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='三怪版保留',designVersion=variant['designVersion'],decision='KEEP'));h=w.read('feedback/manual-review/implementation-handoff-v1.json');self.assertEqual(h['rows'][0]['designVersion'],variant['designVersion']);self.assertEqual(h['rows'][0]['designFile'],file)
 def test_discard_one_variant_preserves_other_unreviewed_option(self):
  d=self.prepare();data=w.read(w.IDEAS);variant=copy.deepcopy(d);variant['bounds']['h']=384;variant=seal_design(variant);file='generation/module-workshop/ideas/idea-abcdef/variant.json';w.write(file,variant);data['rows'][0]['designVariants']=[data['rows'][0]['design'],dict(file=file,sha256=w.digest(file),version=variant['designVersion'])];w.write(w.IDEAS,data)
  w.decide(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='两怪版废弃',designVersion=d['designVersion'],decision='DISCARD'));r=w.read(w.IDEAS)['rows'][0];self.assertEqual(r['stage'],'DESIGN_REVIEW');self.assertEqual(r['design']['version'],variant['designVersion']);self.assertEqual(w.read('feedback/manual-review/implementation-handoff-v1.json')['rows'],[])
 def prepare_options(self):
  d=self.prepare();data=w.read(w.IDEAS);one=dict(data['rows'][0]['design'],key='enemies-2');variant=copy.deepcopy(d);variant['bounds']['h']=384;variant=seal_design(variant);file='generation/module-workshop/ideas/idea-abcdef/third.json';w.write(file,variant);two=dict(file=file,version=variant['designVersion'],sha256=w.digest(file),key='enemies-3');data['rows'][0]['designVariants']=[one,two];w.write(w.IDEAS,data);return one,two
 def test_two_human_keeps_create_independent_handoffs(self):
  one,two=self.prepare_options();w.approve_variants(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='这两个保留',designVersions=[one['version'],two['version']]));h=w.read('feedback/manual-review/implementation-handoff-v1.json');self.assertEqual(len(h['rows']),2);self.assertEqual({r['moduleId']for r in h['rows']},{'idea-abcdef-enemies-2','idea-abcdef-enemies-3'});self.assertEqual({r['designVersion']for r in h['rows']},{one['version'],two['version']});self.assertTrue(all(r['sourceIdea']['id']=='idea-abcdef'for r in h['rows']));self.assertFalse((w.ROOT/'modules').exists())
 def test_invalid_second_option_does_not_partially_approve_first(self):
  one,two=self.prepare_options()
  with self.assertRaises(ValueError):w.approve_variants(dict(id='idea-abcdef',sourceType='human_feedback',verbatim='这两个保留',designVersions=[one['version'],'stale']))
  self.assertEqual(w.read('feedback/manual-review/implementation-handoff-v1.json')['rows'],[]);self.assertEqual(w.read(w.IDEAS)['rows'][0]['stage'],'DESIGN_REVIEW')
 def test_boundary_must_be_block_face_center(self):
  d=self.design();d['ports'][0]['position']=[0,200]
  with self.assertRaises(AssertionError):seal_design(d)
if __name__=='__main__':unittest.main()
