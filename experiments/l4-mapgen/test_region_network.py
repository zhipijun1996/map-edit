import copy
import unittest
import region_network as r


class RegionalNetworkTests(unittest.TestCase):
    def test_region_has_two_initial_approaches_and_no_mandatory_core_chain(self):
        for region in r.REGIONS:
            g=r.construct('0',region)
            self.assertEqual(r.validate_region_intent(g),[])
            self.assertEqual(r.base.validate_graph(g)[0],[])
            paths=r.approach_routes(g)
            self.assertGreaterEqual(len(paths),2)
            self.assertNotEqual(paths[0]['nodes'],paths[1]['nodes'])

    def test_bent_spine_with_side_rewards_is_rejected_too(self):
        g=r.construct('0','plains')
        # Replacing the core with a zig-zag chain must fail even when it is not
        # horizontal. This detects a topology problem, not only an art direction.
        core=g['core_nodes'];g['edges']=[e for e in g['edges'] if e['purpose']!='regional_route']
        for a,b in zip(core,core[1:]):r.base.add_edge(g,a,b,purpose='regional_route')
        self.assertIn('mandatory_core_chain_or_bottleneck',r.validate_region_intent(g))

    def test_boss_gate_bypass_still_rejected(self):
        g=r.construct('0','forest');r.base.add_edge(g,g['entry'],g['goal'])
        self.assertIn('boss_gate_bypass',r.base.validate_graph(g)[0])

    def test_premature_shortcut_unlock_rejected(self):
        g=r.construct('0','forest');g['nodes'][0]['opens'].append('expedition_return_0')
        self.assertIn('shortcut_not_earned_at_reward',r.validate_region_intent(g))

    def test_seed_changes_topology_and_objective_positions(self):
        a=r.construct('0','plains');b=r.construct('2','plains')
        self.assertNotEqual(r.base.topology_signature(a),r.base.topology_signature(b))
        self.assertNotEqual([(n['role'],n['ideal']) for n in a['nodes']],[(n['role'],n['ideal']) for n in b['nodes']])

    def test_determinism_and_actual_geometry(self):
        a=r.generate('0','plains',embedding_attempts=2)
        b=r.generate('0','plains',embedding_attempts=2)
        self.assertEqual(a['deterministic_digest'],b['deterministic_digest'])
        self.assertTrue(a['layout']['ok'])
        self.assertEqual(r.base.validate_layout(a['exploration_graph'],a['layout']),[])
        self.assertEqual(a['physics']['status'],'unverified')

    def test_region_returns_without_claiming_optional_reward(self):
        g=r.construct('0','forest')
        reward_ids={n['id'] for n in g['nodes'] if n['reward']}
        # Suppress acquisition of all optional reward flags. Ordinary core still
        # completes and none of the reachable one-way states may trap the player.
        for n in g['nodes']:
            if n['id'] in reward_ids:n['opens']=[]
        g['edges']=[e for e in g['edges'] if e['purpose']!='return_shortcut']
        self.assertEqual(r.base.validate_graph(g)[0],[])


if __name__=='__main__':unittest.main()
