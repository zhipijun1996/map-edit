"""The same original timed gate changes from opening to return landing."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('timed-gate-return-catch',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','observe_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parent/'batch30_blockpilot/rules_v1.py']
TIMERS=[.2,.3,.4,.5]
PAIRS=[('A','B'),('A','C'),('D','B'),('D','C')]

def candidate(entry='A',target='B',timer=.2):
 if(entry,target)not in PAIRS or timer not in TIMERS:raise ValueError('outside registered gate/route domain')
 c=base('N04');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['interface']=0
 c['platforms']=[[0,736,256,64],[1024,736,256,64],[0,352,320,224],[960,352,320,224],[320,352,64,448],[896,352,64,448],[0,864,1280,160]]
 docks={'A':[24,718],'D':[1256,718],'B':[24,334],'C':[1256,334]}
 cells={'A':([0,5],'W'),'D':([9,5],'E'),'B':([0,2],'W'),'C':([9,2],'E')}
 ports={k:block_port(k,cell,edge,docks[k])for k,(cell,edge)in cells.items()}
 c['ports']=[dict(id=k,position=docks[k][:],normal=ports[k]['normal'],support_index=index)for index,k in enumerate(['A','D','B','C'])]
 c['spawn']=docks[entry][:];c['entry_port']=docks[entry][:];c['exit_port']=docks[target][:];c['goal']=[docks[target][0]-25,docks[target][1]-4,50,8]
 c['latches']=[dict(id='return-catch',bell=[640,745],gate=[384,608,512,24],open_seconds=timer)]
 c['reward_sites']=[dict(id='high-'+k,position=docks[k][:],region=[docks[k][0]-30,docks[k][1]-6,60,12],amount=12)for k in ['B','C']]
 incoming=1 if entry=='A'else -1;outgoing=-1 if target=='B'else 1;takeoff=420 if target=='B'else 860
 c['control_plan']=[cmd('axis',value=incoming),wait_x(640,incoming),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='return-catch')),ground(),cmd('wait',6),cmd('axis',value=outgoing),wait_x(takeoff,outgoing),cmd('axis',value=0),ground(),cmd('wait',6),cmd('axis',value=outgoing),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-outgoing*.35,math.sqrt(1-.35**2)]),settle(docks[target][0]),ground(),cmd('wait',10)]
 c['id']=f'b30-block-n04-v1-{entry}-{target}-t{int(timer*100):02}';c['route_spec']=dict(id=entry+'-to-'+target,from_port=entry,to_port=target,role='main',via_ports=[],require_bell=True)
 c['max_frames']=1800;c['trace_all']=False;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12;c['required_rewards']=['high-'+target];c['idea_ids']=['B30-N04'];c['layout_title']='穿过的门，回来接住你';c['native_scene']='res://prototype/creative_batches/batch30_blockn04/main_v1.tscn';c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 c['rule_parameters']=dict(timer=timer,entry=entry,target=target,first_jump_hold=20,exit_jump_hold=20,exit_direction=outgoing)
 projected=declare(dict(case=c,ports=ports,functional_roles=['junction','interchange'],action_clearance=[[0,0,1280,1024]]),[(x,y)for x in range(10)for y in range(8)])
 assert not validate(projected),validate(projected)
 c['block_grid']=projected['block_grid'];c['block_ports']=ports;c['block_reservations']=[[0,0,1280,1024]]
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='batch30/N04',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=dict(timer=timer,geometry='protocol-v1 actual two256px ascents'))
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/block-N04/'+str(timer),source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],junction_role='interchange',core='same timed original door is first opening then actual landing/recharge before a real high-direction choice'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=4,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=a,to_port=b,role='main',route_id=a+'-to-'+b)for a,b in PAIRS],space=dict(max_width=1280,max_height=1024,max_port_span_x=1280,block_size=128,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Actual lower A or D supported dock, gate initially closed, original one-air-shot resources; common world for every route',exit='Observed high B or C, generic world-state transfer UNKNOWN'),return_conditions='Two low ingress directions and two high choices only. Other8 ordered pairs, arbitrary gate phase, generic missed shot recovery, boundaries and Map UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('only N04 registered Block world')
 return[candidate(a,b,.2)for a,b in PAIRS]

def purpose(c,r):
 fs=r.get('frames',[]);why=[];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];hits=[e['frame']for e in r.get('plains',{}).get('events',[])if e.get('type')=='bell_open'and e.get('id')=='return-catch']
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if c['required_rewards'][0]not in {e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}:why.append('required_high_reward_missing')
 shot=shots[0]if shots else None
 counter=bool(c.get('counterexample_kind'))
 first=next((f for f in fs if shot and f['frame']>shot['frame']and f.get('grounded')and(not counter or f.get('n04',{}).get('real_top_support'))),None)
 hit=max((t for t in hits if first and t<first['frame']),default=hits[0]if hits else None)
 clear=next((f for f in fs if hit is not None and f['frame']>=hit and f['y']+18<=608 and f['x']-12>=384 and f['x']+12<=896),None)
 close=next((f for f in fs if hit is not None and f['frame']>hit and not f.get('n04',{}).get('open',True)and f.get('n04',{}).get('collision_layer')==1 and not f.get('n04',{}).get('shape_disabled',True)),None)
 gate=bool(first and first.get('n04',{}).get('real_top_support')and abs(first['y']+18-608)<.2 and first.get('support_id')=='n04_return_catch_gate')
 if not c.get('counterexample_kind')and(not shot or shot.get('grounded')or hit is None):why.append('nominal_same_air_shot_opening_missing')
 if not gate:why.append('first_post_shot_landing_not_actual_same_gate_top')
 if not(clear and close and first and clear['frame']<=close['frame']<first['frame']):why.append('actual_body_clear_close_land_order_failed')
 if close and close['y']+18>(608 if counter else 584):why.append('gate_closed_before_complete_body_left_antipinch_growth'if not counter else'counter_body_not_clear_of_real_gate_at_close')
 if counter and any(f.get('grounded')and f['y']+18<=608 and not f.get('n04',{}).get('real_top_support')and shot and first and shot['frame']<f['frame']<first['frame']for f in fs):why.append('fixed_upper_landing_replaced_gate_before_catch')
 if first and first.get('shot_charges',0)<1:why.append('no_actual_gate_ground_refill')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_left_frozen_block_reservation')
 return dict(ok=not why,reasons=why,causal=dict(first_shot=shot['frame']if shot else None,actual_bell_hit=hit,complete_body_clear=clear['frame']if clear else None,actual_gate_closed=close['frame']if close else None,first_landing={k:first.get(k)for k in ['frame','x','y','support_id','shot_charges']}if first else None,real_gate_top_support=gate,close_body_bottom=close['y']+18 if close else None,unreserved_body_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})

def alternatives(c):
 out=[];original=copy.deepcopy(c['control_plan']);entry=c['rule_parameters']['entry'];target=c['rule_parameters']['target'];side=-1 if target=='B'else 1
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 p=copy.deepcopy(original);p[7]=cmd('wait');add('omit-opening-air-shot',p)
 p=copy.deepcopy(original);p[18]=cmd('wait');add('omit-high-bank-recoil',p)
 for hold in [8,20,28]:
  edge=240 if entry=='A'else 1040;direction=1 if entry=='A'else -1
  add('ordinary-low-shore-'+str(hold),[cmd('axis',value=direction),wait_x(edge,direction),cmd('jump'),cmd('jump_release',hold),settle(c['exit_port'][0]),ground(),cmd('wait',10)])
 for dy in [.15,.6,.85,.99]:
  edge=240 if entry=='A'else 1040;direction=1 if entry=='A'else -1
  add('direct-low-shore-recoil-'+str(dy),[cmd('axis',value=direction),wait_x(edge,direction),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-side*math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0]),ground(),cmd('wait',10)])
 for x in [400,880]:
  direction=-1 if x<640 else 1
  add('around-gate-edge-'+str(x),copy.deepcopy(original[:5])+[cmd('axis',value=direction),wait_x(x,direction),cmd('axis',value=0),ground(),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-side*.35,math.sqrt(1-.35**2)]),settle(c['exit_port'][0]),ground(),cmd('wait',10)])
 add('ground-prefire-extra-shot',copy.deepcopy(original[:5])+[cmd('shoot',aim_cell=dict(kind='bell',id='return-catch')),cmd('wait',8)]+copy.deepcopy(original[5:]))
 add('low-shore-prefire-extra-shot',[cmd('shoot',aim_cell=dict(kind='bell',id='return-catch')),cmd('wait',12)]+copy.deepcopy(original))
 add('long-wait-before-catching',copy.deepcopy(original[:8])+[cmd('wait',30)]+copy.deepcopy(original[8:]))
 add('skip-gate-catch-air-retry',copy.deepcopy(original[:8])+[cmd('axis',value=side),cmd('shoot',12,direction=[-side*.35,math.sqrt(1-.35**2)]),settle(c['exit_port'][0]),ground(),cmd('wait',10)])
 p=copy.deepcopy(original);p[7]=cmd('shoot',direction=[1,0]);add('miss-opening-receiver',p)
 for hold in [12,28]:
  p=copy.deepcopy(original);p[6]['trigger']['after']=hold;add('different-first-jump-'+str(hold),p)
 assert len(out)==18
 return out
