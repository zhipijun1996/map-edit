"""Controller/data regressions; real boundary success is measured by Harness."""
import copy
import unittest
from unittest.mock import patch
from pcg.migration import core, corners, godot_package
from pcg.migration import corner_batch_adapter as v2,corner_batch_adapter_v3 as v3
from pcg.migration.tests.test_corner_batch_adapter import fixture


class CornerV3Tests(unittest.TestCase):
    def test_forked_body_clearance_moves_only_new_oneway_dock_eight_pixels(self):
        source,cases=fixture('game-forest-playful-module-variants-forked-bough-hh')
        doc,inputs,report=v2.adapt_data(source,cases,'basin','BOTTOM_RIGHT')
        old=copy.deepcopy(doc)
        result,new,drop=v3.lower_obstructed_bottom_dock(doc,inputs,'basin')
        self.assertEqual(drop['pixels'],8)
        port=next(p for p in result['generationContract']['ports']if p['id']=='basin')
        dock=next(o for o in result['objects']if o['id']==port['support']['objectId'])
        self.assertEqual([dock[k]for k in ('y','h')],[282,24])
        self.assertEqual(port['stagingPosition'],[960,264])
        for before,after in zip(old['objects'],result['objects']):
            if before['id']!=dock['id']:self.assertEqual(before,after,'Original ceiling and every other shape stay exact')
        self.assertEqual(doc,old)
        godot_package.audit_cases(result,new,require_replay=False)
        corners.verify_open_geometry(source,result,[dict(portId='basin',corner='BOTTOM_RIGHT')])

    def test_unobstructed_top_dock_is_not_lowered(self):
        source,cases=fixture('b31-n06-fourport-two-low-ingress')
        doc,inputs,_=v2.adapt_data(source,cases,'C','TOP_RIGHT')
        new,new_inputs,drop=v3.lower_obstructed_bottom_dock(doc,inputs,'C')
        self.assertEqual(drop['pixels'],0);self.assertEqual(new,doc);self.assertEqual(new_inputs,inputs)

    def test_real_settle_deadband_uses_original_goal_guard_instead_of_unreachable_threshold(self):
        source,cases=fixture('b31-n06-fourport-two-low-ingress')
        doc,inputs,_=v2.adapt_data(source,cases,'C','TOP_RIGHT')
        with patch('pcg.migration.corner_batch_adapter_v3.boundary_runtime.bind',side_effect=lambda d,c:(d,c,[])):
            result,bound,_=v3.bind_vertical_controls(doc,inputs,'C')
        case=next(c for c in bound if c['route_spec']['to_port']=='C')
        original=next(c for c in inputs if c['id']==case['id']);plan=case['migration_boundary_plans']['C']['egress'];length=len(original['control_plan'])
        self.assertEqual(plan[:length],original['control_plan'])
        trigger=plan[length]['trigger'];self.assertEqual(trigger['state'],'grounded');self.assertEqual(trigger['migration_goal'],original['goal']);self.assertNotIn('dynamic',trigger)
        goal=original['goal'];actual_x=1252.59
        self.assertTrue(goal[0]<=actual_x<=goal[0]+goal[2])
        terminal=next(c for c in reversed(original['control_plan'])if c['op']=='settle')
        self.assertLess(actual_x,terminal['target_x']-3,'Original generic +/-3 threshold really excludes an accepted endpoint')
        self.assertEqual(plan[-2]['op'],'jump');self.assertEqual(plan[-1]['op'],'jump_release')

    def test_entry_crosses_at_anchor_before_sideways_canonical_docking(self):
        source,cases=fixture('game-foundry-climb-change-height-base-v1-p0')
        doc,inputs,_=v2.adapt_data(source,cases,'entry','BOTTOM_LEFT')
        with patch('pcg.migration.corner_batch_adapter_v3.boundary_runtime.bind',side_effect=lambda d,c:(d,c,[])):
            result,bound,_=v3.bind_vertical_controls(doc,inputs,'entry')
        case=next(c for c in bound if c['route_spec']['from_port']=='entry')
        p=next(p for p in doc['generationContract']['ports']if p['id']=='entry')
        plan=case['migration_boundary_plans']['entry']['ingress']
        self.assertEqual(plan[0]['target_x'],p['position'][0])
        self.assertEqual(plan[1]['op'],'jump')
        guard=next(c for c in plan if c['op']=='wait')['trigger']
        self.assertEqual(guard['migration_goal'][:2],[p['stagingPosition'][0]-6,p['stagingPosition'][1]-5])
        self.assertEqual(plan[-1]['target_x'],case['spawn'][0])
        self.assertEqual(case['control_plan'],inputs[0]['control_plan'])

    def test_v3_id_does_not_overwrite_v2_configuration(self):
        self.assertEqual(v3.configuration_id('C','TOP_RIGHT'),'c-top-right-open-v3')
        self.assertNotEqual(v3.configuration_id('C','TOP_RIGHT'),v2.configuration_id('C','TOP_RIGHT'))


if __name__=='__main__':unittest.main()
