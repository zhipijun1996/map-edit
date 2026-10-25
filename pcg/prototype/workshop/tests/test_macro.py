import copy,json,tempfile,shutil,unittest
from pathlib import Path
from pcg.prototype.workshop.macro_interface import specifications,generate
from pcg.prototype.workshop.macro import recipe
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary

class MacroDemandTests(unittest.TestCase):
    def test_macro_proposal_uses_executable_registry_and_feedback(self):
        from pcg.prototype.workshop.intake import propose
        request=dict(content_kind='macro',family='gate-brake-return')
        self.assertEqual(propose(request,[])[0]['status'],'executable_rule_requires_physics')
        failure=dict(family='gate-brake-return',flag='unexpected_shortcut')
        self.assertEqual(propose(request,[failure])[0]['selection_weight'],0)
        failure['resolved_by']='explicit new continuous evidence';self.assertEqual(propose(request,[failure])[0]['selection_weight'],1)
    def test_unknown_recipe_cannot_be_self_implemented(self):
        s=specifications()[0];s.update(required_family='unregistered-macro',implemented=True)
        r=generate(s);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['conflicts']);self.assertNotIn('cases',r)
    def test_return_or_resource_contract_cannot_be_ignored(self):
        for field,value in [('return_conditions','all states reversible'),('resource_state',{'reset_between_components':True})]:
            s=specifications()[0];s[field]=value;self.assertEqual(generate(s)['status'],'unsatisfied')
    def test_space_is_a_real_constraint(self):
        s=specifications()[0];s['space']['max_width']=1199
        r=generate(s);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['searched'])
        s['space']['max_width']=1500;self.assertEqual(generate(s)['status'],'requires_physics')
    def test_port_direction_is_not_inferred_reversible(self):
        s=specifications()[0];s['ports']['required_normals'][0]=[1,0]
        self.assertEqual(generate(s)['status'],'unsatisfied')
    def test_no_hidden_seam_geometry_or_reward_alias(self):
        for variant in range(2):
            response=generate(specifications()[variant]);a,b=recipe(variant)
            self.assertEqual(response['cases'][0]['platforms'],a['platforms']+b['platforms'])
            rewards=response['cases'][0]['reward_sites'];self.assertEqual(len({r['id']for r in rewards}),2)
            for x,y,w,h in a['platforms']:
                for xx,yy,ww,hh in b['platforms']:
                    self.assertFalse(min(x+w,xx+ww)>max(x,xx)and min(y+h,yy+hh)>max(y,yy))

class MacroPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_run=ROOT/'results/workshop-macro-holdout-v2'
        if not(cls.source_run/'retrieval.json').exists():raise unittest.SkipTest('restore content-workshop-macro-v1 for actual physical library')
    def test_same_demand_reuses_exact_version_without_generator(self):
        specs=json.loads((self.source_run/'challenge-specifications.json').read_text())
        versions=[]
        for spec in specs:
            found=WorkshopLibrary(self.source_run/'library').find_multi(spec)
            self.assertEqual(len(found),1);self.assertEqual(found[0]['record']['content_kind'],'macro')
            self.assertFalse(found[0]['record']['production_admitted']);versions.append(found[0]['record']['contentVersion'])
        self.assertNotEqual(*versions)
    def test_dependency_drift_rejects_macro(self):
        specs=json.loads((self.source_run/'challenge-specifications.json').read_text())
        with tempfile.TemporaryDirectory(dir=ROOT/'results')as tmp:
            target=Path(tmp)/'library';shutil.copytree(self.source_run/'library',target)
            record=next(p for p in (target/'candidates').glob('*/record.json')if json.loads(p.read_text())['specification']['objective']==specs[0]['objective'])
            p=record.parent/'module.mapnote.json';d=json.loads(p.read_text())
            d['generationContract']['composition']['components'][0]['contentVersion']='sha256:'+'0'*64;p.write_text(json.dumps(d))
            with self.assertRaises(ValueError):WorkshopLibrary(target).find_multi(specs[0])
    def test_withdrawn_child_invalidates_dependent_macro(self):
        spec=json.loads((self.source_run/'challenge-specifications.json').read_text())[0]
        lib=WorkshopLibrary(self.source_run/'library');found=lib.find_multi(spec);case_path=Path(found[0]['path']).parent/'module.mapnote.json'
        doc=json.loads((ROOT.parent/case_path).read_text());lib.withdrawn.add(doc['generationContract']['composition']['components'][0]['contentVersion'])
        self.assertEqual(lib.find_multi(spec),[])

if __name__=='__main__':unittest.main()
