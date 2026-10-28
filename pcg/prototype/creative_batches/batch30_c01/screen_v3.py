import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import rules_v3 as rules
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 cs=[rules.candidate(i,k)for i in [0,1]for k in range(4)]
 expanded=[instantiate(c,261031001,l,j)for c in cs for l,n in [('clean',1),('mild',6),('moderate',6)]for j in range(n)]
 for c,r,e in engine.run(expanded,'two-space-screen'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],landing=q['causal']['first_landing'])),flush=True)
 write(engine.out/'screen-results.json',rows)
 selected={};scores=[]
 for interface in [0,1]:
  ranked=[]
  for control in range(4):
   subset=[x for x in rows if x['case']['interface']==interface and x['case']['rule_parameters']['control']==control]
   rate={l:sum(x['purpose']['ok']for x in subset if '-'+l+'-'in x['case']['id'])for l in ['clean','mild','moderate']}
   scores.append(dict(interface=interface,control=control,successes=rate));
   if rate['clean']and rate['mild']>=5:ranked.append((-min(rate['mild'],rate['moderate']),-rate['mild']-rate['moderate'],control))
  if ranked:selected[interface]=min(ranked)[2]
 write(engine.out/'control-selection.json',dict(scores=scores,selected=selected,holdout_run=False))
 print(json.dumps(dict(selection=selected,scores=scores)),flush=True)
if __name__=='__main__':main()
