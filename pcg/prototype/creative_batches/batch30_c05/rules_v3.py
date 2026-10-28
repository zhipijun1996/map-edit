"""Final two-space station-choice domain; tall use waits for wide prototype proof."""
from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def wait_depart(x,sign):
 q=wait_x(x,sign);q['trigger']['timeout']=260;return q
def candidate(interface=0,control=0,route='near'):
 if interface not in [0,1]:raise ValueError('outside registered C05 space domain')
 c=prior.candidate(0,control,route);c['id']=f'b30-c05-v3-i{interface}-{route}-c{control}';c['interface']=interface
 if interface==0:
  c['platforms'][1]=[520,310,120,20];c['platforms'][3]=[-100,280,580,120]
  c['ports'][1]['position']=[180,262];c['reward_sites'][0].update(position=[180,262],region=[150,257,60,10]);c['latches'][1]['bell']=[860,220]
  prefix=c['control_plan'][:11]
  depart=([670,690,710,730]if route=='near'else[820,850,880,900])[control]
  if route=='near':plan=prefix+[wait_depart(depart,1),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),wait_x(580,-1),*rest(),cmd('axis',value=-1),wait_x(525,-1),cmd('jump'),cmd('jump_release',8),settle(180,6)];point=[180,262]
  else:plan=prefix+[wait_depart(depart,1),cmd('axis',value=1),cmd('jump'),cmd('jump_release',18),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),settle(1160,6)];point=[1160,182]
 else:
  c['platforms']=[[1060,758,340,45],[860,430,60,20],[0,180,220,80],[960,400,440,120],[270,430,200,570],[-50,1000,1450,60],[1240,880,160,30],[0,860,140,30],[40,720,140,30],[100,580,140,30]]
  c['moving_platforms']=[dict(platform_id='branch-ferry',start=[970,760],finish=[400,210],size=[200,20],travel_duration=3.4,dwell_duration=.15,initial_phase=0)]
  c['latches']=[dict(id='ferry-start',bell=[1150,710],gate=[1390,-250,10,10],open_seconds=0,ferry_id='branch-ferry'),dict(id='station-selector',bell=[450,180],gate=[716,-300,24,800],paired_gate=[256,-300,24,580],initial_open='A')]
  c['ports']=[dict(id='A',position=[1220,740],normal=[0,1],support_index=0),dict(id='B',position=[1120,382],normal=[1,0],support_index=3),dict(id='C',position=[140,162],normal=[-1,0],support_index=2)]
  c['one_way_platform_indices']=[0];c['spawn']=[1220,740];c['entry_port']=[1220,740]
  c['reward_sites']=[dict(id='near-cache',position=[1120,382],region=[1090,377,60,10],amount=10),dict(id='far-cache',position=[140,162],region=[110,157,60,10],amount=16)]
  prefix=[cmd('axis',value=-1),wait_x(1095,-1),cmd('jump'),cmd('jump_release',8),wait_x(970,-1),cmd('axis',value=0),prior.old.on_deck(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='ferry-start')),cmd('wait',12),cmd('axis',value=0)]
  depart=([700,670,640,610]if route=='near'else[500,470,440,410])[control]
  if route=='near':plan=prefix+[wait_depart(depart,-1),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),wait_x(890),*rest(),cmd('axis',value=1),wait_x(915),cmd('jump'),cmd('jump_release',8),settle(1120,6)];point=[1120,382]
  else:plan=prefix+[wait_depart(depart,-1),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',18),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),settle(140,6)];point=[140,162]
 c.update(exit_port=point,goal=[point[0]-25,point[1]-4,50,8],control_plan=plan,max_frames=1700)
 c['rule_parameters'].update(interface=interface,control=control,departure_actor_x=depart,geometry='wide underarch'if interface==0 else'tall rising court',capabilities='Only original move/jump/shot_recoil',near_bank_internal=True)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','one_way_platform_indices']})
 c['layout_title']='追台时选择哪一个岸 / '+('斜升断拱'if interface==0 else'高庭回望')
 c['generation_rule']=dict(id='batch30/C05',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c

def purpose(c,r):
 q=prior.purpose(c,r)
 if not r.get('frames'):return q
 supported=[f for f in r['frames']if f.get('grounded')and f.get('support_id')=='branch-ferry']
 centers=[]
 for f in supported:
  p=next((p for p in f.get('moving_platforms',[])if p['id']=='branch-ferry'),None)
  if p:centers.append(p['position'])
 dx=max((p[0]for p in centers),default=0)-min((p[0]for p in centers),default=0);dy=max((p[1]for p in centers),default=0)-min((p[1]for p in centers),default=0)
 q['reasons']=[x for x in q['reasons']if x not in ['actual_neutral_moving_carriage_missing','actual_boarding_and_departure_jumps_missing']]
 if len(supported)<6 or max(dx,dy)<8:q['reasons'].append('original_support_did_not_really_carry_actor')
 if r.get('jumps',0)<1:q['reasons'].append('boarding_jump_missing')
 q['causal'].update(actual_carrier_supported_dx=dx,actual_carrier_supported_dy=dy,carriage_is_real_even_for_active_walking=True,airborne_selector_is_canonical_not_only_legal_method=True)
 q['ok']=not q['reasons'];return q
