"""B30-C10: actual retained-air-shot recovery, not another map port."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('retained-shot-recovery',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[HERE.parent/'batch30_c04/stable_support_names_v1.gd']+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]
DELAYS=[0,4,8,12]
def nominal():return[cmd('axis',value=1),wait_x(180),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.6,.8]),settle(650),ground(),cmd('wait',10)]
def materialize(interface=0,route='main',control=0):
 if interface!=0:raise ValueError('C10 second spatial demand remains UNKNOWN before core')
 c=base('c10');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['spawn']=[80,420];c['entry_port']=[80,420]
 c['platforms']=[[-100,438,300,80],[500,360,240,100],[150,630,250,40],[250,490,150,40]]
 c['latches']=[dict(id='recovery-pair',bell=[500,650],return_access=[350,580],gate=[250,-200,20,830],paired_gate=[400,500,20,130],initial_open='A',open_seconds=0)]
 c['reward_sites']=[];reward(c,650,342,12)
 if route=='main':p=nominal();target=[650,342]
 else:
  p=[cmd('axis',value=1),wait_x(180),cmd('jump'),cmd('jump_release',20),wait_x(440),cmd('shoot',DELAYS[control],aim_cell=dict(kind='bell',id='recovery-pair')),settle(330),ground(),cmd('wait',10)];target=[330,612]
 c['control_plan']=p;c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8]
 c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=[650,342],normal=[1,0],support_index=1)]
 c['route_spec']=dict(id='main'if route=='main'else'conditional-recovery-fixture',from_port='A',to_port='B'if route=='main'else'INTERNAL_RECOVERY',role='main'if route=='main'else'fixture',via_ports=[],require_bell=route!='main')
 c['id']=f'b30-c10-v1-i{interface}-{route}-c{control}';c['interface']=interface;c['max_frames']=900;c['trace_all']=False;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12 if route=='main'else 0;c['required_rewards']=['visible-cache']if route=='main'else[];c['idea_ids']=['B30-C10'];c['native_scene']='res://prototype/creative_batches/batch30_c10/main_v1.tscn'
 c['layout_title']='留一枪，把失误变成另一条活路 / 反向侧洞';c['rule_parameters']=dict(interface=interface,route=route,control=control,correction_delay=DELAYS[control],core='actual retained shot simultaneously opens recovery cavity and redirects a real miss; internal cavity is not map port')
 c['generation_rule']=dict(id='batch30/C10',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters']);c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites']})
 return c

def purpose(c,r):
 fs=r.get('frames',[]);pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0];events=[e for e in pair.get('events',[])if e.get('type')=='pair_switch'];why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5:why.append('harm')
 if r.get('returns'):why.append('reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 correction=[]
 for f in fs:
  if any(e.get('type')=='shot'for e in f.get('accepted',[])):
   before=next((v for v in fs if v['frame']==f['frame']-1),{})
   correction.append(dict(frame=f['frame'],before_charges=before.get('shot_charges'),before_vy=before.get('vy'),airborne=not f.get('grounded'),x=f['x'],y=f['y']))
 cavity=[f['frame']for f in fs if f.get('grounded')and f.get('support_id')=='Platform2']
 if c['rule_parameters']['route']=='main':
  if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 else:
  if not cavity:why.append('no_actual_cavity_landing')
  if not any(e.get('open')=='B'and e.get('airborne')for e in events):why.append('no_air_correction_opening')
  if not any(e.get('before_charges',0)>0 and e.get('airborne')for e in correction):why.append('no_real_retained_charge')
 return dict(ok=not why,reasons=why,causal=dict(correction_shots=correction,cavity_grounded_frames=cavity,actual_swaps=events),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
