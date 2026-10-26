"""State comparison only: v6 geometry + v7 safe return, no manual kill.

This is NOT a new generation rule or a production admission witness. It probes
whether one naturally remaining HP changes the later air/staged choice.
"""
import copy,json
from pathlib import Path
from . import rules_v6,rules_v7
from .probe_v1 import report
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03-c2-comparison-v1',extra_sources=[Path(__file__),Path(rules_v6.__file__),Path(rules_v7.__file__),HERE/'probe_v1.py']+rules_v7.SOURCE_DEPENDENCIES);rows=[];cases=[]
 geometry=next(c for c in rules_v6.layouts(rules_v6.RECIPES[0],0,0)if c['route_spec']['id']=='east-then-dead-west')
 for original in rules_v7.depleted_comparisons(rules_v7.RECIPES[0],0,0):
  c=copy.deepcopy(geometry);c['id']='b30-d03-state-comparison-v1-'+original['purpose_kind'];c['control_plan']=original['control_plan'];c['purpose_kind']=original['purpose_kind'];c['comparison_kind']='two-east-hits-then-one-HP-real-choice';c['generation_rule']=dict(id='D03-state-comparison-only',version=1,source_path=str(Path(__file__)),production_eligible=False);cases.append(c)
 for c,r,ev in e.run(cases,'remaining-HP-same-world'):
  row=report(c,r,ev);fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[]);hits=[h for h in events if h['type']=='enemy_hit'];first_west_jump=next((f['frame']for f in fs if f['frame']>200 and any(x['type']=='ground_jump'for x in f.get('accepted',[]))),None)
  row['comparison']=dict(kind=c['purpose_kind'],safe_stable=r.get('ok'),actual_rewards=sorted({x['id']for x in r.get('workshop',{}).get('events',[])if x.get('type')=='chest_claim'and x.get('accepted')}),enemy_hits=[dict(frame=x['frame'],fired_airborne=x.get('fired_airborne'),player_airborne=x.get('player_airborne'))for x in hits],enemy_final=r.get('plains',{}).get('enemies'),first_west_jump=first_west_jump,production_eligible=False)
  rows.append(row);print(json.dumps(row['comparison']),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,production_eligible=False,comparisons=[v['comparison']for v in rows]))
