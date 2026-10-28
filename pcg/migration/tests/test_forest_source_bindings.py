"""Regression checks for real source-program binding, not physics substitutes."""
import copy
import unittest
from pcg.migration import core,game_adapter,forest_feedback_v9 as forest,forest_hollow_v10 as hollow


class ForestSourceBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sources={s['id']:s for s in game_adapter.source_entries()}

    def source(self,suffix):return next(s for key,s in self.sources.items()if key.endswith(suffix))

    def test_drop_source_keeps_real_vertical_down_input(self):
        p=forest.steps_program([dict(kind='drop_through',takeoff=[20,30],landing=[20,150],path=[[20,30],[20,150]])])
        self.assertIn('drop_through',[c['op']for c in p])
        self.assertEqual(p[-1]['trigger']['migration_goal'],[15,146,10,8])

    def test_approach_is_executed_before_deep_root_first_hook(self):
        source=self.source('deep_root_switchback');case=dict(original_pickups=[dict(id='root_coin',position=source['data']['reward_position'])])
        p=forest.program(source,case,0);first=next(i for i,c in enumerate(p)if c['op']=='grapple')
        targets=[c.get('target_x')for c in p[:first]if c['op']=='settle']
        self.assertIn(592,targets)
        self.assertTrue(any(c.get('trigger',{}).get('migration_goal',[0,0])[1]==330 for c in p[:first]))

    def test_outside_departure_requires_observed_airborne_y(self):
        source=self.source('backbranch_turn');case=dict(original_pickups=[dict(id='root_coin',position=source['data']['reward_position'])])
        p=forest.program(source,case,0);first=next(i for i,c in enumerate(p)if c['op']=='grapple')
        self.assertTrue(any('source_min_y'in c.get('trigger',{})for c in p[:first]))
        self.assertNotIn('jump',[c['op']for c in p[:first]])

    def test_normal_window_approaches_its_actual_hook_not_first_gap(self):
        source=self.source('double_window');case=dict(original_pickups=[dict(id='root_coin',position=source['data']['reward_position'])])
        p=forest.program(source,case,0);first=next(i for i,c in enumerate(p)if c['op']=='grapple')
        targets=[c.get('target_x')for c in p[:first]if c['op']=='settle']
        self.assertEqual(targets[-1],816)
        self.assertEqual(p[first]['aim_target'],source['data']['hook_anchors'][0]['position'])

    def test_named_cavity_binds_both_actual_hooks(self):
        source=self.source('forest_hollow_trunk_geometry__cavity');case={};p=hollow.program(source,case,0)
        self.assertEqual([a['anchor']for a in case['source_action_program']if a['action']=='H'],['cavity_ring_a','cavity_ring_b'])
        self.assertEqual(len([c for c in p if c['op']=='grapple']),2)

    def test_source_elbow_has_body_departure_guard_before_second_hook(self):
        source=self.source('forest_hollow_trunk_geometry__cavity_elbow');case={};p=hollow.program(source,case,0)
        indices=[i for i,c in enumerate(p)if c['op']=='grapple'];guards=[i for i,c in enumerate(p)if'source_right_of'in c.get('trigger',{})]
        self.assertEqual(len(indices),2);self.assertTrue(indices[0]<guards[0]<indices[1])
        self.assertTrue(case['original_named_driver']['onlyInputTranslation'])


if __name__=='__main__':unittest.main()
