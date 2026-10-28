import unittest
from pcg.migration import game_adapter,forest_departure_v11 as departure

class DepartureDispatch(unittest.TestCase):
    def test_every_source_observation_is_actually_dispatched(self):
        source=next(s for s in game_adapter.source_entries()if s['id'].endswith('backbranch_turn'))
        case=dict(original_pickups=[dict(id='root_coin',position=source['data']['reward_position'])])
        plan=departure.program(source,case,0)
        guards=[c['trigger']for c in plan if'source_min_y'in c.get('trigger',{})]
        self.assertTrue(guards)
        self.assertTrue(all(t['state']=='free'for t in guards))

    def test_grounded_f0_cast_cannot_pass_descending_source_claim(self):
        case=dict(hooks=[dict(x=246,y=78)],source_departure_observation=dict(kind='outside_descending_cast'),source_action_program=[dict(action='H',anchor='side_fruit')],original_pickups=[],required_original_pickups=[])
        raw=dict(ok=True,hp=5,returns=0,hook_contacts=1,original_hook_contacts=[dict(source_id='side_fruit')],frames=[dict(x=380,y=0,grounded=True,requested=[dict(type='grapple')])])
        result=departure.purpose(case,raw)
        self.assertFalse(result['ok']);self.assertIn('original_descending_cast_not_observed',result['reasons'])

if __name__=='__main__':unittest.main()
