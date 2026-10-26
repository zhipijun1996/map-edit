"""CSP regressions independent of old result archives or a Godot install."""
import copy,unittest
from pcg.map_directed.shape_search.search import search,closed_solids

def template(key,rects,port,normal,clearance=()):
    return dict(id=key,variant_id=key+'/a',source_shape_sha256='fixture',case=dict(platforms=rects,one_way_platform_indices=[]),
        ports={'e':dict(position=port,normal=normal)},action_clearance=list(clearance),
        motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),
        spec=dict(placement=[99999,99999]))

class ShapeSearchChecks(unittest.TestCase):
    def test_motion_control_dummy_gate_is_not_a_collider(self):
        m=template('a',[[0,0,10,10]],[10,0],[1,0])
        m['case']['latches']=[dict(gate=[20,0,5,20],ferry_id='actual-carrier'),dict(gate=[30,0,5,20],starts_ferry='other-carrier')]
        self.assertEqual(closed_solids(m),[[0,0,10,10],[30,0,5,20]])
    def test_budget_is_a_hard_bound_even_after_backtracking(self):
        a=template('a',[[0,0,20,20]],[10,0],[1,0]);b=template('b',[[0,0,20,20]],[0,0],[-1,0])
        r=search(self.graph(),{'a':[a]*10,'b':[b]*10},'fixed',budget=4)
        self.assertEqual(r['status'],'budget_exhausted');self.assertEqual(r['expanded'],4)
    def graph(self):return dict(nodes=[dict(id='a'),dict(id='b')],edges=[dict(id='e',**{'from':'a','to':'b'})])
    def test_interlocking_actual_shapes_are_not_rejected_by_bounds(self):
        a=template('a',[[0,0,10,30],[10,20,20,10]],[30,0],[1,0])
        b=template('b',[[-20,0,20,10]],[0,0],[-1,0])
        d={'a':[a],'b':[b]}
        self.assertEqual(search(self.graph(),d,'fixed','aabb')['status'],'unsatisfied')
        r=search(self.graph(),d,'fixed');self.assertEqual(r['status'],'feasible')
        self.assertEqual(r['placements']['a']['position'],[0,0]);self.assertEqual(r['placements']['b']['position'],[30,0])
    def test_solid_in_actual_action_space_is_a_real_backtrack_reason(self):
        a=template('a',[[0,0,10,30],[10,20,20,10]],[30,0],[1,0],[[12,-2,12,20]])
        b=template('b',[[-20,0,20,10]],[0,0],[-1,0]);d={'a':[a],'b':[b]}
        self.assertEqual(search(self.graph(),d,'fixed','shape_only')['status'],'feasible')
        r=search(self.graph(),d,'fixed');self.assertEqual(r['status'],'unsatisfied');self.assertGreater(r['rejections']['actual_action_space_blocked'],0)
    def test_capabilities_and_actual_entry_resources_are_not_ignored(self):
        a=template('a',[[0,0,10,10]],[10,0],[1,0]);b=template('b',[[0,0,10,10]],[0,0],[-1,0]);d={'a':[a],'b':[b]}
        self.assertEqual(search(self.graph(),d,'x',abilities=['move','jump'])['status'],'unsatisfied')
        self.assertEqual(search(self.graph(),d,'x',entry_state=dict(grounded=True,air_shots=0,speed=0))['status'],'unsatisfied')
        self.assertEqual(search(self.graph(),d,'x',entry_state=dict(grounded=True,air_shots=1,speed=200))['status'],'unsatisfied')
    def test_fixed_seed_replay_ignores_source_placement(self):
        a=template('a',[[0,0,10,10]],[10,0],[1,0]);b=template('b',[[0,0,10,10]],[0,0],[-1,0]);d={'a':[a],'b':[b]}
        r=search(self.graph(),d,'same');d['a'][0]['spec']['placement']=[-500,-600]
        self.assertEqual(r['layout_signature'],search(self.graph(),d,'same')['layout_signature'])
    def test_neighbor_may_not_enter_a_real_saw_sweep(self):
        a=template('a',[[0,20,10,10]],[30,0],[1,0]);a['case']['saws']=[dict(origin=[22,0],travel=[4,0],radius=2)]
        b=template('b',[[-10,-1,4,2]],[0,0],[-1,0])
        r=search(self.graph(),{'a':[a],'b':[b]},'fixed')
        self.assertEqual(r['status'],'unsatisfied');self.assertEqual(r['rejections']['dynamic_sweep_into_neighbor'],1)
    def test_port_alignment_does_not_override_actor_aperture(self):
        a=template('a',[[0,20,10,10]],[30,0],[1,0]);b=template('b',[[0,20,10,10]],[0,0],[-1,0])
        a['ports']['e']['aperture']=[20,-20,20,40];b['ports']['e']['aperture']=[-10,-20,20,40]
        r=search(self.graph(),{'a':[a],'b':[b]},'fixed')
        self.assertEqual(r['status'],'unsatisfied');self.assertEqual(r['rejections']['actor_aperture_too_small'],1)
