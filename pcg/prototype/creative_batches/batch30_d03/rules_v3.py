"""Finite shared enemy health: immediate air routes versus staged landing routes.

All programs share real Cells, reward transactions and enemy state. No damage,
resource or actor-position writes. Recipes are bounded, not an online creator.
"""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('finite-enemy-routes',)
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json']
CAPS=['move','jump','shot_recoil']

def stop_ground():return [cmd('axis',value=0),ground(),cmd('wait',6)]
def leg(takeoff,sign,land,hold=12,delay=6):
 return [cmd('axis',value=sign),wait_x(takeoff,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,direction=[-sign*.5,math.sqrt(.75)]),wait_x(land-5*sign,sign),*stop_ground()]
def mirror_point(x):return 160-x

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('unsupported exact finite enemy interface')
 dx=interface*35;front=380+dx;top=-20-interface*15;bx=front+100;cx=mirror_point(bx)-120;stage1=370+dx;stage2=650+dx
 c=base('b30-finite-enemy');c['family']='finite-enemy-routes';c['capabilities']=CAPS[:]
 c['platforms']=[[-160,438,400,100],[front,top,220,70],[mirror_point(front+220)-120,top,220,70],[-850,680,2100,80],[stage1,290,180,50],[stage2,130,170,50],[mirror_point(stage1+180),290,180,50],[mirror_point(stage2+170),130,170,50]]
 c['enemies']=[dict(id='shared-sentry',definition='plains_sentry',position=[125,422],initial_idle_cooldown=.6)]
 c['ports']=[dict(id='A',position=[80,420],support_index=0,normal=[0,-1]),dict(id='B',position=[bx,top-18],support_index=1,normal=[1,0]),dict(id='C',position=[cx,top-18],support_index=2,normal=[-1,0]),dict(id='D',position=[1040,662],support_index=3,normal=[1,0])]
 c['reward_sites']=[dict(id='east-cache',position=[bx,top-18],region=[bx-35,top-24,70,12],amount=12),dict(id='west-cache',position=[cx,top-18],region=[cx-35,top-24,70,12],amount=12)]
 c['world_bounds']=[-1200,-800,3200,2300]
 def air(sign):
  target=bx if sign==1 else cx
  return [cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=sign),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='shared-sentry')),cmd('shoot',18,aim_cell=dict(kind='enemy',id='shared-sentry')),cmd('shoot',18,direction=[0,1]),settle(target,6)]
 def stages(sign):
  transform=(lambda x:x)if sign==1 else mirror_point
  first=([cmd('axis',value=1),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[0,1]),wait_x(stage1+85),*stop_ground()]if sign==1 else leg(transform(220),sign,transform(stage1+90)))
  target=bx if sign==1 else cx
  return first+leg(transform(stage1+145),sign,transform(stage2+(85 if sign==1 else 140)))+leg(transform(stage2+(30 if sign==1 else 130)),-sign,target,16,6)
 # Real arrival at B without installing a persistent settle controller.
 b_visit=air(1)[:-1]+[wait_x(bx-8),*stop_ground()]
 # Descend west of B, reach a safe ground firing point, then eliminate the
 # remaining one HP. This is a deliberate clear-for-safety option, not refill.
 return_and_clear=[cmd('axis',value=-1),wait_x(300,-1),cmd('shoot',aim_cell=dict(kind='enemy',id='shared-sentry')),wait_x(10,-1),*stop_ground()]
 west_visit=stages(-1)[:-4]+[]
 plans=[('east-air','A','B','reward',air(1),[],['east-cache'],'two_air_hits'),('west-air','A','C','reward',air(-1),[],['west-cache'],'two_air_hits'),('east-staged','A','B','reward',stages(1)+[settle(bx,6)],[],['east-cache'],'ground_refill'),('west-staged','A','C','reward',stages(-1)+[settle(cx,6)],[],['west-cache'],'ground_refill'),('main','A','D','main',[cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),settle(1040,6)],[],[],'safe_exit'),('east-then-dead-west','A','C','recovery',b_visit+return_and_clear+stages(-1)+[settle(cx,6)],['B'],['east-cache','west-cache'],'persistent_death'),('both-rewards-exit','A','D','recovery',b_visit+return_and_clear+stages(-1)+[cmd('axis',value=1),settle(1040,6)],['B','C'],['east-cache','west-cache'],'persistent_death')]
 physical={k:c.get(k,[])for k in ['platforms','ports','enemies','reward_sites','world_bounds','capabilities','hazards','thorns','saws','moving_platforms','hooks','latches','one_way_platform_indices']};uid=digest(physical);out=[]
 for rid,frm,to,role,plan,via,rewards,kind in plans:
  v=copy.deepcopy(c);start=next(p for p in c['ports']if p['id']==frm);end=next(p for p in c['ports']if p['id']==to)
  v.update(id=f'b30-d03-v3-i{interface}-{rid}',spawn=start['position'],entry_port=start['position'],exit_port=end['position'],goal=[end['position'][0]-25,end['position'][1]-4,50,8],control_plan=copy.deepcopy(plan),max_frames=2400,trace_all=False,interface=interface,production_recipe=recipe,challenge_route=False,expected_reward=12*len(rewards),layout_uid=uid,layout_title=f'借火留给哪一岸 / 4口 / 接口{interface+1}')
  v['route_spec']=dict(id=rid,from_port=frm,to_port=to,role=role,via_ports=via,require_bell=False)
  v['required_rewards']=rewards;v['purpose_kind']=kind;v['idea_ids']=['PR-D03'];v['rule_parameters']=dict(interface=interface,right_high_front=front,high_surface=top,enemy_health='original 3HP, shared persistent actor',stage_support_indices=[4,5,6,7],core='air route spends finite hits; staged route needs ground landings and works after enemy death')
  v['generation_rule']=dict(id='batch30/finite-enemy-routes',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=v['rule_parameters']);out.append(v)
 spec=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/D03/{interface}/v3',region='plains',source_type='model_authored_challenge_spec',required_family=c['family'],objective=dict(recipe=recipe,interface=interface,physical_layout_sha256=uid,junction_role='resource_choice',ports=c['ports']),capabilities=dict(version=1,status='defined',allOf=CAPS,anyOfGroups=[]),ports=dict(count=4,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=v['route_spec']['from_port'],to_port=v['route_spec']['to_port'],route_id=v['route_spec']['id'],role=v['route_spec']['role'])for v in out],space=dict(max_width=2600,max_height=1800,max_port_span_x=2000),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='real original supported actor; same 3HP enemy',exit='observed stable only; enemy death persists'),return_conditions='Continuous B visit and dead-enemy C completion explicitly requested; arbitrary returns UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))
 for v in out:v['map_specification']=spec
 return out

