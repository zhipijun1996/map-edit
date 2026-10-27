"""Recoil-only terrain recipes on the original production loop.

Four relationships, two explicit demands each. Old adapters and combinations
are kept distinct from novelty claims; no independent simulator/store.
"""
import argparse, copy, json, math
from pathlib import Path
from pcg.prototype.workshop.rules import thorn,brake,launch,settle,cmd,wait_x,reward,finish,specifications,ground
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT

HERE=Path(__file__).parent
CAPS=['move','jump','shot_recoil']
DEMANDS={
 'slot-low-approach':dict(recipe='terrain-slot',interface=0,front=482,top=428,landing_width=230),
 'slot-wide-exit':dict(recipe='terrain-slot',interface=1,front=508,top=442,landing_width=260),
 'brake-short-pocket':dict(recipe='terrain-brake',interface=0,lip=254,top=450,x=112,width=112),
 'brake-deep-pocket':dict(recipe='terrain-brake',interface=1,lip=248,top=464,x=102,width=120),
 'reload-level-relay':dict(recipe='landing-reload-relay',interface=0,first_front=480,first_top=438,second_front=945,second_top=438),
 'reload-rising-relay':dict(recipe='landing-reload-relay',interface=1,first_front=500,first_top=442,second_front=985,second_top=426),
 'pocket-rising-departure':dict(recipe='pocket-reload-climb',interface=0,lip=250,pocket_top=450,pocket_x=105,final_front=430,final_top=330),
 'pocket-side-departure':dict(recipe='pocket-reload-climb',interface=1,lip=258,pocket_top=464,pocket_x=112,final_front=450,final_top=348),
}

def materialize(key,control=0):
 d=DEMANDS[key];recipe=d['recipe'];i=d['interface'];id='p50-terrain-'+key+'-control-'+str(control)
 if recipe=='terrain-slot':
  c=thorn(0);front=d['front'];top=d['top'];x=front+105;y=top-18
  c['platforms'][1]=[front,top,d['landing_width'],160]
  c['platforms'][2][2]=front-220;c['thorns'][0]['length']=front-220
  hold,shot,takeoff=[(8,16,205),(10,18,205),(8,16,195),(10,18,215)][control]
  plan=launch(hold,shot,.15,takeoff)+[settle(x,6)]
 elif recipe=='terrain-brake':
  c=brake(0);x=d['x'];y=d['top']-18
  c['platforms'][0][2]=d['lip']+160;c['platforms'][1]=[x-60,d['top'],d['width'],65]
  advance,turn=[(105,9),(100,9),(110,9),(105,11)][control]
  plan=[cmd('axis',value=1),wait_x(d['lip']+advance),cmd('shoot',direction=[1,0]),cmd('axis',value=-1,after=turn),settle(x,6)]
 elif recipe=='landing-reload-relay':
  c=thorn(0);c['family']=recipe;front=d['first_front'];top=d['first_top'];second=d['second_front'];endtop=d['second_top'];mid=front+100;x=second+105;y=endtop-18
  c['platforms'][1]=[front,top,220,160];c['platforms'][2][2]=front-220;c['thorns'][0]['length']=front-220
  c['platforms'][4]=[-300,900,2000,70]
  c['platforms'] += [[second,endtop,240,160],[front+260,80,second-front-220,200],[front+280,444,150,90]]
  c['thorns'] += [dict(surface_id='second-upper-slot',platform_index=6,face='bottom',start_offset=0,length=second-front-220,depth=12),dict(surface_id='second-lower-slot',platform_index=7,face='top',start_offset=0,length=150,depth=12)]
  hold,shot,takeoff=[(8,16,205),(10,18,205),(8,16,195),(10,18,215)][control]
  # The midpoint stop follows the original state trigger and actual ground
  # resource renewal. It never sets resources or rebuilds world state.
  plan=launch(hold,shot,.15,takeoff)+[settle(mid,6),ground(),cmd('wait',after=14),cmd('axis',value=1),wait_x(front+185),cmd('jump'),cmd('jump_release',after=8),cmd('shoot',after=8,direction=[-math.sqrt(1-.15**2),.15]),settle(x,6)]
  c['relay_support_index']=1;c['relay_support_id']='Platform1';c['max_frames']=1200
 else:
  c=brake(0);c['family']=recipe;mid=d['pocket_x'];top=d['pocket_top'];x=d['final_front']+100;y=d['final_top']-18
  c['platforms'][0][2]=d['lip']+160;c['platforms'][1]=[mid-60,top,150,65];c['platforms'][2]=[-300,900,2000,60]
  c['platforms'].append([d['final_front'],d['final_top'],240,100])
  advance,turn=[(105,9),(100,9),(110,9),(105,11)][control]
  plan=[cmd('axis',value=1),wait_x(d['lip']+advance),cmd('shoot',direction=[1,0]),cmd('axis',value=-1,after=turn),settle(mid,6),ground(),cmd('wait',after=14),cmd('axis',value=1),wait_x(mid+55),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(x,6)]
  c['relay_support_index']=1;c['relay_support_id']='Platform1';c['max_frames']=1200
 c['id']=id;c['capabilities']=CAPS[:];c['reward_sites']=[];reward(c,x,y,10 if recipe=='terrain-brake'else 12)
 c['rule_parameters']=dict(d,control_candidate=control);c['exit_port']=[x,y];c['goal']=[x-25,y-4,50,8];c['control_plan']=plan;c['max_frames']=max(c.get('max_frames',720),1000);c['trace_all']=False
 c['generation_rule']=dict(id='plains50/terrain/'+recipe,version=1,source_path=str(Path(__file__).relative_to(ROOT.parent)),parameters=c['rule_parameters'],source_type='current_codex_model_rule',novelty='existing relationship adaptation'if recipe in ['terrain-slot','terrain-brake']else'composition hypothesis, independent novelty review required')
 c['idea_ids']=['plains50-terrain/'+recipe];return c

