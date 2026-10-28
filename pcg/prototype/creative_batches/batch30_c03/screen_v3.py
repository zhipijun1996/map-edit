import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import rules_v3 as rules
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[];clean=[]
 cs=[rules.candidate(i,k,'air')for i in [0,1]for k in range(4)]+[rules.candidate(i,1,'staged')for i in [0,1]]
 for c,r,e in engine.run(cs,'two-space-clean'):
  q=rules.purpose(c,r);row=dict(case=c,result=r,purpose=q,evidence=e);rows.append(row)
  if q['ok']:clean.append(row)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],min_y=min((f['y']for f in r.get('frames',[])),default=None),air=q['causal'].get('air_shot_frames'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 selected=[];selection={}
 for i in [0,1]:
  good=[v for v in clean if v['case']['interface']==i and v['case']['route_spec']['id']=='air']
  def score(v):
   fs=v['result']['frames'];air=v['purpose']['causal']['air_shot_frames'];margin=v['case']['exit_port'][1]-min(f['y']for f in fs);timing=(air[-1]-air[-2]-16)*10
   return (-min(margin,timing),v['case']['rule_parameters']['control'])
  if good:
   w=min(good,key=score);selected.append(w['case']);selection[str(i)]=dict(air=w['case']['rule_parameters']['control'],score=-score(w)[0])
  stage=next((v['case']for v in clean if v['case']['interface']==i and v['case']['route_spec']['id']=='staged'),None)
  if stage:selected.append(stage);selection.setdefault(str(i),{})['staged']=1
 write(engine.out/'selection-before-perturb.json',dict(controls=selection,holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031101,l,k)for c in selected for l in ['mild','moderate']for k in range(6)],'selected-perturb'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'screen-results.json',rows)
 print(json.dumps(dict(selection=selection,actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
