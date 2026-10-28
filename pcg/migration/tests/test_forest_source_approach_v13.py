import unittest
from pcg.migration import game_adapter,forest_source_approach_v13 as approach

class OriginalApproach(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sources={s['id']:s for s in game_adapter.source_entries()}
    def source(self,suffix):return next(s for k,s in self.sources.items()if k.endswith(suffix))
    def test_deep_drop_keeps_intermediate_OWP_and_requests_real_Down(self):
        source=self.source('deep_root_switchback');case=dict(original_pickups=[dict(position=source['data']['reward_position'])]);plan=approach.program(source,case,0)
        guards=[c['trigger']for c in plan if'source_drop_until_y'in c.get('trigger',{})]
        self.assertTrue(guards);self.assertEqual(guards[0]['source_drop_until_y'],334);self.assertEqual(guards[0]['state'],'grounded')
        self.assertEqual(source['data']['platforms'][6]['rect'][1],240)
    def test_walk_to_authored_takeoff_does_not_change_fixture_spawn(self):
        source=self.source('double_fruit_s');spawn=source['data']['spawn'][:];case=dict(original_pickups=[dict(position=source['data']['reward_position'])]);plan=approach.program(source,case,0)
        self.assertEqual(source['data']['spawn'],spawn);self.assertEqual(plan[0]['op'],'settle');self.assertEqual(plan[0]['target_x'],192)
        self.assertTrue(case['original_source_approach_repair']['sourceSpawnUnchanged'])
    def test_unaccepted_second_R_is_not_implemented_recoil(self):
        case=dict(source_action_program=[dict(action='R'),dict(action='R')],original_pickups=[],required_original_pickups=[]);raw=dict(ok=True,hp=5,returns=0,shots=1)
        result=approach.purpose(case,raw);self.assertFalse(result['ok']);self.assertIn('original_recoil_actions_not_actually_accepted',result['reasons'])
if __name__=='__main__':unittest.main()
