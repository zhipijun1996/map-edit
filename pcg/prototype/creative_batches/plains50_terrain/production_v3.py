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
 'column-low-exit':dict(recipe='under-column-escape',interface=0,wall_x=240,wall_width=16,wall_bottom=400,final_front=410,final_top=540),
 'column-wide-turn':dict(recipe='under-column-escape',interface=1,wall_x=260,wall_width=20,wall_bottom=420,final_front=440,final_top=570),
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
  plan=launch(hold,shot,.15,takeoff)+[wait_x(mid-20),cmd('axis',value=0),ground(),cmd('wait',after=14),cmd('axis',value=1),wait_x(front+185),cmd('jump'),cmd('jump_release',after=8),cmd('shoot',after=8,direction=[-math.sqrt(1-.15**2),.15]),settle(x,6)]
  c['relay_support_index']=1;c['relay_support_id']='Platform1';c['max_frames']=1200
 else:
  c=base(id);c['family']=recipe;wall=d['wall_x'];width=d['wall_width'];bottom=d['wall_bottom'];x=d['final_front']+100;y=d['final_top']-18
  c['platforms']=[[-160,180,wall+120,100],[wall,-500,width,bottom+500],[d['final_front'],d['final_top'],240,120],[-300,1000,2000,60]]
  c['spawn']=[80,162];c['entry_port']=[80,162]
  offset,dy=[(13,.8660254037844386),(17,.8660254037844386),(13,.7),(17,.7)][control]
  plan=[cmd('axis',value=1),wait_x(wall+width+offset),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),settle(x,6)]
  c['max_frames']=1000
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
 s.update(id='plains50/terrain/'+key,required_family=c['family'],objective=dict(recipe=d['recipe'],parameters=d,role='practice'if d['recipe']in ['terrain-slot','terrain-brake']else'ground-resource-combination'),entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2600,max_height=1800,max_port_span_x=1600),budget=dict(generator_candidates=4,director_revisions=0),return_conditions='UNKNOWN; only declared forward route validated, no implicit retry teleport/resource reset')
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
 check_case=copy.deepcopy(c)
 if c['family']=='landing-reload-relay':check_case['family']='thorn-slot'
 p=original_purpose(check_case,r)
 if c['family']=='landing-reload-relay':
  fs=r.get('frames',[]);shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
  between=[f for f in fs if len(shots)>=2 and shots[0]['frame']<f['frame']<shots[1]['frame'] and f.get('grounded')and f.get('support_id')==c['relay_support_id']]
  actual=[f for f in between if f.get('shot_charges',0)>=1]
  p['causal'].update(actual_midpoint_ground_frames=len(between),ground_refill_frames=len(actual),accepted_shot_frames=[f['frame']for f in shots])
  if len(shots)<2 or not actual:p['reasons'].append('no_real_midpoint_ground_refill_chain')
  p['ok']=not p['reasons']
 if c['family']=='under-column-escape':
  fs=r.get('frames',[]);wall=c['platforms'][1];shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
  below_pass=[f for f in fs if f['x']+12>=wall[0] and f['x']-12<=wall[0]+wall[2] and f['y']-18>=wall[1]+wall[3]-.1]
  valid=bool(shots and not shots[0]['grounded'] and shots[0]['y']-18>=wall[1]+wall[3]-.1 and below_pass)
  p['causal'].update(shot_after_body_clears_column=bool(shots and shots[0]['x']-12>=wall[0]+wall[2]),shot_below_column_base=valid,below_column_body_frames=len(below_pass),shot_position=[shots[0]['x'],shots[0]['y']]if shots else None,body_size=[24,36])
  if not valid:p['reasons'].append('not_a_below_column_late_escape')
  p['ok']=not p['reasons']
 return p

def alternatives(c):
 cs=original_alternatives(c)
 if c['family']=='under-column-escape':
  wall=c['platforms'][1]
  for x in [160,wall[0]-45,wall[0]+2,wall[0]+wall[2]+8]:
   for dy in [0.,.8660254037844386]:
    v=copy.deepcopy(c);label=f'early-or-horizontal-{x}-{dy}';v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=[cmd('axis',value=1),wait_x(x),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)];cs.append(v)

 if c['family']=='landing-reload-relay':
  for hold in [8,16,24]:
   for dy in [.15,.5,.8660254037844386,1.]:
    v=copy.deepcopy(c);label=f'direct-recoil-{hold}-{dy}';v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=launch(hold,hold+6,dy,205 if c['family']=='landing-reload-relay'else 230)+[settle(c['exit_port'][0],6)];cs.append(v)
 return cs

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--recipes',nargs='+',default=['terrain-slot','terrain-brake','landing-reload-relay','under-column-escape']);a=p.parse_args()
 run(a.name,requests=[dict(recipe=x)for x in a.recipes],cycles=len(a.recipes),compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'protocol-v1.json'])
if __name__=='__main__':main()
