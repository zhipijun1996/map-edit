"""N03: real signed trajectory reversal; original character and carrier bodies."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward
from pcg.prototype.workshop.evaluate import purpose as base_purpose
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.prototype.factory.core.quality import digest
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
HERE=Path(__file__).parent
RECIPES=('block128-real-reverse-intercept',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
SOURCE_DEPENDENCIES=[HERE/f for f in ['protocol-v1.json','reverse_definition_v1.gd','reverse_carrier_v1.gd','reverse_latch_v1.gd','runtime_v1.gd','runner_v1.gd']]+[Path(__file__),HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v1.json']


def machinery(c,initial_x=480,speed=140,dwell=.15,direction=1,offset=(72,-48),start=256,finish=1280):
 c['moving_platforms']=[dict(platform_id='reverse-carrier',start=[start,480],finish=[finish,480],size=[176,20],travel_duration=(finish-start)/speed,dwell_duration=dwell,initial_phase=0,control_mode='reverse_on_hit',initial_clock_offset=(dwell+(initial_x-start)/speed)if initial_x>start else 0,initial_direction=direction,endpoint_policy='hold_until_manual_reverse')]
 c['latches']=[dict(id='reverse-bell',bell=[initial_x+offset[0],480+offset[1]],gate=[32,32,8,8],ferry_id='reverse-carrier',carrier_mount='reverse-carrier',control_mode='reverse_on_hit',open_seconds=0)]
 return c


def module_candidate(target='B',control=0):
 if target not in ['B','C']or control not in range(4):raise ValueError('outside registered control domain')
 c=base('n03');c['platforms']=[[0,736,768,64],[1376,224,160,96],[0,224,192,96],[96,864,1344,48]];machinery(c)
 a=[24,718];b=[1512,206];west=[24,206];end=b if target=='B'else west
 c.update(family=RECIPES[0],production_recipe=RECIPES[0],interface=0,spawn=a,entry_port=a[:],exit_port=end[:],goal=[end[0]-25,end[1]-4,50,8],world_bounds=[-512,-512,2560,2048],max_frames=1400,trace_all=True,expected_reward=12,required_rewards=['east-cache'if target=='B'else'west-cache'])
 c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=1),dict(id='C',position=west,normal=[-1,0],support_index=2)]
 c['block_ports']={'A':block_port('A',[0,5],'W',a),'B':block_port('B',[11,1],'E',b),'C':block_port('C',[0,1],'W',west)}
 c['block_reservations']=[[0,0,1536,1024]]
 c['reward_sites']=[dict(id='east-cache',position=b,region=[1482,200,60,12],amount=12),dict(id='west-cache',position=west,region=[0,200,60,12],amount=12)]
 h=[20,20,24,24][control];dy=[.95,.98,.95,.98][control]
 boarding=[cmd('axis',value=1),wait_x(732),cmd('jump'),cmd('jump_release',h),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='reverse-carrier'),timeout=240)),cmd('axis',value=0)]
 if target=='B':tail=[wait_x(1240),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[-.5,.8660254037844386]),settle(end[0],6)]
 else:tail=[cmd('wait',12),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,aim_cell=dict(kind='bell',id='reverse-bell')),cmd('axis',value=0),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='reverse-carrier'),timeout=240)),wait_x(300,-1),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[.5,.8660254037844386]),settle(end[0],6)]
 c['control_plan']=boarding+tail
 c['route_spec']=dict(id='keep-east'if target=='B'else'reverse-west',from_port='A',to_port=target,role='main',via_ports=[],require_bell=target=='C',required_rewards=c['required_rewards'])
 c['rule_parameters']=dict(control=control,boarding_hold=h,boarding_dy=dy,target=target,reverse_cell='manual_reverse_on_hit/v1',same_initial_world=True)
 c['id']=f'b31-block-n03-v1-i0-{target.lower()}-c{control}';c['layout_title']='让台掉头，接住另一边的自己'
 c['idea_ids']=['B31-N03'];c['generation_rule']=dict(id='B31-N03/manual-reverse-intercept',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],new_cell_required=True)
 projected=dict(case=c,ports=c['block_ports'],action_clearance=c['block_reservations'])
 own=set().union(*(raster(r)for r in regions(projected)))
 # Original receiver28x34 moves on the carrier for the entire known path.
 m=c['moving_platforms'][0];own|=raster([m['start'][0]+72-14,480-48-17,m['finish'][0]-m['start'][0]+28,34])
 projected=declare(projected,own);errors=validate(projected)
 if errors:raise ValueError(errors)
 c['block_grid']=projected['block_grid'];c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31/N03/three-port-east-or-reverse-west',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],roles=['traversal','fork'],physical_layout_sha256=c['layout_uid'],decision='retain east heading to B; reverse/catch/real refill and ride west to C'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[1,0],[-1,0]]),relations=[dict(from_port='A',to_port=k,role='main')for k in ['B','C']],space=dict(max_width=1536,max_height=1024,block_size=128,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='Original supported A internal stage; signed carrier initially east-moving at authored playhead, same world for both routes',exit='Observed stable highbank/resources only; arbitrary-state transfer UNKNOWN'),return_conditions='B->A/B->C/C->A/C->B UNKNOWN; retained bottom floor does not certify retry',budget=dict(generator_candidates=8,director_revisions=0))
 return c


def purpose(c,r):
 q=base_purpose(c,r);fs=r.get('frames',[]);owned=set(map(tuple,c.get('block_grid',{}).get('cells',[])));outside=[]
 for a,b in zip(fs,fs[1:]):
  if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned:outside.append(b['frame'])
 states=r.get('workshop',{}).get('reverse_carriers',[]);state=states[0]if states else{};events=state.get('events',[])
 supported=[f for f in fs if f.get('support_id')=='reverse-carrier'];neutral=[f for f in supported if abs(f['axis'])<.01];displacement=max([f['x']for f in neutral],default=0)-min([f['x']for f in neutral],default=0)
 q['causal'].update(reverse_events=events,carrier_supported_frames=len(supported),neutral_carried_span=displacement,outside_body_sweep_frames=outside[:20])
 if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
 if len(supported)<12 or displacement<12:q['reasons'].append('real_carriage_not_demonstrated')
 if c['route_spec']['to_port']=='C':
  first=events[0]if events else{};at=first.get('frame',99999);after=[f for f in fs if f['frame']>at];landing=next((f for f in after if f.get('grounded')),None);reverse_moving=[f for f in after if any(p.get('physics_velocity',[0])[0]<-1 for p in f.get('workshop',{}).get('reverse_carriers',[]))]
  caught=bool(landing and landing.get('support_id')=='reverse-carrier'and landing.get('shot_charges')==1 and landing.get('jumps_used')==0)
  q['causal'].update(first_ground_after_reverse=({k:landing.get(k)for k in ['frame','x','y','support_id','shot_charges','shot_cooldown','jumps_used','energy']}if landing else None),real_west_velocity_frames=len(reverse_moving),same_carrier_catch_and_refill=caught)
  if not events or not first.get('airborne')or first.get('direction')!=-1:q['reasons'].append('airborne_true_reversal_not_demonstrated')
  if not reverse_moving:q['reasons'].append('real_reverse_velocity_not_demonstrated')
  if not caught:q['reasons'].append('same_reversed_carrier_catch_not_demonstrated')
 for e in events:
  if e['position_before']!=e['position_after']:q['reasons'].append('reversal_teleported_platform')
 q['ok']=not q['reasons'];return q
