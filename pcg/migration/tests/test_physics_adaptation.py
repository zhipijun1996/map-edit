"""Real artifact integrity and seam fixture construction; no fake playability."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,physics


class AdaptedPhysicsFixtures(unittest.TestCase):
    def vertical(self):
        port=dict(id='P',position=[64,128],normal=[0,1],face='BOTTOM',surface='ONE_WAY_PLATFORM',
                  permission='INOUT',stagingPosition=[64,78])
        case=dict(id='vertical',platforms=[[0,96,128,16]],ports=[dict(id='P',support_index=0)],
                  one_way_platform_indices=[0],control_plan=[],spawn=[64,78],goal=[55,73,18,10],
                  block_ports={'P':{'aperture':[0,96,128,64]}})
        return case,{'generationContract':{'ports':[port]}}

    def test_bottom_interface_uses_actual_jump_and_drop(self):
        case,doc=self.vertical();fixtures=physics.seam_cases(case,doc)
        self.assertEqual(len(fixtures),6)
        self.assertTrue(all('jump'in[c['op']for c in f['control_plan']]for f in fixtures if f['migration_probe']['direction']=='ingress'))
        self.assertTrue(all('drop_through'in[c['op']for c in f['control_plan']]for f in fixtures if f['migration_probe']['direction']=='egress'))
        self.assertEqual(case['platforms'],[[0,96,128,16]])
        for f in fixtures:self.assertFalse(f['migration_probe']['neighbor']['copiedIntoModule'])

    def test_initial_output_permission_does_not_test_fictional_ingress(self):
        case,doc=self.vertical();doc['generationContract']['ports'][0]['permission']='OUTPUT'
        self.assertEqual({f['migration_probe']['direction']for f in physics.seam_cases(case,doc)},{'egress'})

    def test_rock_cannot_be_relabelled_as_vertical_port(self):
        case,doc=self.vertical();doc['generationContract']['ports'][0]['surface']='ROCK'
        with self.assertRaisesRegex(ValueError,'requires_real_one_way'):physics.seam_cases(case,doc)

    def test_vertical_crossing_requires_full_36px_body(self):
        case,doc=self.vertical();port=doc['generationContract']['ports'][0]
        case['migration_probe']=dict(kind='local_boundary',portId='P',boundary=port['position'],normal=port['normal'],direction='egress',neighbor={})
        raw=dict(ok=True,hp=5,frames=[dict(frame=i,x=64,y=y)for i,y in enumerate([100,120,140,142])])
        self.assertFalse(physics.crossing(case,raw)['passed'])
        raw['frames'][-1]['y']=150
        self.assertTrue(physics.crossing(case,raw)['passed'])


class HashBoundVerificationCache(unittest.TestCase):
    def test_cache_reuses_analysis_but_raw_mutation_invalidates(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);run=root/'run';folder=root/'module';run.mkdir();folder.mkdir()
            core.write(run/'report.json',{'fixture':'untrusted'})
            (run/'actual.output.json.gz').write_bytes(b'immutable raw bytes')
            core.write(folder/'cases.json',{'cases':[]})
            core.write(folder/'module.mapnote.json',{'generationContract':{'contentVersion':'sha256:test','ports':[],'routes':[]}})
            proof=dict(path='run/report.json',sha256=core.sha(run/'report.json'))
            with patch.object(core,'REPO',root),patch.object(physics,'_verify_report_uncached',return_value={'verified':True})as deep:
                physics.verify_report(folder,proof);physics.verify_report(folder,proof)
                self.assertEqual(deep.call_count,1)
                (run/'actual.output.json.gz').write_bytes(b'tampered raw bytes')
                physics.verify_report(folder,proof)
                self.assertEqual(deep.call_count,2)
                physics.verify_report(folder,proof,deep=True)
                self.assertEqual(deep.call_count,3)


if __name__=='__main__':unittest.main()


class NativeTimelineCounterTests(unittest.TestCase):
    def fixture(self):
        return dict(id='native',family='foundry',spawn=[0,0],goal=[90,-5,20,10],route_spec={'id':'main'},
            control_plan=[dict(op='settle',trigger={'after':444},target_x=100,deadband=3)],
            axes=[dict(frame=4,value=1.0,noise_key=124)],
            actions=[dict(frame=10,type='jump',direction=[0,0]),
                     dict(frame=22,type='shoot_release',direction=[0,1]),
                     dict(frame=25,type='jump_release',direction=[0,0])])

    def test_generic_counter_clears_original_native_inputs(self):
        case=self.fixture();rows=physics.counter_cases(case)
        for row in rows:
            if not row['migration_counter'].get('keepNativeTimeline'):
                self.assertNotIn('axes',row);self.assertNotIn('actions',row)
        self.assertEqual(len(case['actions']),3)

    def test_native_omission_retains_other_actions_and_axis_timeline(self):
        case=self.fixture();rows=physics.counter_cases(case)
        row=next(c for c in rows if c['migration_counter']['kind']=='native-omit-all-shots')
        self.assertTrue(row['migration_counter']['keepNativeTimeline'])
        self.assertEqual(row['axes'],case['axes'])
        self.assertEqual([a['type']for a in row['actions']],['jump','jump_release'])
        self.assertEqual(row['control_plan'],case['control_plan'])

    def test_extra_jump_does_not_automatically_pay_for_missing_recoil(self):
        from unittest.mock import patch
        case={'family':'thorn-slot'};raw={'shots':0,'jumps':3,'ticks':90};baseline={'shots':1,'jumps':1,'ticks':100}
        failure={'ok':False,'reasons':['no_recoil'],'causal':{}}
        with patch.object(physics,'checked_purpose',return_value=failure),patch.object(physics,'_same_outcome',return_value={'ok':True}):
            result=physics._counter_judgment(case,raw,None,baseline)
        self.assertTrue(result['adjudication']['invalidates_design'])


class OriginalPickupGoalTests(unittest.TestCase):
    def fixture(self):
        return ({'required_original_pickups':['coin']},
            {'ok':True,'hp':5,'original_pickups':{'coins':2,'notes':0,
                'pickups':[{'id':'coin','kind':'coin','amount':2,'claimed':True}],
                'events':[{'id':'coin','type':'original_pickup_interaction','accepted':True,'coins':2,'notes':0}]}})

    def test_reaching_exit_without_required_pickup_is_not_same_outcome(self):
        case,raw=self.fixture();raw['original_pickups']['pickups'][0]['claimed']=False
        self.assertFalse(physics._same_outcome(case,raw)['ok'])

    def test_claimed_boolean_without_real_accepted_consumer_event_is_insufficient(self):
        case,raw=self.fixture();raw['original_pickups']['events']=[]
        self.assertFalse(physics._same_outcome(case,raw)['ok'])

    def test_original_amount_must_have_been_actually_granted(self):
        case,raw=self.fixture();raw['original_pickups']['coins']=1
        self.assertFalse(physics._same_outcome(case,raw)['ok'])

    def test_original_claim_and_accepted_grant_satisfy_declared_goal(self):
        self.assertTrue(physics._same_outcome(*self.fixture())['ok'])
