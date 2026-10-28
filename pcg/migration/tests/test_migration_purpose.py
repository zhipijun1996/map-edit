import copy
import unittest
from unittest.mock import patch
from pcg.migration import migration_purpose as purpose


def fixture():
    source=next(path for path in purpose._AUTHORS if 'plains50_ports' in path)
    return dict(id='sample',platforms=[[0,100,100,24]],reward_sites=[dict(id='cache',position=[20,82],amount=5)],
        resource_state=dict(air_shots=1),control_plan=[dict(op='shoot',direction=[-1,0])],
        ports=[dict(id='A',position=[-24,82]),dict(id='B',position=[500,82]),dict(id='C',position=[900,82])],
        route_spec=dict(from_port='A',to_port='C',via_ports=[],source_via_ports=['B'],via_waypoints=['core-waypoint-B']),
        migration_purpose=dict(schema='pcg/internal-waypoint-purpose-binding/v1',originalAuthorSource=source,
            waypoints=[dict(id='core-waypoint-B',sourcePortId='B',position=[20,82],interpretation='original_grounded_internal_dock')]))


class InternalWaypointPurposeTests(unittest.TestCase):
    def test_original_view_changes_only_explicit_core_alias(self):
        case=fixture();before=copy.deepcopy(case)
        author,view=purpose.original_view(case)
        self.assertEqual(case,before)
        self.assertEqual(view['ports'][1]['position'],[20,82])
        self.assertEqual(view['ports'][0],case['ports'][0]);self.assertEqual(view['ports'][2],case['ports'][2])
        self.assertEqual(view['platforms'],case['platforms'])
        self.assertEqual(view['resource_state'],case['resource_state'])
        self.assertEqual(view['reward_sites'],case['reward_sites'])
        self.assertEqual(view['control_plan'],case['control_plan'])
        self.assertEqual(view['route_spec']['via_ports'],['B'])

    def test_waypoint_still_requires_real_grounded_trace(self):
        case=fixture();author,_=purpose.original_view(case)
        with patch.object(author,'purpose',side_effect=lambda c,r:dict(ok=True,reasons=[],causal={})):
            valid=purpose.purpose(case,dict(frames=[dict(x=20,y=82,grounded=True)]))
            airborne=purpose.purpose(case,dict(frames=[dict(x=20,y=82,grounded=False)]))
            external_only=purpose.purpose(case,dict(frames=[dict(x=500,y=82,grounded=True)]))
        self.assertTrue(valid['ok']);self.assertFalse(airborne['ok']);self.assertFalse(external_only['ok'])
        self.assertIn('missing_actual_internal_waypoint/core-waypoint-B',external_only['reasons'])

    def test_endpoint_cannot_be_relabelled_as_internal_waypoint(self):
        case=fixture();case['migration_purpose']['waypoints'][0]['sourcePortId']='A'
        with self.assertRaisesRegex(ValueError,'external_route_endpoint'):
            purpose.original_view(case)

    def test_missing_waypoint_binding_is_rejected(self):
        case=fixture();case['migration_purpose']['waypoints']=[]
        with self.assertRaisesRegex(ValueError,'bindings_incomplete'):
            purpose.original_view(case)

    def test_unregistered_original_author_is_rejected(self):
        case=fixture();case['migration_purpose']['originalAuthorSource']='pcg/arbitrary.py'
        with self.assertRaisesRegex(ValueError,'unsupported_original'):
            purpose.original_view(case)


if __name__=='__main__':unittest.main()
