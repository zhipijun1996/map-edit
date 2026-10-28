"""C05: ascend under an arch and choose a real backward or forward station."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('moving-station-choice',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=CELL/'main_v3.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]]
def on_deck():return dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='branch-ferry'),timeout=240))
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def boarding():
 return [cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',8),wait_x(330),cmd('axis',value=0),on_deck(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='ferry-start')),cmd('wait',12),cmd('axis',value=0)]
def candidate(interface=0,control=0,route='near'):
 if interface!=0:raise ValueError('Second spatial demand waits for actual branch core proof')
 c=base(f'b30-c05-v1-i{interface}-{route}-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[-100,638,340,45],[400,400,120,20],[1080,200,220,80],[-100,400,480,120],[830,400,200,480],[-100,880,1500,60],[-100,760,160,30],[1160,740,140,30],[1120,600,140,30],[1060,460,140,30]]
 c['moving_platforms']=[dict(platform_id='branch-ferry',start=[330,640],finish=[900,250],size=[200,20],travel_duration=3.4,dwell_duration=.15,initial_phase=0)]
 c['latches']=[dict(id='ferry-start',bell=[150,590],gate=[-100,-150,10,10],open_seconds=0,ferry_id='branch-ferry'),dict(id='station-selector',bell=[700,350],gate=[560,-200,24,600],paired_gate=[1020,-200,24,500],initial_open='A')]
 c['ports']=[dict(id='A',position=[80,620],normal=[-1,0],support_index=0),dict(id='B',position=[450,382],normal=[-1,0],support_index=1),dict(id='C',position=[1160,182],normal=[1,0],support_index=2)]
 c['reward_sites']=[dict(id='near-cache',position=[450,382],region=[420,377,60,10],amount=10),dict(id='far-cache',position=[1160,182],region=[1130,177,60,10],amount=16)]
 c['spawn']=[80,620];c['entry_port']=[80,620]
 departure=([620,650,680,710]if route=='near'else[700,730,760,790])[control]
 if route=='near':plan=boarding()+[wait_x(departure),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),settle(450,6)];target='B'
 elif route=='far':plan=boarding()+[wait_x(departure),cmd('axis',value=1),cmd('jump'),cmd('jump_release',18),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),settle(1160,6)];target='C'
 else:raise ValueError('outside registered station routes')
 point=next(p['position']for p in c['ports']if p['id']==target)
 c.update(exit_port=point,goal=[point[0]-25,point[1]-4,50,8],control_plan=plan,max_frames=1500,trace_all=False,interface=interface,production_recipe=RECIPES[0],challenge_route=True,expected_reward=10 if route=='near' else 16,required_rewards=['near-cache'if route=='near'else'far-cache'],idea_ids=['B30-C05'],native_scene='res://prototype/creative_batches/batch30_c05/main_v1.tscn')
 c['route_spec']=dict(id=route,from_port='A',to_port=target,role='main',via_ports=[],require_bell=True,required_rewards=c['required_rewards'])
 c['required_pair_states']=[dict(id='station-selector',open_a=route=='near',open_b=route=='far')]
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['layout_title']='追台时选择哪一个岸 / 斜升断拱'
 c['rule_parameters']=dict(interface=interface,control=control,route=route,departure_actor_x=departure,carrier_trajectory='original parked-start, linear forth/back; no automatic docking',core='real carriage underneath the arch then backward upper-west or forward high-east station choice',port_roles=dict(A='lower-west ingress beneath arch',B='upper-west onward branch',C='high-east onward branch'))
 c['generation_rule']=dict(id='batch30/C05',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('unexpected_reset')
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 if not set(c['required_rewards'])<=claimed:why.append('correct_station_reward_missing')
 supported=[f for f in fs if f.get('grounded')and f.get('support_id')=='branch-ferry'];neutral=[f for f in supported if abs(f.get('axis',0))<.01]
 dx=max((f['x']for f in neutral),default=0)-min((f['x']for f in neutral),default=0)
 if len(neutral)<20 or dx<80:why.append('actual_neutral_moving_carriage_missing')
 jumps=[f for f in fs if any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))]
 if len(jumps)<2:why.append('actual_boarding_and_departure_jumps_missing')
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id']=='station-selector'),{})
 expected=c['required_pair_states'][0]
 if any(pair.get(k)!=v for k,v in expected.items()if k!='id'):why.append('station_selection_pair_state_wrong')
 running=next((p.get('running')for p in r.get('workshop',{}).get('carriers',[])if p['id']=='branch-ferry'),None)
 if running is not True:why.append('carrier_did_not_continue_after_branch_choice')
 return dict(ok=not why,reasons=why,causal=dict(real_supported_frames=len(supported),neutral_carried_frames=len(neutral),neutral_carried_dx=dx,pair=pair,carrier_still_running=running,actual_jump_frames=[f['frame']for f in jumps],coupled_airborne_choice=any(e.get('airborne')for e in pair.get('events',[])if e.get('type')=='pair_switch')),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
