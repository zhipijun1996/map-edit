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
class LongerDecisions(unittest.TestCase):
 def test_sustained_control_reversal_not_braking_jitter(self):
  frames=[dict(frame=i,grounded=True,shot_charges=1,accepted=[],axis=1 if i<5 else -1,real_velocity=[260 if i<5 else -260,0])for i in range(10)]
  self.assertEqual(observed({},dict(frames=frames))['reversals'],1)
  for f in frames:f['axis']=0
  self.assertEqual(observed({},dict(frames=frames))['reversals'],0)
 def test_gear_crossing_is_measured_not_named(self):
  frames=[dict(frame=i,grounded=True,shot_charges=1,accepted=[],x=x,y=100)for i,x in enumerate((0,10,20))]
  case=dict(saws=[dict(origin=[15,100],travel=[0,20],radius=8)])
  self.assertEqual(observed(case,dict(frames=frames))['gear_crossings'],1)
  for f in frames:f['y']=1000
  self.assertEqual(observed(case,dict(frames=frames))['gear_crossings'],0)
 def test_arrival_does_not_replace_long_chain_contract(self):
  r=Decisions().fixture();c=dict(challenge_requirements=dict(min_ground_jumps=2,min_landings=2,min_gear_crossings=1))
  result=purpose(c,r);self.assertFalse(result['ok']);self.assertIn('missing_min_ground_jumps',result['reasons']);self.assertIn('missing_min_landings',result['reasons'])
 def test_each_shot_counterfactual_keeps_its_wait_and_targets_the_same_jump(self):
  from prototype.plains.produce import alternative_cases
  c=proposals()[0];original=next(p for p in c['control_plan']if p['op']=='shoot');alts=dict(alternative_cases(c));skip=alts['omit_shot_0'];replacement=skip['control_plan'][-1];self.assertEqual(replacement['op'],'wait');self.assertEqual(replacement['trigger'],original['trigger']);self.assertNotIn('direction',replacement)
 def test_wrong_aim_and_no_enemy_do_not_keep_reactive_target_correction(self):
  from prototype.plains.produce import alternative_cases
  c=proposals()[0];c['enemies']=[dict(id='enemy')];c['latches']=[dict(id='bell')];c['control_plan'][-1]['aim_cell']=dict(kind='enemy',id='enemy');alts=dict(alternative_cases(c));self.assertTrue(all('aim_cell'not in p for p in alts['wrong_aim']['control_plan']));self.assertTrue(all('aim_cell'not in p for p in alts['no_enemy_same_shots']['control_plan']))
 def test_phrase_probe_uses_only_plains_capabilities(self):
  from prototype.plains.phrases import extend_probe
  base=proposals()[0];base['platforms'].append([300,258,192,72]);base['exit_port']=[430,240]
  for sign in (-1,1):
   c=extend_probe(base,sign,6,12,0);self.assertEqual(c['capabilities'],CAPS);self.assertEqual(sum(x['op']=='jump'for x in c['control_plan']),2)

if __name__=='__main__':unittest.main()
