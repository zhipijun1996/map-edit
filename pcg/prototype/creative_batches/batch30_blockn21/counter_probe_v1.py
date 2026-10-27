import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from . import control_v2 as control
from .alternatives_v1 import alternatives
from .counter_policy_v1 import classify
from .screen_v1 import DEPS
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name;bases=[control.candidate(t,0)for t in ['B','C']];binding=inspect_counter_bindings(bases,alternatives,18)
 if binding['status']!='requires_physics':write(out/'binding.json',binding);raise ValueError('counterID/geometrypreflightrejected')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'screen_v1.py',HERE/'alternatives_v1.py',HERE/'counter_policy_v1.py',*DEPS],runner_script=rules.RUNNER_SCRIPT);write(out/'binding.json',binding);rows=[]
 cs=[c for b in bases for c in alternatives(b)[:12]]
 for c,r,ev in e.run(cs,'first-twelve-exact-counters-per-branch'):
  q=rules.purpose(c,r);decision=classify(c,r,q,common.external_outcome(c,r));v=dict(case=c,purpose=q,counter_classification=decision,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],refutes=decision['invalidates_design'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=46,new_candidates=0,refutations=sum(v['counter_classification']['invalidates_design']for v in rows)))
if __name__=='__main__':main()
