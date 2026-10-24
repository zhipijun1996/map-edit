import copy,unittest
from prototype.plains.three_port import geometry_hash,port_purpose
class ThreePortEvidence(unittest.TestCase):
 def fixture(self):
  c=dict(ports=[dict(id='A',position=[0,100]),dict(id='B',position=[300,100]),dict(id='C',position=[150,20])],route_spec=dict(require_bell=False,via_ports=['C']),latches=[],saws=[])
  frames=[dict(frame=i,x=x,y=y,grounded=ground,shot_charges=1,accepted=[])for i,(x,y,ground)in enumerate([(0,100,True),(150,20,False),(300,100,True)])]
  return c,dict(ok=True,hp=5,shots=0,frames=frames,plains=dict(events=[],player_damage=[]))
 def test_merely_reaching_B_is_not_completing_the_high_branch(self):
  c,r=self.fixture();p=port_purpose(c,r);self.assertFalse(p['ok']);self.assertIn('missing_actual_via_port_C',p['reasons'])
  r['frames'][1]['grounded']=True;self.assertTrue(port_purpose(c,r)['ok'])
 def test_main_route_may_intentionally_require_no_shots(self):
  c,r=self.fixture();c['route_spec']['via_ports']=[];self.assertTrue(port_purpose(c,r)['ok'])
 def test_geometry_identity_ignores_route_program_but_not_cells_or_phase(self):
  c,_=self.fixture();d=copy.deepcopy(c);d.update(spawn=[300,100],goal=[0,80,40,40],control_plan=[dict(op='jump')]);self.assertEqual(geometry_hash(c),geometry_hash(d))
  d['saws']=[dict(initial_phase=.25)];self.assertNotEqual(geometry_hash(c),geometry_hash(d))
 def test_synthetic_via_tags_cannot_replace_observed_grounded_visit(self):
  c,r=self.fixture();r['visited_ports']=['C'];self.assertFalse(port_purpose(c,r)['ok'])
if __name__=='__main__':unittest.main()
