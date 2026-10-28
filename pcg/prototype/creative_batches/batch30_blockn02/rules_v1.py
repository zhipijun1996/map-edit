"""Automatic approach carrier, active second-carrier intercept, real fork."""
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.map_directed.block_grid.contracts import anchor,declare,validate,raster
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-active-transfer-fork',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
NATIVE_SCENE='res://prototype/creative_batches/batch30_blockn02/main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py']

def on(pid,timeout=360):return dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id=pid),timeout=timeout))
def phase():return dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='approach-carrier',window=[.82,.84]),timeout=650))

def candidate(interface=0,control=0,route='high'):
 if interface!=0 or route not in ['high','low']or control not in range(4):raise ValueError('needs_design: onlyfirstnewtransferforkspacedomain')
 c=base(f'b30-blockn02-v1-i0-{route}-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[0,608,208,48],[1216,224,64,40],[1184,608,96,48],[0,864,1280,48]]
 c['moving_platforms']=[dict(platform_id='approach-carrier',start=[256,544],finish=[800,544],size=[176,20],travel_duration=2.4,dwell_duration=.12,initial_phase=.6),dict(platform_id='intercept-carrier',start=[896,416],finish=[1152,288],size=[176,20],travel_duration=1.2,dwell_duration=.12,initial_phase=0)]
 c['latches']=[dict(id='intercept-start',bell=[704,560],gate=[0,1000,8,8],open_seconds=0,ferry_id='intercept-carrier')]
 c['ports']=[dict(id='A',position=[24,590],normal=[-1,0],support_index=0),dict(id='B',position=[1256,206],normal=[1,0],support_index=1),dict(id='C',position=[1256,590],normal=[1,0],support_index=2)]
 c['reward_sites']=[dict(id='high-cache',position=[1256,206],region=[1231,201,50,10],amount=16),dict(id='low-cache',position=[1256,590],region=[1231,585,50,10],amount=8)]
 board=[cmd('axis',value=1),wait_x(192),cmd('axis',value=0),ground(),cmd('wait',4),phase(),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),wait_x(315),cmd('axis',value=0),on('approach-carrier'),cmd('wait',8),cmd('axis',value=0)]
 if route=='high':
  departure=[700,720,740,760][control];hold=[16,16,20,20][control]
  plan=board+[wait_x(departure),cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='bell',id='intercept-start')),on('intercept-carrier'),cmd('axis',value=0),cmd('wait',8),wait_x(1120),cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,direction=[-.8,.6]),settle(1256,6)]
  to='B';target=[1256,206];reward='high-cache';amount=16
 else:
  departure=[720,740,760,780][control]
  plan=board+[wait_x(departure),cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-.98,.1989974874]),settle(1256,6)]
  to='C';target=[1256,590];reward='low-cache';amount=8
 c.update(spawn=[24,590],entry_port=[24,590],exit_port=target,goal=[1249,target[1]-4,14,8],control_plan=plan,max_frames=1800,trace_all=False,interface=0,production_recipe=RECIPES[0],challenge_route=True,expected_reward=amount,required_rewards=[reward],idea_ids=['B30-N02'],native_scene=NATIVE_SCENE,native_block_scene=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3])))
 c['route_spec']=dict(id=route,from_port='A',to_port=to,role='main',via_ports=[],require_bell=route=='high',required_rewards=[reward])
 ports={}
 for p,cell,edge in zip(c['ports'],[[0,4],[9,1],[9,4]],['W','E','E']):
  point=anchor(cell,edge);ports[p['id']]=dict(position=point,normal=p['normal'],grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=p['position']),crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
 reserves=[[12,128,1256,736]];module=declare(dict(case=c,ports=ports,action_clearance=reserves),{(x,y)for x in range(10)for y in range(8)})
 errors=validate(module)
 if errors:raise ValueError('blockN02static/'+','.join(errors))
 c['block_grid']=module['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['layout_title']='双台主动转乘分流 / 留在低河道或追上升台'
 c['rule_parameters']=dict(interface=0,control=control,route=route,departure_actor_x=departure,active_static_bell=[704,560],automatic_P1_boarding_phase_window=[.82,.84],phase_is_randomized_in_original_evaluator=True,novelty='composite_not_independently_counted')
 c['generation_rule']=dict(id='batch30/blockN02',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=specification(c)
 return c

def specification(c):
 return dict(schema='map-notes/challenge-specification/v1',id='block-demand/N02/active-transfer-fork',source_type='model_authored_TaskA_current_Map_contract_demand',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],junction_role='fork',core='Sameapproachcarrier decision: staythenrecoilto loweast or shootoriginalstaticbell to chaseactualsecondcarrier and renew before higheast',independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[1,0],[1,0]],block_profiles=['ground64/v1']),relations=[dict(from_port='A',to_port=to,role='main',route_id=route)for route,to in [('high','B'),('low','C')]],space=dict(block_size=128,max_width=1280,max_height=1024,boundary_policy='open',ownership_shape='connected_polyomino'),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],recovery_floor='internalonly'),resource_state=dict(reset_between_components=False,entry='Same actualgroundedA, automaticP1 randomizedphase, P2parked. No carryinginertia claim.',exit='Actual selecteddock/reward/carrierstate only; arbitraryworld/state propagationUNKNOWN'),return_conditions='OnlyA->B/A->C; otherfourpairs,boundarycrossing,seams,recoveryUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))

def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 if not set(c['required_rewards'])<=claimed:why.append('selected_reward_missing')
 first=[f for f in fs if f.get('grounded')and f.get('support_id')=='approach-carrier'];second=[f for f in fs if f.get('grounded')and f.get('support_id')=='intercept-carrier']
 span=max((f['x']for f in first),default=0)-min((f['x']for f in first),default=0)
 if len(first)<6 or span<60:why.append('actual_P1_carriage_missing')
 toggles=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='carrier_toggle'and e.get('id')=='intercept-start']
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 renewal=[]
 if c['route_spec']['id']=='high':
  if not toggles or not toggles[0].get('running'):why.append('actual_P2_start_missing')
  if len(second)<6:why.append('actual_second_carrier_interception_missing')
  renewal=[f for f in second if shots and shots[0]['frame']<f['frame']and f.get('shot_charges')==1]
  if not renewal:why.append('real_P2_ground_refill_missing')
  if toggles and not toggles[0].get('airborne')and r.get('shots',0)<3:why.append('neither_air_start_nor_costed_prestart')
  if not second or not shots or not any(f['frame']>second[0]['frame']for f in shots):why.append('onward_after_P2_landing_missing')
 elif second:why.append('low_route_unexpected_second_carrier_use')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_complete_body_outside_frozen_block_ownership')
 return dict(ok=not why,reasons=why,causal=dict(actual_P1_support_frames=len(first),P1_carried_span=span,actual_P2_support_frames=len(second),real_P2_refill_frames=len(renewal),P2_toggles=toggles,outside_body_frames=outside[:12],outside_count=len(outside),shot_positions=[dict(frame=f['frame'],x=f['x'],y=f['y'],grounded=f.get('grounded'))for f in shots]),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
