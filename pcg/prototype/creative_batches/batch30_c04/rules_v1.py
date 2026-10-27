"""C04: old cover opens a passage as another cover closes by the receiver."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
from .mechanism_probe_v1 import DEPENDENCIES
HERE=Path(__file__).parent
RECIPES=('cover-relocation-recoil',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=DEPENDENCIES+[HERE/'mechanism_probe_v1.py']
CONTROLS=[(12,0),(12,6),(20,0),(20,6)]

def materialize(interface=0,control=0):
 c=base('c04');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 if interface==0:
  old=[80,420];new=[390,482];sign=1;depart=135;bell=[140,400];enemy=[255,422]
  c['platforms']=[[-160,438,330,100],[330,500,260,100],[220,438,70,40],[-450,780,1500,40]]
  gate=[170,0,20,780];paired=[300,350,20,200]
 else:
  old=[440,482];new=[130,420];sign=-1;depart=385;bell=[380,460];enemy=[265,484]
  c['platforms']=[[350,500,250,100],[40,438,140,100],[230,500,70,40],[-450,840,1500,40]]
  gate=[330,0,20,840];paired=[200,410,20,200]
 hold,delay=CONTROLS[control]
 c['spawn']=old;c['entry_port']=old;c['exit_port']=new;c['goal']=[new[0]-25,new[1]-4,50,8]
 c['latches']=[dict(id='relay',bell=bell,gate=gate,paired_gate=paired,initial_open='B',open_seconds=0)]
 c['enemies']=[dict(id='relay-sentry',definition='plains_sentry',position=enemy,initial_idle_cooldown=.2)]
 c['reward_sites']=[];reward(c,*new,12)
 c['control_plan']=[cmd('wait',18),cmd('axis',value=sign),wait_x(depart,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,aim_cell=dict(kind='bell',id='relay')),settle(new[0],6),ground(),cmd('wait',30)]
 c['ports']=[dict(id='A',position=old,normal=[-sign,0],support_index=0),dict(id='B',position=new,normal=[sign,0],support_index=1)]
 c['route_spec']=dict(id='old-cover-to-new-cover',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True)
 c['id']=f'b30-c04-v1-i{interface}-c{control}';c['interface']=interface;c['max_frames']=1400;c['trace_all']=False;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12;c['required_rewards']=['visible-cache'];c['idea_ids']=['B30-C04'];c['native_scene']='res://prototype/creative_batches/batch30_c04/main_v1.tscn'
 c['layout_title']='旧掩体开路，新掩体接应 / '+('右下凹岸'if interface==0 else'反向抬高岸')
 c['rule_parameters']=dict(interface=interface,control=control,hold=hold,shot_after_release=delay,direction=sign,departure=depart,old=old,new=new,core='A is actual old cover and passage obstacle; original air shot opens A/closes B and recoils over B into a different protected receiver',enemy_activation_range=180)
 c['generation_rule']=dict(id='batch30/C04',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','enemies','reward_sites']})
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C04/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core=c['rule_parameters']['core']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id=c['route_spec']['id'])],space=dict(max_width=1600 if interface==0 else 1450,max_height=950 if interface==0 else 1250,max_port_span_x=800),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original supported A and fresh resources; Aclosed/Bopen, original live sentry',exit='observed stable B; Aopen/Bclosed and sampled real cover. Generic enemy/entry states UNKNOWN'),return_conditions='lower floor is internal recovery terrain; exact retry/return UNKNOWN until continuous witness',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C04 registered demand')
 return[materialize(interface,0)]

def purpose(c,r):
 why=[];fs=r.get('frames',[]);pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0]
 rays=[(f['frame'],a)for f in fs for a in f.get('workshop',{}).get('cover',{}).get('rays',[])]
 old=[(t,a)for t,a in rays if a.get('ray_hit')=='pair/relay/A'and a['distance']<=a['activation_range']and a.get('enemy_alive')]
 new=[(t,a)for t,a in rays if a.get('ray_hit')=='pair/relay/B'and a['distance']<=a['activation_range']and a.get('enemy_alive')and abs(a['player_position'][0]-c['exit_port'][0])<40 and abs(a['player_position'][1]-c['exit_port'][1])<40]
 exposed=[(t,a)for t,a in rays if a.get('actual_original_can_engage')]
 swaps=[e for e in pair.get('events',[])if e.get('type')=='pair_switch'and e.get('open')=='A']
 first=next((e for e in swaps if e.get('airborne')),None)
 landing=next((f for f in fs if first and f['frame']>first['frame']and f.get('grounded')),None)
 enemies=r.get('plains',{}).get('enemies',[]);dead=bool(enemies and all(e.get('dead')for e in enemies))
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('required_reward_not_claimed')
 if not old:why.append('actual_old_cover_within_enemy_range_missing')
 if not dead and not new:why.append('actual_new_cover_within_enemy_range_missing')
 if dead and r.get('shots',0)<3:why.append('unexplained_enemy_death')
 if not swaps or pair.get('open_a')is not True or pair.get('open_b')is not False:why.append('actual_cover_exchange_missing')
 if r.get('shots',0)==1:
  if not first:why.append('single_shot_air_recoil_transfer_missing')
  if not landing or landing.get('support_id')!='Platform1':why.append('single_shot_first_landing_not_new_receiver')
 elif r.get('shots',0)<2:why.append('no_actual_world_and_movement_action')
 # Extra-shot preplanning/combat can be a paid alternative. It does not prove
 # same-shot transfer necessary; the nominal one-shot programme must show it.
 return dict(ok=not why,reasons=why,causal=dict(old_cover_frames=len(old),new_cover_frames=len(new),actual_exposed_frames=len(exposed),actual_air_cover_swap=first,first_post_swap_landing=({k:landing.get(k)for k in ['frame','x','y','support_id']}if landing else None),all_swaps=swaps,enemy_dead=dead,paid_extra_shot_alternative=r.get('shots',0)>=2),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))

def alternatives(c):
 out=[];source=copy.deepcopy(c['control_plan']);sign=c['rule_parameters']['direction'];target=c['exit_port'][0];depart=c['rule_parameters']['departure']
 def add(label,p):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=p;out.append(v)
 omit=copy.deepcopy(source);omit[5]=cmd('wait',omit[5]['trigger']['after']);add('omit-world-shot',omit)
 for hold in [8,16,24,28]:
  add(f'ordinary-jump-no-switch-{hold}',[cmd('axis',value=sign),wait_x(depart,sign),cmd('jump'),cmd('jump_release',hold),settle(target,6),ground(),cmd('wait',30)])
  for dy in [.15,.7,.99]:
   add(f'no-switch-recoil-{hold}-{dy}',[cmd('axis',value=sign),wait_x(depart,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-sign*math.sqrt(1-dy*dy),dy]),settle(target,6),ground(),cmd('wait',30)])
 for hold in [8,16,24,28]:
  for shift in [0,50]:
   add(f'ground-preopen-single-shot-jump-{hold}-{shift}',[cmd('shoot',aim_cell=dict(kind='bell',id='relay')),cmd('wait',8),cmd('axis',value=sign),wait_x(depart+sign*shift,sign),cmd('jump'),cmd('jump_release',hold),settle(target,6),ground(),cmd('wait',30)])
 for delay in [0,6,12,18]:
  p=copy.deepcopy(source);p[5]['trigger']['after']=delay;add(f'air-window-{delay}',p)
 p=copy.deepcopy(source);p += [cmd('shoot',aim_cell=dict(kind='bell',id='relay')),cmd('wait',140)];add('abandon-new-cover-after-arrival',p)
 return out
