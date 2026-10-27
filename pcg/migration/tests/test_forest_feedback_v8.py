import copy,hashlib,unittest
from pcg.migration import core,forest_feedback_v7,forest_feedback_v8

class ForestFeedbackTests(unittest.TestCase):
    def test_exact_original_driver_git_blobs(self):
        for row in core.read(core.STATE/'original-forest-driver-v7.json')['files']:
            data=(core.REPO/row['localPath']).read_bytes()
            self.assertEqual(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),row['gitBlob'])
    def test_wrong_hook_target_not_accepted_by_aggregate_contact_count(self):
        case=dict(source_action_program=[dict(action='H',anchor='a'),dict(action='H',anchor='b')])
        raw=dict(ok=True,hp=5,hook_contacts=2,original_hook_contacts=[dict(source_id='b'),dict(source_id='a')])
        self.assertFalse(forest_feedback_v7.purpose(case,raw)['ok'])
        raw['original_hook_contacts']=[dict(source_id='a'),dict(source_id='b')]
        self.assertTrue(forest_feedback_v7.purpose(case,raw)['ok'])
    def test_source_without_reward_does_not_invent_pickup_or_grant(self):
        source=dict(data=dict(spawn=[0,0],goal=[100,0],steps=[],hook_anchors=[dict(id='a',position=[50,-80])],action_program=[dict(action='H',anchor='a'),dict(action='R',direction=[-1,0])]))
        plan=forest_feedback_v8.program(source,dict(original_pickups=[]),0)
        self.assertEqual([c['op']for c in plan].count('grapple'),1)
        self.assertEqual([c['op']for c in plan].count('shoot'),1)
        self.assertNotIn('native_pickup_interact',[c['op']for c in plan])
        self.assertTrue(all(c['op']in('settle','wait','jump','jump_release','grapple','shoot')for c in plan))
    def test_declared_reward_cannot_silently_disappear(self):
        source=dict(data=dict(spawn=[0,0],goal=[100,0],reward_position=[80,0],steps=[],hook_anchors=[dict(id='a',position=[50,-80])],action_program=[dict(action='H',anchor='a')]))
        with self.assertRaisesRegex(ValueError,'consumer_not_bound'):forest_feedback_v8.program(source,dict(original_pickups=[]),0)

if __name__=='__main__':unittest.main()
