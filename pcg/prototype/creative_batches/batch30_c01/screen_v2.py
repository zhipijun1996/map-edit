import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import rules_v2 as rules
from .alternatives_v1 import alternatives
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'alternatives_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 cs=[instantiate(rules.candidate(0,k),261031001,'mild',i)for k in [1,2,3]for i in range(6)]
 for c,r,e in engine.run(cs,'mild-core'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],landing=q['causal']['first_landing'])),flush=True)
 write(engine.out/'screen-results.json',rows)
 scores={k:sum(x['purpose']['ok']for x in rows if f'-c{k}-'in x['case']['id'])for k in [1,2,3]};selected=min(scores,key=lambda k:(-scores[k],k))
 write(engine.out/'control-selection.json',dict(scores=scores,selected=selected,before_counterexample_execution=True))
 ctr=[]
 for c,r,e in engine.run(alternatives(rules.candidate(0,selected)),'cheap-counter'):
  q=rules.purpose(c,r);same=bool(r.get('ok'))and r.get('workshop',{}).get('coins',0)>=12 and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
  ctr.append(dict(case=c,result=r,purpose=q,evidence=e,same_external_outcome=same,invalidates_design=same and not q['ok']));print(json.dumps(dict(counter=c['counterexample_kind'],same=same,purpose=q['ok'],shots=r.get('shots'),reason=r.get('reason'))),flush=True)
 write(engine.out/'counter-results.json',ctr)
if __name__=='__main__':main()
