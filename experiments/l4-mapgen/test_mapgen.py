import copy,json,tempfile,unittest
import mapgen as m

def node(n,role='challenge',grants=None,reward=0,opens=None):
 return {'id':n,'role':role,'grants':grants or [],'opens':opens or [],'reward':reward,'risk':1,'ideal':[0,0]}

def graph(nodes,entry='s',goal='g'):
 return {'entry':entry,'goal':goal,'initial_abilities':['jump','shot_recoil'],'nodes':nodes,'edges':[],'branches':[{'nodes':['r']}]}

class GeneratorTests(unittest.TestCase):
 def test_seed_reproducible(self):
  a=m.generate('A','0','plains',embedding_attempts=2);b=m.generate('A','0','plains',embedding_attempts=2)
  self.assertEqual(a['deterministic_digest'],b['deterministic_digest'])
  self.assertEqual(len(a['exploration_graph']['nodes']),18)
 def test_namespace_independence(self):
  a=m.RandomStream('s','mission');b=m.RandomStream('s','mission');junk=m.RandomStream('s','decoration')
  for _ in range(30):junk.next_int(100)
  self.assertEqual([a.next_int(100) for _ in range(20)],[b.next_int(100) for _ in range(20)])
 def test_true_asp_state_validation(self):
  self.assertIsNotNone(m.clingo)
  g,proof=m.asp_b(m.mission('0','forest'),'0')
  self.assertTrue(g);self.assertIn('opened-switch-mask',proof['scope']);self.assertEqual(m.validate_graph(g)[0],[])
 def test_unreachable_self_locked_grant(self):
  g=graph([node('s'),node('k',grants=['grapple']),node('g','boss')]);m.add_edge(g,'s','k',requires=['grapple']);m.add_edge(g,'k','g')
  errors,proof=m.validate_graph(g);self.assertIn('goal_unreachable',errors);self.assertIn('objective_unreachable:k',errors);self.assertFalse(proof['ability_lock_correct'])
 def test_universal_softlock(self):
  g=graph([node('s'),node('g','boss'),node('pit')]);m.add_edge(g,'s','g');m.add_edge(g,'s','pit',bidirectional=False)
  self.assertTrue(any(x.startswith('softlock_states') for x in m.validate_graph(g)[0]))
 def test_boss_gate_bypass(self):
  g=m.mission('0','plains');m.add_edge(g,'m0','m5',purpose='bad_shortcut')
  self.assertIn('boss_gate_bypass',m.validate_graph(g)[0])
 def test_unknown_switch(self):
  g=m.mission('0','plains');g['edges'][0]['switch']='ungranted_switch'
  self.assertTrue(any(x.startswith('unknown_switch') for x in m.validate_graph(g)[0]))
 def test_reward_detour_same_state(self):
  g=graph([node('s'),node('r',reward=12),node('k',grants=['key']),node('g','boss')]);m.add_edge(g,'s','r',cost=1);m.add_edge(g,'s','k',cost=100);m.add_edge(g,'k','r',cost=100);m.add_edge(g,'r','g',cost=1,requires=['key'])
  self.assertEqual(m.validate_graph(g)[0],[])
  report=m.graph_metrics(g);self.assertEqual(report['main_completion_cost'],201);self.assertEqual(report['rewards'][0]['completion_detour'],0)
 def test_label_invariant_fingerprint(self):
  g=m.mission('1','forest');renamed=copy.deepcopy(g);names={n['id']:'renamed_'+str(100-i) for i,n in enumerate(renamed['nodes'])}
  for n in renamed['nodes']:n['id']=names[n['id']]
  for e in renamed['edges']:e['from']=names[e['from']];e['to']=names[e['to']]
  renamed['entry']=names[g['entry']];renamed['goal']=names[g['goal']]
  self.assertEqual(m.topology_signature(g),m.topology_signature(renamed));self.assertEqual(m.topology_signature(g,True),m.topology_signature(renamed,True))
 def test_strict_real_catalog_rejects_fake_hub(self):
  g=m.mission('0','plains');catalog={'templates':[{'id':'canonical','roles':[n['role'] for n in g['nodes']],'ports':[{'id':'in','type':'grounded'},{'id':'out','type':'grounded'}]}]}
  proof=m.strict_catalog_feasibility(g,catalog);self.assertFalse(proof['ok']);self.assertTrue(any(x['required_distinct_connections']>2 for x in proof['errors']))
 def test_layout_success_is_independently_validated(self):
  result=m.generate('A','0','plains',embedding_attempts=8);self.assertTrue(result['layout']['ok']);self.assertEqual(m.validate_layout(result['exploration_graph'],result['layout']),[])
  broken=copy.deepcopy(result['layout']);broken['rooms'][1]['cells'].append(broken['rooms'][0]['cells'][0]);self.assertIn('overlapping_room_masks',m.validate_layout(result['exploration_graph'],broken))
 def test_unplanned_room_contact_counterexample(self):
  rooms=[]
  for name,x,y in [('a',0,0),('b',10,0),('c',5,1)]:
   rooms.append({'node':name,'cells':[[x+i,y+j] for i in range(3) for j in range(3)],'port_type':'grounded','x':x,'y':y})
  g=graph([node('a'),node('b'),node('c')],entry='a',goal='b');m.add_edge(g,'a','b')
  routes,_=m.route_layout(g,rooms,m.RandomStream('0','route'))
  self.assertIsNotNone(routes)
  self.assertEqual(m.validate_layout(g,{'ok':True,'rooms':rooms,'corridors':routes}),[])
  # Explicit old bad route touches the undeclared c room, and must be rejected.
  bad=copy.deepcopy(routes);bad[0]['points']=[[2,1],[3,1],[4,1],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0]]
  bad[0]['from_port']={'cell':[2,1],'outside':[3,1],'type':'grounded'};bad[0]['to_port']={'cell':[10,0],'outside':[9,0],'type':'grounded'}
  self.assertIn('undeclared_room_contact',m.validate_layout(g,{'ok':True,'rooms':rooms,'corridors':bad}))
 def test_port_mismatch_rejected(self):
  result=m.generate('A','0','plains',embedding_attempts=8);broken=copy.deepcopy(result['layout']);broken['corridors'][0]['to_port']['type']='airborne_fast'
  self.assertIn('port_type_mismatch',m.validate_layout(result['exploration_graph'],broken))
 def test_edge_endpoint_binding_rejected(self):
  result=m.generate('A','0','plains',embedding_attempts=8);broken=copy.deepcopy(result['layout'])
  broken['corridors'][0]['edges'],broken['corridors'][1]['edges']=broken['corridors'][1]['edges'],broken['corridors'][0]['edges']
  self.assertIn('edge_endpoint_mismatch',m.validate_layout(result['exploration_graph'],broken))
 def test_port_direction_drift_rejected(self):
  result=m.generate('A','0','plains',embedding_attempts=8);broken=copy.deepcopy(result['layout']);port=broken['corridors'][0]['from_port'];port['direction']=[-port['direction'][0],-port['direction'][1]]
  self.assertIn('port_direction_mismatch',m.validate_layout(result['exploration_graph'],broken))
 def test_impossible_catalog_fails_bounded(self):
  catalog={'version':1,'kind':'synthetic_fixed_catalog','provenance':{},'templates':[]}
  result=m.generate('A','0','plains',catalog,embedding_attempts=2)
  self.assertFalse(result['layout']['ok']);self.assertIn('embedding_budget_exhausted',result['failures']);self.assertEqual(len(result['layout']['attempt_failures']),2)
 def test_mutation_and_random_equal_eval_budget(self):
  base=m.mission('2','forest');a,pa=m.evolve_c(base,'2',8,True);b,pb=m.evolve_c(base,'2',8,False)
  self.assertEqual(pa['evaluations'],pb['evaluations']);self.assertEqual(len(pa['history']),8);self.assertTrue(pa['archive']);self.assertNotEqual(pa['method'],pb['method'])

if __name__=='__main__':unittest.main()
