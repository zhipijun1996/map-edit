"""Six actual new spatial adaptations of three existing plains causal rules.

Uses original producer, runner, regular policy and persistent library. No new
simulation or online model service. Each interface is a supplied spatial demand.
"""
import argparse,copy,json
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent
LEGACY=HERE.parent/'resource_routes'
RECIPES=['sightline-backtrack','trapdoor-commit','ordered-target-transaction']

def candidates(recipe,interface):
 out=[]
 for k in range(4):
  c=base(f'p50-resource-{recipe}-i{interface}-c{k}');c['production_recipe']=recipe;c['family']=recipe
  c['max_frames']=1000;c['trace_all']=False
  if recipe=='sightline-backtrack':
   # Interface0: long westward exit behind narrow occluder. Interface1:
   # wider occluder and nearer but more easterly observation station.
   left,screen_width,bell_x,peek=(-455,100,440,370)if interface==0 else(-365,150,480,410)
   c['platforms']=[[-520,438,1220,100],[140,-500,screen_width,890],[-310,-600,30,900]]
   c['latches']=[dict(id='remote-key',bell=[bell_x,245],gate=[-310,300,30,138],open_seconds=0)]
   c['rule_parameters']=dict(relationship='leave exit direction to expose remote shot ray, permanently unlock west route, then backtrack',screen=c['platforms'][1],peek_x=peek,exit_x=left)
   reward(c,left,420,12)
   p=[cmd('axis',value=1),wait_x(peek),cmd('axis',value=0),cmd('shoot',4+k*2,aim_cell=dict(kind='bell',id='remote-key')),settle(left,14)]
   finish(c,left,420,p);c['exit_normal']=[-1,0]
  elif recipe=='trapdoor-commit':
   width,drop=(210,340)if interface==0 else(230,220)
   right=240+width;low_y=438+drop;goal_x=240+width/2
   c['platforms']=[[-160,438,400,310],[right,438,430,310],[180,-500,120,890],[240,low_y,width,70]]
   c['latches']=[dict(id='bridge-key',bell=[390 if interface==0 else 410,245],gate=[240,438,width,20],open_seconds=0)]
   c['rule_parameters']=dict(relationship='open own real support bridge and commit into lower reward route',bridge=c['latches'][0]['gate'],shaft_drop=drop,lower_width=width)
   reward(c,goal_x,low_y-18,14)
   p=[cmd('axis',value=1),wait_x(goal_x-10+k*6),cmd('axis',value=0),cmd('shoot',4,aim_cell=dict(kind='bell',id='bridge-key')),settle(goal_x,6)]
   finish(c,goal_x,low_y-18,p)
  elif recipe=='ordered-target-transaction':
   x,y,w,target=(310,280,220,410)if interface==0 else(320,310,220,420)
   c['platforms'] += [[x,y,w,70],[-400,820,1550,60]]
   c['latches']=[dict(id='resource-order',bell=[20,350],gate=[x-10,-500,24,y+500],open_seconds=0,sequence_offset=[120,80])]
   c['rule_parameters']=dict(relationship='two simultaneously visible projectile receivers commit noncommuting persistent gate state; partial first progress remains',first=[20,350],second=[140,430],landing=[x,y,w,70],both_entry_visible=True)
   reward(c,target,y-18,16)
   hold=12+k*2;shot=18+k*2
   p=[cmd('shoot',aim_cell=dict(kind='bell',id='resource-order')),cmd('axis',value=1,after=20),wait_x(140),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot-hold,aim_cell=dict(kind='bell',id='resource-order',receiver='second')),settle(target,6)]
   finish(c,target,y-18,p)
  else:raise ValueError('unregistered_rule')
  c['interface']=interface;c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule'].update(source_type='current_codex_subagent_authored_recipe',author_task='/root/plains50_resources',version=1)
  out.append(c)
 return out

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);recipe=c['production_recipe'];events=r.get('plains',{}).get('events',[])
 opens=[e for e in events if e['type']=='bell_open'];shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
 if recipe=='sightline-backtrack':
  hit=opens[0]['frame']if opens else None;screen=c['platforms'][1];right=screen[0]+screen[2]
  exposed=any(f['x']>right for f in fs if hit is not None and f['frame']<=hit);returned=any(f['x']<-310 for f in fs if hit is not None and f['frame']>hit)
  p['causal'].update(opened=hit,exposed=exposed,returned=returned)
  if not(hit is not None and exposed and returned):p['reasons'].append('remote_exposure_backtrack_missing')
 elif recipe=='trapdoor-commit':
  hit=opens[0]['frame']if opens else None;floor=c['latches'][0]['gate'][1]
  dropped=bool(hit is not None and any(not f['grounded']and f['y']>floor+32 for f in fs if f['frame']>hit))
  # Air opening is a valid same-cause alternative; do not force grounded input.
  p['causal'].update(real_bridge_open=hit,descended_into_shaft=dropped)
  if not(hit is not None and dropped):p['reasons'].append('self_support_route_commit_missing')
 else:
  primed=any(any(b.get('sequence_step')==1 and not b.get('open')for b in f.get('plains',{}).get('bells',[]))for f in fs)
  p['causal'].update(real_partial_progress=primed,real_final_gate_open=bool(opens))
  if not(primed and opens):p['reasons'].append('noncommuting_target_state_missing')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=original_alternatives(c)
 def add(name,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+name;v['counterexample_kind']=name;v['control_plan']=plan;out.append(v)
 rec=c['production_recipe'];target=c['exit_port'][0];bell=c['latches'][0]['id']
 if rec=='sightline-backtrack':
  for hold in [8,20,30]:add(f'direct-left-jump-{hold}',[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',hold),settle(target,10)])
  for x in [80,110,130]:
   for delay in [8,18]:add(f'early-jump-ray-{x}-{delay}',[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',12),cmd('shoot',delay,aim_cell=dict(kind='bell',id=bell)),settle(target,18)])
  for delay in [0,12,30]:add(f'ground-preopen-{delay}',[cmd('shoot',delay,aim_cell=dict(kind='bell',id=bell)),settle(target,18)])
 elif rec=='trapdoor-commit':
  for x in [180,220,235,260,290]:add(f'preopen-{x}',[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',4,aim_cell=dict(kind='bell',id=bell)),settle(target,18)])
  for hold in [8,20,30]:add(f'air-open-{hold}',[cmd('axis',value=1),wait_x(200),cmd('jump'),cmd('jump_release',hold),cmd('shoot',10,aim_cell=dict(kind='bell',id=bell)),settle(target,18)])
 else:
  for i in range(6):
   plan=copy.deepcopy(c['control_plan']);plan[0]['aim_cell']['receiver']='second';plan[5]['aim_cell'].pop('receiver',None);plan[4]=cmd('jump_release',8+i*4);add(f'wrong-first-{i}',plan)
  for delay in [8,20,30]:add(f'both-ground-{delay}',[cmd('shoot',aim_cell=dict(kind='bell',id=bell)),cmd('shoot',delay,aim_cell=dict(kind='bell',id=bell,receiver='second')),cmd('axis',value=1),wait_x(140),cmd('jump'),cmd('jump_release',20),settle(target,6)])
  for delay in [18,30,45]:
   add(f'correct-ground-plus-air-{delay}',[cmd('shoot',aim_cell=dict(kind='bell',id=bell)),cmd('shoot',delay,aim_cell=dict(kind='bell',id=bell,receiver='second')),cmd('axis',value=1,after=18),wait_x(140),cmd('jump'),cmd('jump_release',16),cmd('shoot',8,direction=[-.5,.8660254037844386]),settle(target,6)])
   add(f'wrong-then-recover-{delay}',[cmd('shoot',aim_cell=dict(kind='bell',id=bell,receiver='second')),cmd('shoot',delay,aim_cell=dict(kind='bell',id=bell)),cmd('axis',value=1,after=20),wait_x(140),cmd('jump'),cmd('jump_release',16),cmd('shoot',8,aim_cell=dict(kind='bell',id=bell,receiver='second')),settle(target,6)])
 return out

def specification(recipe,i):
 c=candidates(recipe,i)[0]
 return dict(schema='map-notes/challenge-specification/v1',id=f'plains50/resources/{recipe}/i{i}',region='plains',required_family=recipe,objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],c.get('exit_normal',[1,0])]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2300,max_height=1800,max_port_span_x=1100),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=c['reward_sites'][0]['amount'],mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))

def compiler(request):
 recipe=request['recipe'];specs=[specification(recipe,i)for i in [0,1]];cs=[]
 for i,spec in enumerate(specs):
  for c in candidates(recipe,i):c['map_specification']=spec;c['idea_ids']=[f'plains50/resources/{recipe}/v1'];cs.append(c)
 return dict(status='requires_physics',specifications=specs,cases=cs)

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe','produce']);p.add_argument('--name',required=True);p.add_argument('--recipes',nargs='+',choices=RECIPES,default=RECIPES);a=p.parse_args()
 extra=[HERE/'protocol-v1.json',LEGACY/'runner-v2.gd',LEGACY/'export-v4.mjs']
 if a.mode=='produce':run(a.name,[dict(recipe=r)for r in a.recipes],len(a.recipes),library_root=ROOT/'map_directed/library',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extra,runner_script=LEGACY/'runner-v2.gd',export_script=LEGACY/'export-v4.mjs')
 else:
  engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+extra,runner_script=LEGACY/'runner-v2.gd');rows=[]
  for c,r,e in engine.run([c for rec in a.recipes for i in [0,1]for c in candidates(rec,i)],'probe'):
   check=purpose(c,r);rows.append(dict(case=c,result=r,purpose=check,evidence=e));print(c['id'],r['reason'],check['ok'],check['reasons'],flush=True)
  (engine.out/'probe-results.json').write_text(json.dumps(rows))
if __name__=='__main__':main()
