"""Frozen V2 regression. Total Cell campaign remains below 120 real cases."""
import argparse,json
from pathlib import Path
from . import probe_v1 as old,probe_v2 as fixed,verify_v1 as checks,probe_enemy_v2 as enemy
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import evaluate
HERE=Path(__file__).parent

def cases():
 out=fixed.cases()
 for c in out:c['id']+='-cell-v2'
 for c in checks.passage_cases():
  if c['id'].startswith('pair-cell-pass-B-'):
   c['id']+='-corrected-v2';c['latches'][0]['paired_gate']=[1050,250,24,188];out.append(c)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--fault',action='store_true');a=p.parse_args();runner=HERE/('fault_runner_v2.gd'if a.fault else'runner_v2.gd');sources=enemy.SOURCES+[Path(__file__),Path(checks.__file__),HERE/'fault_runner_v2.gd'];e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=sources,runner_script=runner);rows=[]
 for c,r,b in e.run(checks.fault_cases()if a.fault else cases(),'fault-regression'if a.fault else'cell-regression'):
  q=checks.check_fault(c,r)if a.fault else checks.check_passage(c,r)if'expected_passage'in c or'expect_passage'in c else old.check(c,r)
  rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),fault_injection=a.fault,rows=rows))
 if not a.fault:
  selected=next(c for c in cases()if c['probe_kind']=='twice'and c['latches'][0]['initial_open']=='A');entries=evaluate(e,[selected],261027102,12,'v2-perturbation',purpose_fn=old.check);write(e.out/'perturbation-summary.json',dict(actual_cases=e.sim.cases,entries=entries,scope='Cell component regression only, not candidate Module admission'))
if __name__=='__main__':main()