def specification(key):
 d=DEMANDS[key];c=materialize(key)
 if c['family']in ['thorn-slot','brake-under-ledge']:
  s=copy.deepcopy(next(v for v in specifications()if v['required_family']==c['family']))
 else:
  s=copy.deepcopy(next(v for v in specifications()if v['required_family']=='thorn-slot'))
 s.update(id='plains50/terrain/'+key,required_family=c['family'],objective=dict(recipe=d['recipe'],parameters=d,role='practice'if d['recipe']in ['terrain-slot','terrain-brake']else'ground-resource-combination'),entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2600,max_height=1300,max_port_span_x=1600),budget=dict(generator_candidates=4,director_revisions=0),return_conditions='UNKNOWN; only declared forward route validated, no implicit retry teleport/resource reset')
 return s

def compiler(request):
 recipe=request['recipe'];keys=[k for k,d in DEMANDS.items()if d['recipe']==recipe]
 if len(keys)!=2:return dict(status='needs_design',gaps=['no exact bounded recipe'],cases=[])
 specs=[specification(k)for k in keys];cs=[]
 for key,s in zip(keys,specs):
  for control in range(4):
   c=materialize(key,control);c['map_specification']=copy.deepcopy(s);cs.append(c)
 return dict(status='requires_physics',specifications=specs,cases=cs)

def purpose(c,r):
 p=original_purpose(c,r)
 if c['family']in ['landing-reload-relay','pocket-reload-climb']:
  fs=r.get('frames',[]);shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
  between=[f for f in fs if len(shots)>=2 and shots[0]['frame']<f['frame']<shots[1]['frame'] and f.get('grounded')and f.get('support_id')==c['relay_support_id']]
  actual=[f for f in between if f.get('shot_charges',0)>=1]
  p['causal'].update(actual_midpoint_ground_frames=len(between),ground_refill_frames=len(actual),accepted_shot_frames=[f['frame']for f in shots])
  if len(shots)<2 or not actual:p['reasons'].append('no_real_midpoint_ground_refill_chain')
  if c['family']=='pocket-reload-climb':
   lip=c['platforms'][0]
   if not shots or shots[0]['y']-18<=lip[1]+lip[3]:p['reasons'].append('first_brake_not_below_lip')
  p['ok']=not p['reasons']
 return p

def alternatives(c):
 cs=original_alternatives(c)
 if c['family']in ['landing-reload-relay','pocket-reload-climb']:
  for hold in [8,16,24]:
   for dy in [.15,.5,.8660254037844386,1.]:
    v=copy.deepcopy(c);label=f'direct-recoil-{hold}-{dy}';v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=launch(hold,hold+6,dy,205 if c['family']=='landing-reload-relay'else 230)+[settle(c['exit_port'][0],6)];cs.append(v)
 return cs

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--recipes',nargs='+',default=['terrain-slot','terrain-brake','landing-reload-relay','pocket-reload-climb']);a=p.parse_args()
 run(a.name,requests=[dict(recipe=x)for x in a.recipes],cycles=len(a.recipes),compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'protocol-v1.json'])
if __name__=='__main__':main()
