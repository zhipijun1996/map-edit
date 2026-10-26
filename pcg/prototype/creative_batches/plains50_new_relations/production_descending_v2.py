"""D02 repaired bank sightline, fixed second geometry revision; original loop."""
import copy,argparse
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.probe_v2 import descent2
from pcg.prototype.creative_batches.plains50_new_relations.production_v1 import specification
from pcg.prototype.creative_batches.descending_carrier.counters_v1 import alternatives as old_alternatives
from pcg.prototype.workshop.counterexamples import alternatives as generic_alternatives
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.rules import cmd,wait_x,settle
HERE=Path(__file__).parent

def compiler(request):
 cs=[];ss=[]
 for v in [0,1]:
  source=descent2(v);source['rule_parameters'].update(interface=v,relationship='supported diagonal descent: regulate relative position under roof and depart before losing height')
  s=specification(source,v);s['risk_reward']['amount']=8;ss.append(s)
  for retreat in [295,305]:
   c=copy.deepcopy(source);c['id']=f'p50-descent-i{v}-r{retreat}';c['control_plan'][6]=wait_x(retreat,-1);c['production_recipe']='descending-carrier';c['map_specification']=s;c['idea_ids']=['PR-D02'];c['generation_rule']=dict(id='plains50-new/descending-carrier',version=2,source_type='current_codex_subagent',parameters=c['rule_parameters']);cs.append(c)
 return dict(status='requires_physics',specifications=ss,cases=cs)

def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<8:why.append('reward_not_claimed')
 moving=[];neutral=[]
 for f in fs:
  if f.get('support_id')!='descending-deck':continue
  p=next((p for p in f.get('moving_platforms',[])if p['id']=='descending-deck'),None)
  if p and p.get('physics_velocity',[0,0])[1]>10:
   moving.append(f)
   if abs(f.get('axis',0))<.01:neutral.append(f)
 drop=max((f['y']for f in moving),default=0)-min((f['y']for f in moving),default=0)
 if len(moving)<24 or drop<120:why.append('moving_descent_support_bypassed')
 xs=[f for f in fs if 548<f['x']<732];clear=min((f['y']-18-410 for f in xs),default=None)
 if clear is None or clear<-.1:why.append('body_roof_clearance_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=dict(moving_supported_frames=len(moving),moving_supported_drop=drop,neutral_supported_frames=len(neutral),body_roof_clearance=clear))

def alternatives(c):
 out=generic_alternatives(c)
 for source in old_alternatives():
  d=copy.deepcopy(c);d['id']+='-counter-'+source['counterexample_kind'];d['counterexample_kind']=source['counterexample_kind'];d['control_plan']=copy.deepcopy(source['control_plan']);out.append(d)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-plains50-new-descending-production-v2');a=p.parse_args()
 run(a.name,requests=[dict(recipe='descending-carrier')],cycles=1,compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'probe_v2.py',HERE/'probe_v1.py',HERE/'production_v1.py',Path('pcg/prototype/creative_batches/descending_carrier/counters_v1.py').resolve()])
