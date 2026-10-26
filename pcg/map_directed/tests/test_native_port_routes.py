"""Routing regressions: ordered Port evidence cannot become all-to-all access."""
import unittest
from unittest.mock import patch
from pcg.map_directed.content_domains.routes import route_section
from pcg.map_directed.content_domains.build import owned_results
from pcg.map_directed.content_domains.failure_boundary_probe import prune


class NativePortRoutes(unittest.TestCase):
    def test_shared_port_and_program_target_keeps_correct_support_after_floor_pruning(self):
        target=dict(support_indices=[1],position=[64,80])
        module=dict(case=dict(platforms=[[0,500,700,32],[0,96,128,32]],ports=[dict(support_index=1)]),
                    action_clearance=[[0,0,128,96]],center=target,ports={'A':dict(dock=target)},
                    port_transitions={'A>A':[dict(target=target)]},center_to_port={'A':[dict(target=target)]},
                    adaptation={},variant_id='shared-support')
        # Isolate the support remap from unrelated shape/Port contract checks.
        with patch('pcg.map_directed.content_domains.failure_boundary_probe.declare',side_effect=lambda m,c:m),patch('pcg.map_directed.content_domains.failure_boundary_probe.validate',return_value=[]),patch('pcg.map_directed.content_domains.failure_boundary_probe.regions',return_value=[[0,0,128,128]]):
            result=prune(module)
        self.assertEqual(result['center']['support_indices'],[0])
        self.assertEqual(result['port_transitions']['A>A'][0]['target']['support_indices'],[0])
        self.assertEqual(module['center']['support_indices'],[1])

    def test_variant_motion_samples_are_not_merged_by_a_shared_prefix(self):
        modules=[dict(variant_id='recipe'),dict(variant_id='recipe/mirror-x'),dict(variant_id='recipe/mirror-x/map-failure-boundary')]
        results={k:dict(id=k,marker=i)for i,k in enumerate(['recipe/A>B','recipe/mirror-x/A>B','recipe/mirror-x/map-failure-boundary/A>B'])}
        rows=owned_results(modules,results)
        self.assertEqual([r['marker']for r in rows['recipe']],[0])
        self.assertEqual([r['marker']for r in rows['recipe/mirror-x']],[1])
        self.assertEqual([r['marker']for r in rows['recipe/mirror-x/map-failure-boundary']],[2])

    def fixture(self):
        return dict(nodes=dict(
            choice=dict(center_port='A',port_transitions={'A>B':[dict(id='actual-upper-challenge')],'A>C':[dict(id='actual-lower-challenge')],'C>C':[dict(id='reward-and-return')]},ports={'C':dict(target=dict(position=[0,0]))},center_to_port={'B':[dict(id='incorrect-centre-detour')]}),
            upper=dict(port_transitions={'B>A':[]}),lower=dict(port_transitions={'C>A':[]})),
            edges={'B':dict(**{'from':'choice'},forward_waypoints=[dict(id='upper-seam')],reverse_waypoints=[dict(id='reverse-upper-seam')]),'C':dict(**{'from':'choice'},forward_waypoints=[dict(id='lower-seam')],reverse_waypoints=[dict(id='reverse-lower-seam')])})

    def test_native_choice_uses_the_declared_pair_without_forcing_a_centre(self):
        c=self.fixture();steps=[dict(edge_id='B',**{'from':'choice','to':'upper'})]
        self.assertEqual([p['id']for p in route_section(c,steps,0)],['actual-upper-challenge','upper-seam'])

    def test_undeclared_cross_connection_is_rejected(self):
        c=self.fixture();steps=[dict(edge_id='C',**{'from':'lower','to':'choice'}),dict(edge_id='B',**{'from':'choice','to':'upper'})]
        with self.assertRaisesRegex(ValueError,'unsupported_ordered_port_pair/choice/C>B'):route_section(c,steps,1)

    def test_same_port_reward_excursion_is_not_skipped_as_a_turnaround(self):
        c=self.fixture();steps=[dict(edge_id='C',**{'from':'lower','to':'choice'}),dict(edge_id='C',**{'from':'choice','to':'lower'})]
        self.assertEqual([p['id']for p in route_section(c,steps,1)],['reward-and-return','lower-seam'])


if __name__=='__main__':unittest.main()
