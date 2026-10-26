"""Design regressions; explicitly neither physics nor human fun evidence."""
import copy,unittest
from pcg.map_directed.catalog_feed.design_review import graph_review,reward_requests,review
from pcg.map_directed.woven_region.design import graph_for,load_policy

def graph():
    policy=load_policy();policy['topology']['core_count']=16
    return graph_for('plains-weave-0',policy)

class ExplorationIntent(unittest.TestCase):
    def test_original_regional_network_keeps_multiple_reentrant_directions(self):
        r=graph_review(graph());self.assertTrue(r['ok'],r['errors']);self.assertEqual(r['core_articulations'],[]);self.assertEqual(r['reentrant_core_fraction'],1)

    def test_two_serial_diamonds_do_not_count_as_reentrant_exploration(self):
        keys=['s','a','b','m','c','d','t']
        g=dict(entry='s',goal='t',initial_abilities=['move','jump','shot_recoil'],nodes=[dict(id=k,role='challenge',grants=[],opens=[],reward=0)for k in keys],edges=[])
        for i,(a,b)in enumerate([('s','a'),('s','b'),('a','m'),('b','m'),('m','c'),('m','d'),('c','t'),('d','t')]):
            g['edges'].append(dict(id=str(i),**{'from':a,'to':b},bidirectional=False,requires=[],switch=None,cost=1))
        before=copy.deepcopy(g);r=graph_review(g)
        self.assertFalse(r['ok']);self.assertEqual(r['reentrant_core_fraction'],0);self.assertIn('m',r['goal_unavoidable_nodes']);self.assertEqual(g,before)

    def test_rewards_are_allocated_to_two_explicit_expeditions_only(self):
        g=graph();r=reward_requests(g)
        self.assertTrue(r['ok'],r['errors']);self.assertEqual(len(r['chest_nodes']),2)
        self.assertEqual(sum(x['value']for x in r['requests'].values()),48)
        for n in g['nodes']:
            if n['role']!='reward':self.assertEqual(r['requests'][n['id']]['max_reward_sites'],0)

    def test_mainline_reward_is_not_made_optional_by_a_label(self):
        g=graph();n=next(n for n in g['nodes']if n['role']=='prep');n.update(role='reward',reward=12)
        r=reward_requests(g);self.assertFalse(r['ok']);self.assertIn('reward_not_optional_objective/'+n['id'],r['errors'])

    def test_physical_module_chests_are_counted_even_when_graph_rewards_are_zero(self):
        g=graph();modules=[];sites=[]
        for n in g['nodes']:
            local=[dict(id='free',amount=12)]
            modules.append(dict(id=n['id'],case=dict(reward_sites=local)))
            sites.append(dict(id=n['id']+'/free',amount=12))
        c=dict(exploration_graph=g,modules=modules,case=dict(reward_sites=sites))
        before=copy.deepcopy(c);r=review(c)
        self.assertFalse(r['ok']);self.assertIn('physical_chest_budget_exceeded',r['errors']);self.assertEqual(c,before)

    def test_missing_planned_chests_cannot_pass_by_filtering_everything(self):
        g=graph();c=dict(exploration_graph=g,modules=[dict(id=n['id'],case=dict(reward_sites=[]))for n in g['nodes']],case=dict(reward_sites=[]))
        r=review(c);self.assertFalse(r['ok']);self.assertTrue(any(e.startswith('reward_request_not_materialized/')for e in r['errors']))

