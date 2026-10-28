import unittest
from pcg.migration.forest_region_ui_v16 import bind_ui

class PausedOriginalUIIntent(unittest.TestCase):
    def case(self):return dict(id='source',generation_rule={},required_region_chest_choices=[dict(id='cache',kind='coin')],control_plan=[dict(op='jump',trigger=dict(after=0)),dict(op='native_region_interact',trigger=dict(after=4)),dict(op='native_region_choose',trigger=dict(after=0),kind='coin'),dict(op='settle',trigger=dict(after=0),target_x=500)])
    def test_explicit_two_UI_intents_share_one_physical_interaction_trigger(self):
        original=self.case();fixed=bind_ui(original);plan=fixed['control_plan']
        self.assertEqual(plan[1],dict(op='native_region_select',trigger=dict(after=4),kind='coin'))
        self.assertEqual(plan[0],original['control_plan'][0]);self.assertEqual(plan[2],original['control_plan'][-1]);self.assertFalse(fixed['native_region_UI_intent']['autoRewardGrant']);self.assertEqual(fixed['max_frames']+180,3600)
    def test_missing_explicit_choice_cannot_be_invented(self):
        case=self.case();case['control_plan'].pop(2)
        with self.assertRaisesRegex(ValueError,'explicit_adjacent'):bind_ui(case)
    def test_unsupported_choice_cannot_be_substituted(self):
        case=self.case();case['control_plan'][2]['kind']='random'
        with self.assertRaisesRegex(ValueError,'explicit_adjacent'):bind_ui(case)
if __name__=='__main__':unittest.main()
