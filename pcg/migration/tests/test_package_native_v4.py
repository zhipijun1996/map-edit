"""Native coin/note identity and fixed actor-profile contract regressions."""
import copy, unittest
from pathlib import Path
from pcg.migration import core,godot_package as package,godot_package_v4 as v4

class NativeV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prefix='87731645f7be';folder=next(core.LEGACY.glob(prefix+'*'),None)
        if folder is None:
            original=next(s for s in core.ledger()['relocations']if Path(s).name.startswith(prefix));folder=core.resolve_artifact(original+'/module.mapnote.json').parent
        cls.base_doc=core.read(folder/'module.mapnote.json');cls.base_cases=core.legacy_cases(folder)

    def fixture(self):
        doc=copy.deepcopy(self.base_doc);cases=copy.deepcopy(self.base_cases)
        point=cases[0]['spawn'];spec=dict(id='native-coin',kind='coin',amount=3,position=point)
        for case in cases:case['original_pickups']=[copy.deepcopy(spec)];case['required_original_pickups']=['native-coin']
        doc['objects'].append(dict(id=doc['id']+'/native-coin',type='reward',x=point[0]-7,y=point[1]-7,w=14,h=14,rotation=0,mechanics=dict(service='DemoApp._commit_pickup',kind='coin',amount=3,interactionRadius=46,source=copy.deepcopy(spec))))
        return package.bind_case_behavior(doc,cases),cases

    def test_native_coin_is_kept_separate_from_chest_service(self):
        doc,cases=self.fixture();content,audit=package.audit_cases(doc,cases)
        self.assertEqual(content['original_pickups'],cases[0]['original_pickups'])
        self.assertEqual(audit['nativeConsumer'],'DemoApp._commit_pickup')
        self.assertNotIn('native-coin',{r['id']for r in content['reward_sites']})

    def test_changed_native_interaction_radius_is_rejected(self):
        doc,cases=self.fixture();doc['objects'][-1]['mechanics']['interactionRadius']=47
        with self.assertRaises(package.PackageError):package.audit_cases(doc,cases)

    def test_changed_native_pickup_position_is_rejected(self):
        doc,cases=self.fixture();doc['objects'][-1]['x']+=1
        with self.assertRaises(package.PackageError):package.audit_cases(doc,cases)

    def test_fake_note_conversion_is_rejected(self):
        doc,cases=self.fixture();doc['objects'][-1]['mechanics']['kind']='note'
        with self.assertRaises(package.PackageError):package.audit_cases(doc,cases)

    def test_profile_uses_actual_native_default_capacity(self):
        record=next(r for r in core.read(v4.PROFILE_PATH)['profiles']if r['id']=='base')
        profile=v4.profile_definition({k:record[k]for k in ('id','overrides','abilities')})
        defaults=core.read(v4.DEFAULTS_PATH)
        self.assertEqual(profile['effectiveTuning']['max_air_shots'],defaults['max_air_shots'])
        self.assertEqual(profile['effectiveTuning']['max_jumps'],defaults['max_jumps'])

    def test_self_claimed_original_profile_override_is_rejected(self):
        with self.assertRaises(package.PackageError):v4.profile_definition(dict(id='base',overrides=dict(max_air_shots=99),abilities=['jump','shot_recoil']))

    def test_profile_must_be_bound_to_document_before_compile(self):
        doc,cases=self.fixture();record=next(r for r in core.read(v4.PROFILE_PATH)['profiles']if r['id']=='air_chain')
        cases[0]['original_tuning_profile']={k:record[k]for k in ('id','overrides','abilities')}
        with self.assertRaises(package.PackageError):package.audit_cases(doc,cases)
        doc=package.bind_case_behavior(doc,cases)
        content,_=package.audit_cases(doc,cases)
        self.assertEqual(content['original_tuning_profile']['effectiveTuning']['max_air_shots'],4)

    def test_required_native_reward_cannot_reference_nonexistent_pickup(self):
        doc,cases=self.fixture();cases[0]['required_original_pickups']=['missing']
        with self.assertRaises(package.PackageError):package.audit_cases(doc,cases)

if __name__=='__main__':unittest.main()
