import copy,unittest
from prototype.plains.synthesis import proposals,identity,CAPS
from prototype.plains.evaluation import observed,purpose,instantiate

class Decisions(unittest.TestCase):
 def fixture(self):
  frames=[dict(frame=i,grounded=False,shot_charges=n,accepted=[])for i,n in enumerate((1,0,1,0))]
  frames[0]['accepted']=[dict(type='ground_jump')];frames[1]['accepted']=[dict(type='shot',direction=[0,1])];frames[3]['accepted']=[dict(type='shot',direction=[-1,0])]
  return dict(ok=True,hp=5,shots=2,frames=frames,plains=dict(events=[dict(type='enemy_hit',frame=2,id='enemy',fired_airborne=True,player_airborne=True)],player_damage=[]))
 def test_exact_plains_scope_and_unique_budget(self):
  ps=proposals();self.assertEqual(len(ps),36);self.assertEqual(len({identity(c)for c in ps}),36)
  for c in ps:self.assertEqual(c['capabilities'],['move','jump','shot_recoil']);self.assertFalse(c['hooks'])
 def test_labels_do_not_create_novelty(self):
  a=proposals()[0];b=copy.deepcopy(a);b.update(id='anything',family='new_name',title='new');self.assertEqual(identity(a),identity(b))
 def test_cells_change_identity(self):
  a=proposals()[0]
  for field in ('enemies','latches'):
   b=copy.deepcopy(a);b[field]=[dict(id='added')];self.assertNotEqual(identity(a),identity(b))
 def test_refund_requires_real_air_hit_and_charge_gain(self):
  r=self.fixture();self.assertEqual(observed({},r)['refunds'],1);self.assertTrue(observed({},r)['continuous_two_air_shots'])
  r['plains']['events']=[];self.assertEqual(observed({},r)['refunds'],0)
 def test_ground_reset_is_not_air_hit_refund(self):
  r=self.fixture();r['frames'][2]['grounded']=True;b=observed({},r);self.assertEqual(b['refunds'],0);self.assertFalse(b['continuous_two_air_shots'])
 def test_tagged_bell_cannot_replace_actual_open(self):
  r=self.fixture();c=dict(latches=[dict(id='bell')]);self.assertIn('required_bell_not_opened',purpose(c,r)['reasons']);r['plains']['events'].append(dict(type='bell_open',frame=2,id='bell'));self.assertTrue(purpose(c,r)['ok'])
 def test_enemy_damage_is_not_player_damage(self):
  r=self.fixture();r['plains']['events'].append(dict(type='damage',frame=2,target='enemy',amount=1));self.assertTrue(purpose(dict(enemies=[dict(id='enemy')]),r)['ok']);r['plains']['player_damage']=[dict(target='player',amount=1)];self.assertFalse(purpose({},r)['ok'])
 def test_no_granted_advanced_abilities(self):
  for field in ('air_jumps','grapples','wall_jumps'):
   r=self.fixture();r[field]=1;self.assertIn('forbidden_advanced_ability',purpose({},r)['reasons'])
 def test_common_random_numbers_and_no_mutation(self):
  c=proposals()[0];c['saws']=[dict(initial_phase=0)];c['enemies']=[dict(initial_idle_cooldown=0)];old=copy.deepcopy(c);a=instantiate(c,173,'mild',2);b=instantiate(c,173,'mild',2);self.assertEqual(a,b);self.assertEqual(c,old);self.assertNotEqual(a['saws'],c['saws'])
if __name__=='__main__':unittest.main()
