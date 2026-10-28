import argparse,json
from pathlib import Path
from . import recovery_v1 as prior
from . import rules_v3 as rules
from .probe_v1 import compact
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def candidate():
 c=prior.candidate(0);c['id']+='-edge-jump-repair'
 c['control_plan']=c['control_plan'][:11]+[settle(760),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),cmd('wait',8),settle(820),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),settle(650,8)]
 return c
purpose=prior.purpose
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();rows=[];good=False
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v2.json',HERE/'verification-protocol-v1.json',HERE/'recovery_v1.py',HERE/'probe_v1.py',HERE/'counter_v3.py',HERE/'alternatives_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);c=candidate()
 for case,r,e in engine.run([c],'failed-cue-stair-repair-clean'):
  q=purpose(case,r);good=q['ok'];rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'],causal=q['causal'],last=rows[-1]['actual']['last'],shots=r.get('shots'),jumps=r.get('jumps'))),flush=True)
 if good:
  for case,r,e in engine.run([instantiate(c,261031301,l,k)for l in ['mild','moderate']for k in range(6)],'failed-cue-stair-repair-perturb'):
   q=purpose(case,r);rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
