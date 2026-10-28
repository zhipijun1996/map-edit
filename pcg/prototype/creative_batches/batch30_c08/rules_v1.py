"""C08 original charger-space exchange and an explicit staged alternative."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
from .mechanism_probe_v2 import DEPENDENCIES
HERE=Path(__file__).parent
RECIPES=('charger-space-exchange',)
RUNNER_SCRIPT=HERE/'runner_v2.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=DEPENDENCIES+[HERE/'mechanism_probe_v2.py',HERE/'engagement_probe_v1.py',HERE/'engagement-protocol-v1.json',HERE/'main-solve-protocol-v1.json',HERE/'runner_v2.gd',HERE.parent/'enemy_world/runner_v2.gd']
DELAYS=[5,2,8,11]

def attack_wait():return dict(op='wait',trigger=dict(state='grounded',enemy_state=dict(id='borrowed-charger',state='attack'),timeout=240))
def materialize(interface=0,route='air',control=0):
 c=base('c08');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];old=[200,420]
 if interface==0:
  c['platforms']=[[-180,438,520,100],[350,300,100,40],[500,100,260,100],[-200,850,1200,40],[420,190,80,50]]
  enemy=[80,420];a=[480,-200,20,1050];b=[100,-200,20,638];target=[650,82];launch=200;hold=16
 else:
  c['platforms']=[[180,438,160,12],[260,300,100,40],[380,100,240,100],[-200,850,1200,40],[-180,488,520,100]]
  enemy=[60,470];a=[360,-200,20,1050];b=[80,-200,20,688];target=[500,82];launch=192;hold=12
 c['spawn']=old;c['entry_port']=old;c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8]
 c['latches']=[dict(id='release',bell=[150,400],gate=a,paired_gate=b,initial_open='A',open_seconds=0)]
 c['enemies']=[dict(id='borrowed-charger',definition='plains_charger',position=enemy,initial_idle_cooldown=.2)]
 c['reward_sites']=[];reward(c,*target,12)
 if route=='air':
  c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='release')),settle(launch),attack_wait(),cmd('wait',DELAYS[control])]
  if interface==0:c['control_plan'] += [settle(1000),cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='enemy',id='borrowed-charger'))]
  else:c['control_plan'] += [cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='enemy',id='borrowed-charger')),settle(1000)]
  c['control_plan'] += [cmd('shoot',18,aim_cell=dict(kind='bell',id='release')),settle(target[0]),ground(),cmd('wait',10)]
 else:
  if interface==0:p=[cmd('axis',value=1),wait_x(325),cmd('jump'),cmd('jump_release',20),settle(400),ground(),cmd('wait',12),settle(400),cmd('jump'),cmd('jump_release',20)]
  else:p=[settle(230),cmd('wait',16),ground(),cmd('jump'),cmd('wait',12),settle(310),cmd('jump_release',8),ground(),cmd('wait',12),settle(310),cmd('jump'),cmd('jump_release',20)]
  c['control_plan']=p+[cmd('shoot',direction=[-.7,math.sqrt(.51)]),settle(target[0]),ground(),cmd('wait',10)]
 c['ports']=[dict(id='A',position=old,normal=[-1,0],support_index=0),dict(id='B',position=target,normal=[1,0],support_index=2)]
 c['route_spec']=dict(id='borrowed-air'if route=='air'else'grounded-stages',from_port='A',to_port='B',role='main',via_ports=[],require_bell=route=='air')
 c['id']=f'b30-c08-v1-i{interface}-{route}-c{control}';c['interface']=interface;c['max_frames']=1600;c['trace_all']=False;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12;c['required_rewards']=['visible-cache'];c['idea_ids']=['B30-C08'];c['native_scene']='res://prototype/creative_batches/batch30_c08/main_v1.tscn'
 c['layout_title']='放出借火，再关回通路 / '+('同层追赶庭'if interface==0 else'下槽与上唇')
 c['rule_parameters']=dict(interface=interface,route=route,control=control,jump_after_attack=DELAYS[control],jump_hold=hold,launch=launch,core='original cage opens actual charger reach; finite air hit refunds next shot, which re-closes fence and opens onward gate',strategy_variants=['borrowed_air','grounded_stages'])
 c['generation_rule']=dict(id='batch30/C08',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','enemies','reward_sites']})
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C08/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core=c['rule_parameters']['core'],declared_strategies=['borrowed_air','grounded_stages'],enemy_is_not_a_key=True),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id='borrowed-air'),dict(from_port='A',to_port='B',role='main',route_id='grounded-stages')],space=dict(max_width=1800 if interface==0 else 1450,max_height=1100 if interface==0 else 1450,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original supported A; same original live caged3HP charger, Aopen/Bclosed',exit='observed stable B and actual persistent charger/gates; arbitrary statesUNKNOWN'),return_conditions='Staged strategy supplies no-hit route; actual dead-enemy and misrelease continuity require separate fixtures, generic reverse/seamsUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C08 exact demand')
 return[materialize(interface,'air',0),materialize(interface,'staged',0)]

def purpose(c,r):
 why=[];fs=r.get('frames',[]);pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0];swaps=[e for e in pair.get('events',[])if e.get('type')=='pair_switch']
 hits=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='enemy_hit'and e.get('fired_airborne')and e.get('player_airborne')]
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];airshots=[f for f in shots if not f.get('grounded')]
 stages=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform1']
 B=c['latches'][0]['paired_gate'];released_positions=[dict(frame=f['frame'],x=f['plains']['enemies'][0]['x'],state=f['plains']['enemies'][0]['state'])for f in fs if f.get('plains',{}).get('enemies')and f['plains']['enemies'][0]['x']-14>B[0]+B[2]+6]
 actual_refills=[]
 for hit in hits:
  for f in fs:
   if hit['frame']<=f['frame']<=hit['frame']+2 and not f.get('grounded')and f.get('shot_charges',0)>0:actual_refills.append(dict(frame=f['frame'],shot_charges=f['shot_charges'],energy=f.get('energy')))
 borrowed=bool(len(swaps)>=2 and swaps[0]['open']=='B'and any(e['open']=='A'and e.get('airborne')for e in swaps[1:])and hits and actual_refills and released_positions and len(airshots)>=2 and not stages)
 staged=bool(len(stages)>=4 and r.get('jumps',0)>=2)
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('required_reward_not_claimed')
 intended=c['rule_parameters']['route'];counter=bool(c.get('counterexample_kind'))
 if counter:
  if not(borrowed or staged):why.append('neither_actual_declared_strategy_completed')
 elif intended=='air'and not borrowed:why.append('canonical_borrowed_air_not_demonstrated')
 elif intended=='staged'and not staged:why.append('canonical_staged_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=dict(requested_strategy=intended,actual_borrowed_air=borrowed,actual_grounded_stages=staged,counter_may_use_other_explicitly_declared_strategy=counter,actual_charger_outside_fence=released_positions[::10],air_enemy_hits=len(hits),enemy_hit_events=hits,real_air_refills=actual_refills,staged_supports=sorted({f['support_id']for f in stages}),staged_grounded_frames=len(stages),actual_swaps=swaps,final_enemy=r.get('plains',{}).get('enemies')),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))

def alternatives(c):
 out=[];source=copy.deepcopy(c['control_plan']);target=c['exit_port'][0]
 def add(label,p):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=p;out.append(v)
 for index,q in enumerate(source):
  if q['op']=='shoot':
   p=copy.deepcopy(source);p[index]=cmd('wait',q['trigger']['after']);add('omit-shot-'+str(index),p)
 for hold in [8,16,24,28]:
  for dy in [.15,.7,.99]:
   add(f'direct-no-release-{hold}-{dy}',[cmd('axis',value=1),wait_x(325),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(target),ground(),cmd('wait',10)])
 for delay in [0,3,8,15]:
  if c['rule_parameters']['route']=='air':
   p=copy.deepcopy(source);p[3]=cmd('wait',delay);add('different-attack-response-'+str(delay),p)
  else:
   p=copy.deepcopy(source);idx=next(i for i,q in enumerate(p)if q['op']=='shoot');p[idx]['trigger']['after']=delay;add('different-staged-shot-'+str(delay),p)
 other=materialize(c['interface'],'staged'if c['rule_parameters']['route']=='air'else'air',0);add('other-declared-strategy',copy.deepcopy(other['control_plan']))
 return out
