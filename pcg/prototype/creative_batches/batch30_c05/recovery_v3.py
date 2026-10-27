import argparse,json
from pathlib import Path
from . import api_v1 as api
from . import recovery_v2 as prior
from .probe_v2 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def failed_selector():
 c=prior.failed_selector(20);c['id']+='-horizontal-real-miss'
 for q in c['control_plan']:
  if q['op']=='shoot'and q.get('direction')==[-.95,(1-.95*.95)**.5]:q['direction']=[-1,0];break
 return c
purpose=prior.purpose
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v3.json',HERE/'recovery_v2.py',HERE/'recovery_v1.py',HERE/'probe_v2.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];good=False;c=failed_selector()
 for case,r,e in engine.run([c],'real-horizontal-miss-clean'):
  q=purpose(case,r);good=q['ok'];rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),pillar=q['causal'].get('pillar_frames'),last={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 if good:
  for case,r,e in engine.run([instantiate(c,261031201,l,k)for l in ['mild','moderate']for k in range(6)],'real-horizontal-miss-perturb'):
   q=purpose(case,r);rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,total=195+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
