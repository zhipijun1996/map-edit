from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
def candidate(interface=0,control=0):
 if interface not in [0,1]:raise ValueError('Outside registered two-space C07 domain')
 c=prior.candidate(0,control);c['id']=f'b30-c07-v3-i{interface}-c{control}'
 if interface==0:
  c['platforms']=[[-160,180,400,32],[214,620,100,30],[550,510,230,80],[-160,950,1120,60],[-160,800,140,30],[760,800,160,30],[780,660,140,30]]
  c['latches']=[dict(id='brake-pair',bell=[450,240],gate=[490,-200,24,820],paired_gate=[190,212,24,408],initial_open='B')]
  start=[100,162];point=[650,492];depart=[320,330,340,350][control];edge=295;sign=1;direction=[-.8,.6]
 else:
  c['platforms']=[[320,98,480,32],[290,680,100,30],[-220,540,240,80],[-300,1080,1250,60],[800,930,140,30],[-300,930,140,30],[-300,780,140,30],[-280,650,100,30]]
  c['latches']=[dict(id='brake-pair',bell=[80,240],gate=[50,-200,24,880],paired_gate=[390,130,24,550],initial_open='B')]
  start=[400,80];point=[-120,522];depart=[240,230,220,210][control];edge=310;sign=-1;direction=[.8,.6]
 c['ports']=[dict(id='A',position=start,normal=[-1,0]if interface==0 else[0,-1],support_index=0),dict(id='B',position=point,normal=[sign,0],support_index=2)]
 c.update(spawn=start,entry_port=start,exit_port=point,goal=[point[0]-25,point[1]-4,50,8],interface=interface)
 c['reward_sites']=[];reward(c,*point,12)
 c['control_plan']=[cmd('axis',value=sign),wait_x(depart,sign),cmd('shoot',aim_cell=dict(kind='bell',id='brake-pair')),cmd('axis',value=-sign,after=6),cmd('wait',45),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,direction=direction),settle(point[0],6)]
 c['rule_parameters'].update(interface=interface,control=control,shot_at_actor_x=depart,side_normal=sign,spatial_role='horizontal behind old lip'if interface==0 else'upper ingress, deep shaft, lower-left outlet')
 c['layout_title']='关出一面能接住反冲的墙 / '+('横向浅袋'if interface==0 else'坠井右袋')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C07',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 # Reflect snapshot contact observations only for the leftward spatial adapter;
 # original recorded positions/velocities and contacts stay byte-for-byte raw.
 if c['interface']==0:return prior.purpose(c,r)
 import copy
 v=copy.deepcopy(c);s=copy.deepcopy(r);v['interface']=0
 for latch in v['latches']:
  for key in ['gate','paired_gate']:
   rect=latch[key];rect[0]=-rect[0]-rect[2]
 for f in s.get('frames',[]):
  f['x']=-f['x'];f['vx']=-f['vx']
  for hit in f.get('original_slide_contacts',[]):
   hit['normal'][0]=-hit['normal'][0];hit['position'][0]=-hit['position'][0]
 q=prior.purpose(v,s);q['causal']['observation_reflected_for_leftward_adapter']=True;q['causal']['raw_side_normal']=-1
 return q
