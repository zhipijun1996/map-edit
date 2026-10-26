import argparse,json
from pathlib import Path
from . import rules_v7 as rules
from .probe_v1 import report
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interface',type=int,choices=[0,1],default=0);p.add_argument('--control',type=int,choices=[0,1,2,3],default=0);p.add_argument('--level',choices=['clean','mild','moderate','counters','comparisons'],default='clean');p.add_argument('--trials',type=int,default=6);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),HERE/'probe_v1.py']+rules.SOURCE_DEPENDENCIES);rows=[]
 selected=['west-air','east-then-dead-west','both-rewards-exit']+(['west-staged']if a.level=='clean'else[])
 bases=[c for c in rules.layouts(rules.RECIPES[0],a.interface,a.control)if c['route_spec']['id']in selected]
 if a.level=='comparisons':cs=rules.depleted_comparisons(rules.RECIPES[0],a.interface,a.control)
 elif a.level=='counters':cs=[v for c in bases if c['route_spec']['id']=='west-air'for v in rules.alternatives(c)if v['counterexample_kind'].startswith('omit-shot-')]
 else:cs=[instantiate(c,261026930,a.level,j)for c in bases for j in range(1 if a.level=='clean'else a.trials)]
 for c,r,ev in e.run(cs,'bounded-v7-'+a.level):
  row=report(c,r,ev);row['purpose']=rules.purpose(c,r);rows.append(row);print(json.dumps(dict(id=c['id'],ok=row['purpose']['ok'],reason=r.get('reason'),purpose=row['purpose'],evidence=ev)),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),rows=[dict(id=x['case']['id'],purpose=x['purpose'],safe_stable=x['result'].get('ok'),evidence=x['evidence'])for x in rows]))
