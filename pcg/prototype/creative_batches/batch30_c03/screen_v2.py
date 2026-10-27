import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import rules_v2 as rules
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[];clean=[]
 cs=[rules.candidate(0,k,route)for route in ['air','staged']for k in range(4)]
 for c,r,e in engine.run(cs,'core-clean'):
  q=rules.purpose(c,r);row=dict(case=c,result=r,purpose=q,evidence=e);rows.append(row)
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],min_y=min((f['y']for f in r.get('frames',[])),default=None),shots=r.get('shots'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 for c,r,e in engine.run([instantiate(c,261031101,l,k)for c in clean for l in ['mild','moderate']for k in range(6)],'core-perturb'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'screen-results.json',rows)
 selected={}
 for route in ['air','staged']:
  scored=[]
  for c in clean:
   if c['route_spec']['id']!=route:continue
   rates={l:sum(x['purpose']['ok']for x in rows if x['case']['id'].startswith(c['id']+'-'+l+'-'))for l in ['mild','moderate']}
   if rates['mild']>=5:scored.append((-min(rates.values()),-sum(rates.values()),c['rule_parameters']['control']))
  if scored:selected[route]=min(scored)[2]
 write(engine.out/'selection.json',dict(controls=selected,holdout_used=False))
 print(json.dumps(dict(selection=selected)),flush=True)
if __name__=='__main__':main()
