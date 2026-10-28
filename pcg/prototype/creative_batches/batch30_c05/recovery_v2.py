import argparse,json
from pathlib import Path
from . import api_v1 as api
from . import recovery_v1 as prior
from .probe_v2 import compact
from pcg.prototype.workshop.rules import cmd,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def failed_selector(wait=20):
 c=prior.failed_selector(wait);c['id']+='-original-ground-condition'
 for i,q in enumerate(c['control_plan']):
  if q.get('trigger',{}).get('dynamic',{}).get('id')=='Platform4':c['control_plan'][i:i+1]=[cmd('wait',90),ground()];break
 return c
purpose=prior.purpose
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v2.json',HERE/'recovery_v1.py',HERE/'probe_v2.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];clean=[]
 for c,r,e in engine.run([failed_selector(w)for w in [20,40,60]],'original-ground-clean'):
  q=purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),pillar=q['causal'].get('pillar_frames'),last={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 selected=clean[:1];write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in selected],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031201,l,k)for c in selected for l in ['mild','moderate']for k in range(6)],'original-ground-perturb'):
  q=purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
