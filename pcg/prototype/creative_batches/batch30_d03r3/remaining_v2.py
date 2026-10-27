"""Single-engine61-case remainder. Compact receipts, originalgzipraw holds frames."""
import json
from pathlib import Path
from . import rules_v2 as rules,counter_recipes_v1 as counters
from .screen_v2 import shot_geometry
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03r3-remainder-v2',extra_sources=[Path(__file__),Path(rules.__file__),Path(counters.__file__),HERE/'screen_v2.py',HERE/'remaining-protocol-v1.json']+rules.SOURCE_DEPENDENCIES);cs=[];rows=[]
 for i in(0,1):
  cases=rules.layouts(rules.RECIPES[0],i,0)
  if i==1:cs += [instantiate(c,261032001,'mild',j)for c in cases if c['route_spec']['id']in['east-air','west-air']for j in range(4)]
  cs += [instantiate(c,261032001,'moderate',j)for c in cases if c['route_spec']['id']in['east-staged','west-staged','main']for j in range(4)]
  cs += [instantiate(c,261032001,'mild',j)for c in cases if c['route_spec']['id']in['east-then-dead-west','both-rewards-exit']for j in range(2)]
  cs += counters.depleted_comparisons(rules.RECIPES[0],i,0)
  west=next(c for c in cases if c['route_spec']['id']=='west-air')
  cc=counters.alternatives(west)[13:]
  cs += cc if i==0 else[c for c in cc if c['counterexample_kind']in['ground-clear3-perch-50','live-perch-50-shot1']]
 assert len(cs)==61,len(cs)
 for c,r,ev in e.run(cs,'bounded-r3-remainder'):
  fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[]);shots=[f for f in fs if any(a['type']=='shot'for a in f.get('accepted',[]))];perch=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform8'];branch=next((x for x in r.get('fired_commands',[])if x['index']==c.get('comparison_branch_plan_index',-1)),None)
  row=dict(id=c['id'],interface=c['interface'],route_spec=c['route_spec'],counter_kind=c.get('counterexample_kind'),comparison_only=c.get('comparison_only',False),purpose=rules.purpose(c,r),shot_geometry=shot_geometry(r),evidence=ev,result_summary={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks','returns']},world_observations=dict(enemy_final=r.get('plains',{}).get('enemies'),perch_supported_frames=len(perch),first_perch_support=({k:perch[0].get(k)for k in ['frame','x','y','shot_charges']}if perch else None),ground_shots=sum(f.get('grounded',False)for f in shots),actual_enemy_hits=[{k:x.get(k)for k in ['frame','shot_id','player_airborne','fired_airborne']}for x in events if x['type']=='enemy_hit'],actual_claimed_rewards=sorted({x['id']for x in r.get('workshop',{}).get('events',[])if x.get('type')=='chest_claim'and x.get('accepted')}),branch_boundary=branch,last_body=({k:fs[-1].get(k)for k in ['frame','x','y','grounded','support_id','shot_charges']}if fs else None)))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows),rows=rows))
