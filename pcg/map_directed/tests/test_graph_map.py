"""Regression checks for observed whole-world failures, not playability claims."""
import copy,unittest
from pcg.prototype.workshop.map_supports import configure
from pcg.map_directed.graph_map.domains import assignments,bind
from pcg.map_directed.graph_map.probes import evaluate
from pcg.map_directed.shape_search.search import search
from pcg.map_directed.tests.test_shape_search import template

class GraphMapChecks(unittest.TestCase):
    def module(self):
        target=dict(id='dock',position=[100,82],region=[97,80,6,4],support_indices=[0])
        return dict(id='owned',case=dict(platforms=[[0,100,100,8],[100,100,100,8],[90,108,30,8],[400,100,60,8]]),ports={'a':dict(dock=target)},center=copy.deepcopy(target),boundary_gates=[],port_transitions={},adaptation={},content_version='before')
    def test_joined_owned_floor_accepts_either_real_coplanar_support(self):
        m=self.module();r=configure(dict(module=m))['modules'][0]
        self.assertEqual(r['ports']['a']['dock']['support_indices'],[0,1])
        self.assertEqual(r['center']['position'],m['center']['position'])
        self.assertEqual(r['case'],m['case']);self.assertEqual(m['center']['support_indices'],[0])
    def test_wrong_height_or_absent_declared_support_is_not_normalized_away(self):
        m=self.module();m['center']['support_indices']=[2]
        with self.assertRaisesRegex(ValueError,'declared_support_not_at_target_floor'):configure(dict(module=m))
    def test_boss_role_requires_an_actual_encounter_contract(self):
        g=dict(initial_abilities=['jump'],nodes=[dict(id='boss')],edges=[dict(id='e',**{'from':'a','to':'boss'},bidirectional=True)])
        m=dict(ports={'p':{}},motion_contract=dict(capabilities=['move','jump']),port_transitions={'p>p':[]})
        self.assertEqual(assignments(g,dict(id='boss',role='boss'),m)[0],[])
        m['boss_contract']={};self.assertEqual(assignments(g,dict(id='boss',role='boss'),m)[0],[])
        m['boss_contract']={'scene':'real'};self.assertEqual(len(assignments(g,dict(id='boss',role='boss'),m)[0]),1)
    def test_failed_unattempted_probe_is_never_a_success(self):
        q=dict(prefix_legs=0,attack_id='attack',gate=dict(bounds=[0,0,8,512],direction=[1,0]),goal=dict(region=[-100,0,10,10]),protected_reward_ids=[])
        case=dict(gate_probe=q,pilot_program=[])
        r=dict(ok=False,reason='setup_failed',frames=[],pilot=dict(legs=[]))
        self.assertEqual(evaluate(case,r)['status'],'inconclusive')
    def graph(self):return dict(nodes=[dict(id='a'),dict(id='b')],edges=[dict(id='e',**{'from':'a','to':'b'})])
    def test_zero_wall_budget_does_not_start_unbounded_search(self):
        a=template('a',[[0,0,10,10]],[10,0],[1,0]);b=template('b',[[0,0,10,10]],[0,0],[-1,0])
        r=search(self.graph(),{'a':[a],'b':[b]},'x',wall_budget_seconds=0)
        self.assertEqual(r['status'],'budget_exhausted');self.assertEqual(r['expanded'],0)
    def test_probe_budget_is_hard_even_without_forward_check(self):
        a=template('a',[[0,0,20,20]],[10,0],[1,0]);b=template('b',[[0,0,20,20]],[0,0],[-1,0])
        r=search(self.graph(),{'a':[a]*10,'b':[b]*10},'x',probe_budget=2)
        self.assertEqual(r['status'],'budget_exhausted');self.assertEqual(r['feasibility_probes'],2)
    def test_solution_rejection_backtracks_without_deleting_graph(self):
        a=template('a',[[0,0,10,10]],[10,0],[1,0]);b=template('b',[[0,0,10,10]],[0,0],[-1,0]);calls=[]
        def reject_once(ms):calls.append(ms);return len(calls)>1
        r=search(self.graph(),{'a':[a,a],'b':[b]},'x',solution_check=reject_once)
        self.assertEqual(r['status'],'feasible');self.assertEqual(len(r['modules']),2);self.assertEqual(len(calls),2)
