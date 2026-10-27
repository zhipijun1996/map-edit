import argparse,json
from pathlib import Path
from . import api_v1 as api
from . import recovery_v3 as prior
from .probe_v2 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def failed_selector():
 c=prior.failed_selector();c['id']+='-lateral-after8';c['control_plan'][-2]['trigger']['after']=8;c['control_plan'][-1]['trigger']['after']=0;return c
purpose=prior.purpose
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v4.json',HERE/'recovery_v3.py',HERE/'recovery_v2.py',HERE/'recovery_v1.py',HERE/'probe_v2.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];good=False;c=failed_selector()
 for case,r,e in engine.run([c],'real-recovery-lateral-clean'):
  q=purpose(case,r);good=q['ok'];rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),pillar=q['causal'].get('pillar_frames'))),flush=True)
 if good:
  for case,r,e in engine.run([instantiate(c,261031201,l,k)for l in ['mild','moderate']for k in range(6)],'real-recovery-lateral-perturb'):
   q=purpose(case,r);rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,total=196+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
