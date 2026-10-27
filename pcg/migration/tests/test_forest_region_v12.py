import copy
import unittest
from pcg.migration import game_adapter,forest_region_v12 as region

class OriginalForestRegion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sources={s['id']:s for s in game_adapter.source_entries()}
    def source(self,suffix):return next(s for k,s in self.sources.items()if k.endswith(suffix))
    def test_actual_world_backlook_note_minimum_is_kept(self):
        source=self.source('backlook_fruit_cache');self.assertEqual(source['data']['risk_reward']['notes'],0)
        chest,proof=region.chest_for(source)
        self.assertEqual(chest['resources'],[dict(kind='coin',amount=4),dict(kind='note',amount=1)])
        self.assertIn('max(1,raw.notes)',proof['origin'])
    def test_original_hard_optional_tier_is_not_renamed(self):
        chest,_=region.chest_for(self.source('z_descending_return_v0'));self.assertEqual(chest['tier'],'hard_optional');self.assertEqual(chest['resources'][1]['amount'],2)
    def test_uninstalled_playful_source_is_not_claimed_world_admission(self):
        chest,proof=region.chest_for(self.source('l_hollow_reward_loop'));self.assertEqual(chest['resources'][1]['amount'],0);self.assertIn('not original-world admission',proof['origin'])
    def test_ordinary_optional_H_branch_executes_real_source_return(self):
        source=self.source('backlook_fruit_cache');case={};plan=region.program(source,case,0)
        ops=[c['op']for c in plan];self.assertIn('native_region_interact',ops);self.assertIn('native_region_choose',ops);self.assertNotIn('native_pickup_interact',ops)
        self.assertEqual(case['source_action_program'],[]);self.assertTrue(case['source_optional_action_program']);self.assertEqual(case['source_ordinary_reward_itinerary']['after'][-1]['landing'],source['data']['goal'])
    def test_arrival_and_claim_marker_without_native_choice_fails(self):
        chest,_=region.chest_for(self.source('backlook_fruit_cache'));case=dict(original_region_chests=[chest],required_region_chest_choices=[dict(id='source_cache',kind='coin')])
        raw=dict(ok=True,hp=5,returns=0,original_region_chests=dict(consumer=region.native.SERVICE,interaction_radius=80,resources_reset=False,modal_open=False,chests=[dict(id='source_cache',claimed=True)],events=[],coins=4,notes=0))
        outcome=region.purpose(case,raw);self.assertFalse(outcome['ok']);self.assertIn('original_region_choice_not_actually_claimed',outcome['reasons'])
    def test_OR_does_not_grant_both_resources(self):
        chest,_=region.chest_for(self.source('backlook_fruit_cache'));case=dict(original_region_chests=[chest],required_region_chest_choices=[dict(id='source_cache',kind='coin')])
        snapshot=dict(consumer=region.native.SERVICE,interaction_radius=80,resources_reset=False,modal_open=False,chests=[dict(id='source_cache',claimed=True)],events=[dict(type='native_region_choose',id='source_cache',kind='coin',accepted=True)],coins=4,notes=1)
        outcome=region.purpose(case,dict(ok=True,hp=5,returns=0,original_region_chests=snapshot));self.assertFalse(outcome['ok']);self.assertIn('original_region_OR_amount_not_exact',outcome['reasons'])
if __name__=='__main__':unittest.main()
