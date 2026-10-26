"""Contract/search failures, never synthetic substitutes for Godot evidence."""
import copy,unittest
from pcg.map_directed.block_grid.contracts import anchor,declare,validate,state_entails,joined_block_origin,placed_cells
from pcg.map_directed.shape_search.search import search
from pcg.map_directed.block_grid.policy import branch_review,load,review
from pcg.map_directed.director import regional

def unit(key,edge,cells):
    p=dict(id='e',position=anchor([0,0],edge),normal={'E':[1,0],'W':[-1,0]}[edge],grid=dict(cell=[0,0],edge=edge,profile='test-floor'),aperture=[96 if edge=='E'else-32,32,64,64])
    m=dict(id=key,variant_id=key,ports={'e':p},case=dict(platforms=[[0,100,128,8]],saws=[],moving_platforms=[],latches=[],one_way_platform_indices=[]),
        action_clearance=[],spec=dict(node_id=key,placement=[0,0]),source_shape_sha256='test',
        motion_contract=dict(mode='grounded_dock',capabilities=['move'],entry_grounded=True,required_air_shots=0,maximum_entry_speed=1))
    return declare(m,cells)

class BlockGrid(unittest.TestCase):
    def test_direct_join_owns_adjacent_cells_not_two_overlapping_port_blocks(self):
        a=unit('a','E',[[0,0]]);b=unit('b','W',[[0,0]])
        origin=joined_block_origin([0,0],a['ports']['e'],b['ports']['e'])
        self.assertEqual(origin,[1,0])
        self.assertFalse(placed_cells(a,[0,0])&placed_cells(b,[128,0]))
        self.assertEqual(a['ports']['e']['position'],[b['ports']['e']['position'][0]+128,b['ports']['e']['position'][1]])

    def test_nonlevel_ports_and_local_grid_origins_close_in_integer_coordinates(self):
        # A exits its upper-right cell; B enters its lower-left cell. Local
        # grid origins are independent of the Module placement origin.
        a=dict(normal=[1,0],grid=dict(cell=[3,-2]));b=dict(normal=[-1,0],grid=dict(cell=[0,2]))
        pose=joined_block_origin([5,7],a,b,[128,-128],[-128,128])
        self.assertEqual(pose,[11,1])
        pa=anchor([3,-2],'E',origin=[128,-128]);pb=anchor([0,2],'W',origin=[-128,128])
        self.assertEqual([pa[i]+[5,7][i]*128 for i in range(2)],[pb[i]+pose[i]*128 for i in range(2)])
        up=dict(normal=[0,-1],grid=dict(cell=[2,0]));down=dict(normal=[0,1],grid=dict(cell=[1,3]))
        self.assertEqual(joined_block_origin([0,0],up,down),[1,-4])

    def test_reserved_empty_block_rejects_even_without_collider_overlap(self):
        a=unit('a','E',[[0,0],[0,1],[1,1]]);b=unit('b','W',[[0,0],[0,1]])
        g=dict(nodes=[dict(id='a'),dict(id='b')],edges=[dict(id='e',**{'from':'a','to':'b'})])
        self.assertEqual(search(g,{'a':[a],'b':[b]},'fixed',require_blocks=False)['status'],'feasible')
        r=search(g,{'a':[a],'b':[b]},'fixed',require_blocks=True)
        self.assertEqual(r['status'],'unsatisfied');self.assertIn('block_occupancy_overlap',r['rejections'])

    def test_internal_face_cannot_be_renamed_as_a_boundary_port(self):
        a=unit('a','E',[[0,0],[1,0]])
        self.assertIn('port_not_on_shape_boundary/e',validate(a))

    def test_shared_coarse_air_keeps_exact_body_and_dynamic_conflicts_closed(self):
        a=unit('a','E',[[0,0],[0,1],[1,1]]);b=unit('b','W',[[0,0],[0,1]])
        a['action_clearance']=[[144,200,24,36]]
        b['case']['platforms'].append([0,160,128,8])
        g=dict(nodes=[dict(id='a'),dict(id='b')],edges=[dict(id='e',**{'from':'a','to':'b'})])
        domains={'a':[a],'b':[b]}
        self.assertEqual(search(g,domains,'air',require_blocks=True)['status'],'unsatisfied')
        self.assertEqual(search(g,domains,'air',require_blocks=True,allow_shared_air=True)['status'],'feasible')
        b['case']['platforms'][-1][1]=210
        self.assertEqual(search(g,domains,'blocked',require_blocks=True,allow_shared_air=True)['status'],'unsatisfied')
        b['case']['platforms'][-1][1]=160
        b['case']['saws']=[dict(origin=[24,218],travel=[0,0],radius=20)]
        r=search(g,domains,'swept',require_blocks=True,allow_shared_air=True)
        self.assertEqual(r['status'],'unsatisfied');self.assertIn('foreign_occupancy_blocks_action',r['rejections'])

    def test_grid_is_configurable_but_does_not_allow_half_block_placements(self):
        self.assertEqual(anchor([2,1],'N',256),[640,256])
        a=unit('a','E',[[0,0]]);a['ports']['e']['position'][1]+=1
        self.assertIn('port_not_at_boundary_center/e',validate(a))

    def test_unknown_or_wider_exit_state_never_proves_entry_requirements(self):
        self.assertFalse(state_entails({'airShots':'UNKNOWN'},{'airShots':[1,1]}))
        self.assertFalse(state_entails({'velocity':{'x':[0,20]}},{'velocity':{'x':[0,1]}}))
        self.assertTrue(state_entails({'grounded':True,'airShots':[1,1]},{'grounded':True,'airShots':[1,1]}))

    def test_all_three_return_modes_use_real_directed_arcs(self):
        g=regional.construct('block-region-eval-0/design-0','plains',20,reward_expeditions=6,reward_return_modes=['foldback','loop_back','merge']*2,core_edge_factor=1.05,approach_steps=(7,14),reuse_perimeter_anchors=True)
        self.assertFalse(regional.base.validate_graph(g)[0])
        for b in g['branches']:self.assertEqual(branch_review(g,b),[])
        b=g['branches'][0];last=b['nodes'][-1];edge=next(e for e in g['edges']if e['to']==last);edge['bidirectional']=False
        self.assertIn('foldback_reverse_missing',branch_review(g,b))

    def test_reward_kinds_and_unknown_values_do_not_become_free_major_items(self):
        g=regional.construct('block-region-eval-0/design-0','plains',20,reward_expeditions=6,reward_return_modes=['foldback','loop_back','merge']*2,core_edge_factor=1.05,approach_steps=(7,14),reuse_perimeter_anchors=True)
        g['reward_allocations']=[dict(id=str(i),node=g['entry'],kind='currency',value=1)for i in range(12)]
        r=review(g,load());self.assertEqual(r['reward_counts']['major_item'],0);self.assertIn('reward_count/major_item',r['errors']);self.assertFalse(r['production_ready'])

if __name__=='__main__':unittest.main()
