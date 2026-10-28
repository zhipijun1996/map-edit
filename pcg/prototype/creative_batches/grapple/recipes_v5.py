import copy,json,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,reward,finish,wait_x
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
RUNNER=Path(__file__).with_name('runner_v3.gd')
RECIPES=['jump-refill','bounce-brake','hang-recast']
def gate(op,state,n=0,timeout=160,**kw):return dict(op=op,trigger=dict(state=state,min_after=n,timeout=timeout),**kw)
def candidates(recipe,interface=0):
 out=[]
 for delay in ([0,2,4,6]if recipe in ['bounce-brake','jump-refill']else [8,12,16,20]):
  c=base(f'grapple-{recipe}-v5-{delay}');c['family']='grapple-'+recipe;c['production_recipe']=recipe;c['capabilities']=['move','jump','grapple'];c['hooks']=[dict(x=210,y=-80 if recipe=='jump-refill'else 70 if recipe=='bounce-brake'else 130 if recipe=='hang-recast'else 230,kind='bounce'if recipe=='bounce-brake'else'hang')]
  c['platforms']=[[-160,438,400,100],[-800,950,2200,60]]
  plan=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',8)]
  if recipe=='jump-refill':c['capabilities'].append('double_jump');plan[-1]=cmd('jump_release',24);plan += [cmd('jump',0),cmd('jump_release',24)]
  plan += [cmd('grapple',delay,aim_target=[210,c['hooks'][0]['y']])]
  if recipe=='bounce-brake':
   plan[2]=cmd('jump_release',24);c['capabilities'].append('shot_recoil');plan += [gate('wait','free',25),cmd('shoot',direction=[-.8,.6])];x,y,width=470,40,180
  elif recipe=='hang-recast':
   c['hooks'].append(dict(x=80,y=-20,kind='hang'));plan += [gate('wait','hook_hang',3),cmd('axis',value=-1),cmd('grapple',6,aim_target=[80,-20]),gate('wait','hook_hang',8),gate('jump','hook_hang',3),cmd('jump_release',12)];x,y,width=-70,90,180;c['exit_normal']=[-1,0]
  else:
   plan += [gate('wait','hook_hang',1)]
   if recipe=='hang-phase':
    c['saws']=[dict(source_id='departure-saw',origin=[285,190],travel=[0,140],radius=18,period=3.,initial_phase=.15)]
    plan += [cmd('axis',value=0),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='departure-saw',window=[.05,.10]),min_after=6,timeout=240))]
   plan += [cmd('axis',value=1),gate('jump','hook_hang',3),cmd('jump_release',12)]
   if recipe=='jump-refill':plan += [cmd('jump',20),cmd('jump_release',12)];x,y,width=450,-30,180
   else:x,y,width=(350 if recipe=='hang-phase'else 320),230,180
  c['platforms'].append([x-width/2,y+18,width,80]);c['one_way_platform_indices']=[len(c['platforms'])-1]
  reward(c,x,y,12);c=finish(c,x,y,plan+[settle(x,5)]);c['max_frames']=650
  c['rule_parameters']=dict(relationship=recipe,interface=interface,delay=delay,contact_restores='double_jump and grapple only; never airShots')
  c['generation_rule']=dict(id='creative/grapple/'+recipe,version=1,parameters=c['rule_parameters'],source_type='llm_subagent_proposal',source_task='/root/grapple_creator');out.append(c)
 return out

