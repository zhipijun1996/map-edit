import argparse,json
from pathlib import Path
from . import rules_v4 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
def compact(c,r,e,q):
 return dict(case=c,purpose=q,evidence=e,actual=dict(ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),enemies=r.get('plains',{}).get('enemies'),coins=r.get('workshop',{}).get('coins'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['frame','x','y','support_id']},shots_at=[{k:f.get(k)for k in ['frame','x','y','grounded','shot_charges']}for f in r.get('frames',[])if any(v.get('type')=='shot'for v in f.get('accepted',[]))]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[];clean=[]
 for c,r,e in engine.run([rules.candidate(k)for k in range(4)],'staged-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'))),flush=True)
 selected=clean[:2]
 write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in selected],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031101,l,k)for c in selected for l in ['mild','moderate']for k in range(6)],'staged-perturb'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'repair-results.json',rows)
 scored=[]
 for c in selected:
  stats={l:sum(x['purpose']['ok']for x in rows if x['case']['id'].startswith(c['id']+'-'+l+'-'))for l in ['mild','moderate']}
  if stats['mild']>=5 and stats['moderate']>=4:scored.append((-min(stats.values()),-sum(stats.values()),c['rule_parameters']['control_repair']))
 winner=min(scored)[2]if scored else None
 write(engine.out/'control-selection.json',dict(control=winner,selection_frozen_before_full=True,holdout_used=False,actual_cases=engine.sim.cases));print(json.dumps(dict(winner=winner,actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
