"""D04 first physical hypothesis. Existing ShotLatch/ModuleMovingPlatform only."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('park-for-return',)
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json']

def on(id):return dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id=id),timeout=240))
def land():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def hop(sign,x,dy=.75,hold=20,shot=0):return [cmd('axis',value=sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot,direction=[-sign*math.sqrt(1-dy*dy),dy]),settle(x,6)]

def materialize(interface=0,park='middle',route='outbound',control=0):
 c=base('d04');c['family']='park-for-return';c['capabilities']=['move','jump','shot_recoil'];dx=interface*30
 c['platforms']=[[-160,438,400,100],[570+dx,438,180,100],[780+dx,-500,55,1040],[1030+dx,650,190,100],[400,800,140,40],[40,620,140,40],[-400,1000,2100,40],[465,325,30,115]]
 c['moving_platforms']=[dict(platform_id='return-deck',start=[300,620],finish=[900+dx,620],size=[176,20],travel_duration=3.,dwell_duration=.15,initial_phase=0)]
 c['latches']=[dict(id='return-control',bell=[155,395],gate=[-100,100,10,10],open_seconds=0,ferry_id='return-deck')]
 c['reward_sites']=[];reward(c,1110+dx,632,12)
 c['ports']=[dict(id='A',position=[80,420],support_index=0,normal=[-1,0]),dict(id='B',position=[650+dx,420],support_index=1,normal=[1,0]),dict(id='C',position=[1110+dx,632],support_index=3,normal=[1,0]),dict(id='D',position=[110,602],support_index=5,normal=[-1,0])]
 hold,shot=[(12,6),(20,0),(12,12),(20,6)][control]
 out=[cmd('shoot',aim_cell=dict(kind='bell',id='return-control')),cmd('wait',90 if park=='reward'else 0),cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot,aim_cell=dict(kind='bell',id='return-control')),wait_x(650+dx-4),*land()]
 # Drop off B's left lip onto a middle parked carrier, then rebound to A.
 back_mid=[cmd('axis',value=-1),wait_x(555+dx,-1),cmd('axis',value=0),on('return-deck'),cmd('wait',10),cmd('axis',value=-1),wait_x(490,-1),*hop(-1,110,.15)]
 target='B';plan=out
 if route=='return-middle':target='D';plan=out+back_mid
 elif route in ['reward-out','reward-return']:
  target='C';plan=out+[cmd('axis',value=1),wait_x(870+dx),cmd('axis',value=0),on('return-deck'),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-.9886859967,.15]),settle(1110+dx,6)]
  if route=='reward-return':
   target='D';plan=plan[:-1]+[wait_x(1110+dx-4),*land(),cmd('axis',value=-1),wait_x(1060+dx,-1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[.9539392,.3]),wait_x(875+dx,-1),cmd('axis',value=0),on('return-deck'),cmd('wait',8),cmd('axis',value=-1),wait_x(760,-1),cmd('jump'),cmd('jump_release',12),wait_x(470,-1),*land(),cmd('axis',value=-1),wait_x(415,-1),*hop(-1,110,.8660254)]
 end=next(p for p in c['ports']if p['id']==target)['position'];uid=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c.update(id=f'b30-d04-v3-i{interface}-{park}-{route}-c{control}',spawn=[80,420],entry_port=[80,420],exit_port=end,goal=[end[0]-25,end[1]-4,50,8],control_plan=plan,max_frames=1400,trace_all=False,layout_uid=uid,layout_title='留给回程的停台',interface=interface,production_recipe=RECIPES[0],challenge_route=True,expected_reward=12 if route in ['reward-out','reward-return']else 0)
 c['route_spec']=dict(id=route,from_port='A',to_port=target,role='return'if target=='D'else'main',via_ports=(['B','C']if route=='reward-return'else['B']if target!='B'else[]),require_bell=True)
 c['rule_parameters']=dict(interface=interface,park=park,route=route,control=control,purpose='outgoing recoil shot parks a return/reward support')
 c['generation_rule']=dict(id='batch30/D04',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['idea_ids']=['PR-D04'];return c

def purpose(c,r):
 why=[];fs=r.get('frames',[])
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('reset_or_teleport')
 toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']
 if len(toggles)<2 or toggles[1]['running']or not toggles[1]['airborne']:why.append('airborne_park_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=dict(toggles=toggles,carrier_support_frames=sum(f.get('support_id')=='return-deck'for f in fs)),behavior={})