def spec(recipe):
 c=candidates(recipe)[0]
 return dict(schema='map-notes/challenge-specification/v5',id='creative/grapple/'+recipe+'/v5/0',region='plains',required_family=c['family'],objective=dict(recipe=recipe,interface=0),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],c.get('exit_normal',[1,0])]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=420-c['exit_port'][1],space=dict(max_width=2200,max_height=1400,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(req):
 recipe=req['recipe']
 if recipe not in RECIPES:return dict(status='needs_design',gaps=['unregistered'],cases=[])
 s=spec(recipe);cs=candidates(recipe)
 for c in cs:c['map_specification']=s;c['idea_ids']=['grapple/'+recipe+'-v5']
 return dict(status='requires_physics',specifications=[s],cases=cs)
def purpose(c,r):
 fs=r.get('frames',[]);reasons=[];causal={};recipe=c['production_recipe']
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if r.get('workshop',{}).get('coins',0)<12:reasons.append('reward_not_claimed')
 contacts=[i for i,f in enumerate(fs)if f['traversal_state'] in ['hook_hang','hook_contact_kick']]
 hang=[f for f in fs if f['traversal_state']=='hook_hang'];anchors=[f for f in fs if any(e['type']=='anchor_jump'for e in f.get('accepted',[]))]
 if not r.get('hook_contacts',0):reasons.append('no_actual_hook_contact')
 if recipe in ['anchor-gap','hang-phase','jump-refill']and not anchors:reasons.append('no_active_anchor_departure')
 if recipe=='hang-phase':
  actual_wait=any(abs(f['axis'])<.01 and abs(f['vx'])+abs(f['vy'])<2 for f in hang)
  phase=anchors[0].get('saws',[{}])[0].get('phase')if anchors else None
  causal.update(hang_frames=len(hang),neutral_hang=actual_wait,departure_phase=phase)
  if not actual_wait:reasons.append('no_safe_air_observation')
 if recipe=='hang-recast':
  causal['contacts']=r.get('hook_contacts',0)
  if r.get('hook_contacts',0)<2:reasons.append('no_actual_target_reselection')
 if recipe=='jump-refill':
  air=[i for i,f in enumerate(fs)if any(e['type']=='air_jump'for e in f.get('accepted',[]))]
  restored=any(a['jumps_used']>=2 and b['jumps_used']==1 and not b['grounded'] for a,b in zip(fs,fs[1:]))
  causal.update(air_jump_frames=air,contact_restored_air_jump=restored)
  if not contacts or not any(i<contacts[0]for i in air)or not any(i>contacts[-1]for i in air)or not restored:reasons.append('no_spent_contact_restored_jump_chain')
 if recipe=='bounce-brake':
  shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
  causal['automatic_contact_kick']=bool(contacts)
  if not contacts or not shots or shots[0]['frame']<=contacts[0]:reasons.append('no_post_automatic_launch_recoil')
 # Contact must never replenish original ammunition, including non-shot recipes.
 increases=[b['frame']for a,b in zip(fs,fs[1:])if b['shot_charges']>a['shot_charges']and not b['grounded']]
 causal['air_shot_charge_increases']=increases
 if increases:reasons.append('unexpected_air_ammo_restore')
 return dict(ok=not reasons,reasons=reasons,causal=causal)
def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 x=c['exit_port'][0]
 for hold in [4,12,24]:
  for start in [80,180,230]:
   add(f'ordinary-{hold}-{start}',[cmd('axis',value=1),wait_x(start),cmd('jump'),cmd('jump_release',hold),settle(x,4)])
   if 'double_jump'in c['capabilities']:add(f'direct-double-{hold}-{start}',[cmd('axis',value=1),wait_x(start),cmd('jump'),cmd('jump_release',hold),cmd('jump',8),cmd('jump_release',hold),settle(x,4)])
   else:add(f'direct-shot-{hold}-{start}',[cmd('axis',value=1),wait_x(start),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-.6,.8]),settle(x,4)])
 for index,s in enumerate(c['control_plan']):
  if s['op']in ['jump','grapple','shoot']:
   p=copy.deepcopy(c['control_plan']);p[index]=dict(op='wait',trigger=copy.deepcopy(s['trigger']));add('omit-'+str(index),p)
 if c['production_recipe']=='hang-phase':
  p=[s for s in copy.deepcopy(c['control_plan'])if not s.get('trigger',{}).get('dynamic')];add('no-phase-wait',p)
 if c['production_recipe']=='jump-refill':
  for hold in [12,24,36,48]:
   for after in [0,4,8]:
    add(f'single-before-hook-{hold}-{after}',[cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('grapple',after,aim_target=[210,-80]),gate('jump','hook_hang',3),cmd('jump_release',12),cmd('jump',20),cmd('jump_release',12),settle(x,5)])
 if c['production_recipe']=='bounce-brake':
  for hold in [8,16,24,36]:
   for start in [80,180,230]:
    for dy in [0,.2,.4,.6,.8,1.]:
     add(f'extended-direct-{hold}-{start}-{dy}',[cmd('axis',value=1),wait_x(start),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(x,4)])
 if c['production_recipe']=='hang-recast':
  p=c['control_plan'][:5]+[cmd('axis',value=-1),gate('jump','hook_hang',3),cmd('jump_release',24),settle(x,6)];add('first-ring-only',p)
  for hold in [12,24,36]:
   add('direct-second-ring-'+str(hold),[cmd('axis',value=0),cmd('jump'),cmd('jump_release',hold),cmd('grapple',2,aim_target=[80,-20]),gate('jump','hook_hang',3),cmd('axis',value=-1),cmd('jump_release',24),settle(x,5)])
 return out
if __name__=='__main__':
 run('workshop-creative-grapple-production-v5',requests=[dict(recipe=r)for r in RECIPES],cycles=4,library_root=ROOT/'results/workshop-creative-grapple-library-v5',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[RUNNER],runner_script=RUNNER.resolve())
