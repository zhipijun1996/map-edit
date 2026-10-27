"""Strict exact-source profile and original region-choice export contracts."""
import copy,unittest
from pathlib import Path
from pcg.migration import core,godot_package as base,godot_package_v5 as v5

class NativeV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=core.ACTIVE/'game-micro-board';cls.doc=core.read(cls.folder/'module.mapnote.json');cls.cases=core.read(cls.folder/'cases.json')['cases']
    def profile(self,jumps=1):
        filename='challenge_recoil_tests.gd'if jumps==1 else'branch_library_runner.gd';source=next(x for x in core.read(v5.SOURCES)['files']if Path(x['localPath']).name==filename)
        fixture=dict(provider='original_fixture/v1',id=f'original-fixture-{jumps}j2s',source=dict(path=source['localPath'],sha256=source['sha256']),initializer='ChallengeRecoilTests._fixture'if jumps==1 else'BranchLibraryRunner.fixture',max_jumps=jumps,max_air_shots=2)
        profile=dict(id=fixture['id'],overrides=dict(max_jumps=jumps,max_air_shots=2),abilities=['move','jump','shot_recoil']+(['double_jump']if jumps==2 else[]),effectiveTuning=dict(max_jumps=jumps,max_air_shots=2))
        return profile,fixture
    def fixture(self,jumps=1):
        d=copy.deepcopy(self.doc);cases=copy.deepcopy(self.cases);profile,fixture=self.profile(jumps)
        point=cases[0]['spawn'];chest=dict(id='native-or',position=point,tier='high',items=[],coins=6,reward_mode='resources',resources=[dict(kind='coin',amount=6),dict(kind='note',amount=2)])
        for c in cases:c.update(original_tuning_profile=copy.deepcopy(profile),original_fixture_profile=copy.deepcopy(fixture),original_region_chests=[copy.deepcopy(chest)])
        d['objects'].append(dict(id=d['id']+'/native-or',type='reward',x=point[0]-12,y=point[1]-12,w=24,h=24,rotation=0,mechanics=dict(service=v5.SERVICE,interactionRadius=80,selection='OR',source=copy.deepcopy(chest))))
        return v5.bind_case_behavior(d,cases),cases
    def test_exact_source_profiles_remain_distinct_1j2s_and_2j2s(self):
        a,fa=self.profile(1);b,fb=self.profile(2)
        self.assertNotEqual(v5.exact_profile(a,fa),v5.exact_profile(b,fb))
        self.assertNotEqual(fa['source']['sha256'],fb['source']['sha256'])
    def test_never_substitute_air_chain_or_more_shots(self):
        p,f=self.profile();p['id']='air_chain';p['overrides']['max_air_shots']=4
        with self.assertRaises(base.PackageError):v5.exact_profile(p,f)
    def test_caller_source_hash_or_initializer_cannot_self_certify(self):
        for key,value in [('source',dict(path='elsewhere',sha256='0'*64)),('initializer','FoundryCatalog.apply_profile')]:
            p,f=self.profile();f[key]=value
            with self.assertRaises(base.PackageError):v5.exact_profile(p,f)
    def test_export_uses_original_chest_separate_from_coin_pickups(self):
        d,c=self.fixture();content,a=v5.audit_cases(d,c)
        self.assertEqual(content['original_region_chests'],c[0]['original_region_chests']);self.assertEqual(content['original_pickups'],[])
        self.assertEqual(content['original_tuning_profile']['effectiveTuning'],dict(max_jumps=1,max_air_shots=2));self.assertEqual(a['regionSelection'],'OR')
    def test_region_radius_or_selection_change_is_rejected(self):
        for key,value in [('interactionRadius',46),('selection','AND')]:
            d,c=self.fixture();d['objects'][-1]['mechanics'][key]=value
            with self.assertRaises(base.PackageError):v5.audit_cases(d,c)
    def test_missing_amounts_and_item_chest_are_explicit_gaps(self):
        chest=dict(id='x',position=[0,0],tier='high',items=[],coins=6,reward_mode='resources',resources=[dict(kind='coin',amount=6),dict(kind='note')])
        with self.assertRaises(base.PackageError):v5.chest_definition(chest)
        chest['resources'][1]['amount']=2;chest['items']=['free-item']
        with self.assertRaises(base.PackageError):v5.chest_definition(chest)
    def test_zero_original_note_is_preserved_and_cannot_be_required(self):
        d,c=self.fixture();d['objects'][-1]['mechanics']['source']['resources'][1]['amount']=0
        for case in c:case['original_region_chests'][0]['resources'][1]['amount']=0
        content,_=v5.audit_cases(d,c);self.assertEqual(content['original_region_chests'][0]['resources'][1]['amount'],0)
        c[0]['required_region_chest_choices']=[dict(id='native-or',kind='note')]
        with self.assertRaises(base.PackageError):v5.audit_cases(d,c)
    def test_historical_hard_optional_tier_is_not_renamed(self):
        d,c=self.fixture();d["objects"][-1]["mechanics"]["source"]["tier"]="hard_optional"
        for case in c:case["original_region_chests"][0]["tier"]="hard_optional"
        content,_=v5.audit_cases(d,c);self.assertEqual(content["original_region_chests"][0]["tier"],"hard_optional")
    def test_other_route_cannot_use_different_profile(self):
        d,c=self.fixture();other=copy.deepcopy(c[0]);other['original_fixture_profile']['max_jumps']=2;c.append(other)
        with self.assertRaises(base.PackageError):v5.audit_cases(d,c)
    def test_region_chest_position_must_be_actual_source_position(self):
        d,c=self.fixture();d['objects'][-1]['x']+=1
        with self.assertRaises(base.PackageError):v5.audit_cases(d,c)
    def test_profile_must_be_bound_into_document(self):
        d,c=self.fixture();d['generationContract']['generation']['parameters']['original_fixture_profile']=None
        with self.assertRaises(base.PackageError):v5.audit_cases(d,c)

if __name__=='__main__':unittest.main()