def purpose(c,r):
 fs=r.get('frames',[]);reasons=[]
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
 if r.get('returns'):reasons.append('world_reset')
 events=r.get('plains',{}).get('events',[]);hits=[e for e in events if e['type']=='enemy_hit'and e['id']=='shared-sentry'];airhits=[e for e in hits if e.get('player_airborne')and e.get('fired_airborne')];ground_stages=[f for f in fs if f.get('grounded')and f.get('support_id')in ['Platform4','Platform5','Platform6','Platform7']]
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 if not set(c.get('required_rewards',[]))<=claimed:reasons.append('required_reward_not_claimed')
 for pid in c['route_spec'].get('via_ports',[]):
  xy=next(p['position']for p in c['ports']if p['id']==pid)
  if not any(f.get('grounded')and abs(f['x']-xy[0])<=30 and abs(f['y']-xy[1])<1 for f in fs):reasons.append('missing_actual_via/'+pid)
 kind=c.get('purpose_kind');dead=any(e.get('dead')for e in r.get('plains',{}).get('enemies',[]))
 if kind=='two_air_hits'and len(airhits)<2:reasons.append('finite_two_hit_air_route_not_demonstrated')
 if kind=='ground_refill'and len({f['support_id']for f in ground_stages})<2:reasons.append('staged_ground_landings_missing')
 if kind=='persistent_death':
  death=next((e['frame']for e in events if e['type']=='enemy_defeated'),None)
  if not(dead and death is not None and any(f['frame']>death for f in ground_stages)):reasons.append('dead_enemy_alternative_not_demonstrated')
 return dict(ok=not reasons,reasons=reasons,causal=dict(air_enemy_hits=len(airhits),enemy_dead=dead,staged_supports=sorted({f['support_id']for f in ground_stages}),claimed_rewards=sorted(claimed)),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))

def alternatives(c):
 out=[]
 for sign in [-1,1]:
  for hold in [0,8,16,24]:
   for delay in [0,12,24]:
    v=copy.deepcopy(c);label=f'direct-{sign}-{hold}-{delay}';v['id']+='-counter-'+label;v['counterexample_kind']=label
    v['control_plan']=[cmd('axis',value=sign)]
    if hold:v['control_plan'] += [cmd('jump',delay),cmd('jump_release',hold),cmd('shoot',6,direction=[0,1])]
    else:v['control_plan'] += [cmd('wait',delay)]
    v['control_plan'] += [settle(c['exit_port'][0])];out.append(v)
 for index,op in enumerate(c['control_plan']):
  if op['op']!='shoot':continue
  v=copy.deepcopy(c);label='omit-shot-'+str(index);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan'][index]=dict(op='wait',trigger=copy.deepcopy(op['trigger']));out.append(v)
 return out
