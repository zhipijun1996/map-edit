from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
def rest():return[ground(),cmd('wait',8)]
def rise(old_x,new_x,hold=20):
 return[settle(old_x),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[0,1]),cmd('wait',10),settle(new_x),*rest()]
def candidate(interface=0,control=0,route='loop'):
 if interface not in[0,1]:raise ValueError('Outside two registered C09 spaces')
 c=prior.candidate(0,control,route);c['id']=f'b30-c09-v3-i{interface}-{route}-c{control}'
 if interface==0:
  c['platforms']=[[0,1000,240,80],[330,760,160,60],[450,520,100,100],[500,280,210,620],[820,680,200,470],[260,1140,450,40],[-160,1200,1400,60],[-160,1170,180,30],[1060,1170,140,30]]
  c['latches']=[dict(id='return-pair',bell=[270,1080],gate=[750,80,24,600],paired_gate=[750,900,24,240],initial_open='B',return_access=[810,960])]
  start=[80,982];point=[900,662];edge=205;first=400;second=470;top=560;shaft=800;low=600;returnedge=280;hold=[10,12,14,16][control]
 else:
  c['platforms']=[[0,1260,210,80],[300,1040,120,60],[400,810,80,80],[450,580,200,560],[740,980,180,430],[240,1400,410,40],[-140,1460,1200,40],[-140,1430,160,30],[960,1430,100,30]]
  c['latches']=[dict(id='return-pair',bell=[240,1340],gate=[680,380,24,600],paired_gate=[680,1140,24,260],initial_open='B',return_access=[730,1260])]
  start=[80,1242];point=[820,962];edge=175;first=360;second=430;top=520;shaft=724;low=560;returnedge=260;hold=[12,14,16,18][control]
 c['ports']=[dict(id='A',position=start,normal=[-1,0],support_index=0),dict(id='B',position=point,normal=[1,0],support_index=4)]
 c.update(spawn=start,entry_port=start,exit_port=point,interface=interface,goal=[start[0]-25,start[1]-4,50,8]if route=='loop'else[point[0]-25,point[1]-4,50,8])
 out=[cmd('axis',value=1),wait_x(edge),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,aim_cell=dict(kind='bell',id='return-pair')),settle(first,6),wait_x(first-4),*rest(),*rise(first,second),*rise(second,top),settle(point[0]),wait_x(point[0]-4),*rest(),cmd('wait',12)]
 ret=[settle(shaft),wait_x(shaft+4,-1),cmd('wait',32),cmd('shoot',aim_cell=dict(kind='bell',id='return-pair',receiver='access')),settle(low,6),wait_x(low+4,-1),*rest(),settle(returnedge),wait_x(returnedge+4,-1),cmd('jump'),cmd('jump_release',32),settle(start[0],6)]
 c['control_plan']=out+ret if route=='loop'else out;c['reward_sites']=[];reward(c,*point,16)
 c['rule_parameters'].update(interface=interface,control=control,first_jump_release=hold,first_takeoff=edge,rise_landing_targets=[first,second,top],return_shaft_x=shaft,return_floor_y=c['platforms'][5][1],conservative_geometry_extent_height=1180 if interface==0 else 1120)
 c['layout_title']='去程走高，回程把空间翻到低处 / '+('宽石冠腹下'if interface==0 else'窄高折返庭')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C09',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 # Original check uses one fixed far-port position; adapt only observation target.
 import copy
 v=copy.deepcopy(r);target=c['ports'][1]['position'];dx=900-target[0];dy=582-target[1]
 for f in v.get('frames',[]):
  if f.get('grounded')and f.get('support_id')=='Platform4':f['x']+=dx;f['y']+=dy
 q=prior.purpose(c,v);q['causal']['actual_far_port_position']=target;q['causal']['same_world_original_trace_not_modified']=True
 return q
