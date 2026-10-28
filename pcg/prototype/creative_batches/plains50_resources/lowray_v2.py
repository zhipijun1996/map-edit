"""Second geometry revision: occluded low-ray late recoil; distinct from unimplemented scarce-enemy D03."""
import argparse,copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent
RECIPE='low-ray-recoil-return'
def candidates(interface):
 out=[]
 for delay in [34,36,38,40]:
  c=base(f'p50-resource-lowray-v2-i{interface}-d{delay}');c['family']=RECIPE;c['production_recipe']=RECIPE
  pocket_y,wall_bottom,exit_x=(520,500,405)if interface==0 else(570,540,430)
  c['platforms']=[[-160,180,400,100],[320,pocket_y,220,80],[-400,990,1700,70],[200,280,40,wall_bottom-280]]
  c['spawn']=[180,162];c['entry_port']=[180,162]
  c['latches']=[dict(id='low-return-key',bell=[80,820],gate=[320,280,220,pocket_y-280],open_seconds=0)]
  c['rule_parameters']=dict(relationship='commit below opaque side lip to expose low projectile ray; same shot opens side pocket and recoils upward to recover it',pocket_y=pocket_y,wall_bottom=wall_bottom,low_bell=[80,820],landing_x=exit_x)
  reward(c,exit_x,pocket_y-18,14)
  finish(c,exit_x,pocket_y-18,[cmd('axis',value=1),wait_x(265),cmd('axis',value=0),cmd('wait',delay),cmd('shoot',aim_cell=dict(kind='bell',id='low-return-key')),settle(exit_x,6)])
  c['interface']=interface;c['max_frames']=900;c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule'].update(source_type='current_codex_subagent_authored_proposal',author_task='/root/plains50_resources');out.append(c)
 return out

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))];opens=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open']
 below=bool(shots and shots[0]['y']-18>c['platforms'][0][1]+c['platforms'][0][3]);rise=bool(shots and any(f['y']<shots[0]['y']-30 for f in fs if f['frame']>shots[0]['frame']))
 p['causal'].update(shot_body_below_entry_lip=below,recoil_recovery_rise=rise,gate_open=bool(opens))
 if not(below and rise and opens):p['reasons'].append('low_ray_then_upward_recovery_missing')
 p['causal']['side_wall_full_body_clearance_not_required']=True
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=original_alternatives(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 target=c['exit_port'][0]
 for x in [80,180,220,245,265]:
  for delay in [0,18,30]:
   add(f'pre-ray-{x}-{delay}',[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',delay,aim_cell=dict(kind='bell',id='low-return-key')),settle(target,6)])
 for hold in [8,20,30]:add(f'over-lip-{hold}',[cmd('axis',value=1),wait_x(200),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,aim_cell=dict(kind='bell',id='low-return-key')),settle(target,6)])
 return out

def specification(i):
 c=candidates(i)[0]
 return dict(schema='map-notes/challenge-specification/v1',id=f'plains50/resources/{RECIPE}/i{i}',region='plains',required_family=RECIPE,objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2400,max_height=1800,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=14,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(req):
 specs=[specification(i)for i in [0,1]];cs=[]
 for i,s in enumerate(specs):
  for c in candidates(i):c['map_specification']=s;c['idea_ids']=['plains50/resources/low-ray-recoil-return/v2'];cs.append(c)
 return dict(status='requires_physics',specifications=specs,cases=cs)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe','produce']);p.add_argument('--name',required=True);a=p.parse_args()
 if a.mode=='produce':run(a.name,[dict(recipe=RECIPE)],1,library_root=ROOT/'map_directed/library',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__))
 else:
  engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]);rows=[]
  for c,r,e in engine.run([c for i in [0,1]for c in candidates(i)],'probe'):
   p=purpose(c,r);rows.append(dict(case=c,result=r,purpose=p,evidence=e));print(c['id'],r['reason'],p['ok'],p['causal'],flush=True)
  (engine.out/'probe-results.json').write_text(json.dumps(rows))
if __name__=='__main__':main()
