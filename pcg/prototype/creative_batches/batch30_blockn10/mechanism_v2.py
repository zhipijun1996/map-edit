"""Same isolated controls, distinct original Module markers required by Harness."""
import argparse,json
from pathlib import Path
from .mechanism_v1 import candidate as original,purpose
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
HERE=Path(__file__).parent
def candidate(k):
 c=original(k);c['exit_port']=[680,600];c['id']+='-fixture-v2'
 c['validation_fixture']=dict(kind='stationary_receiver_layer_controls',actual_goal=[600,600],definition_exit_marker=[680,600],marker_is_not_route_destination=True,no_module_enrollment=True)
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=check([HERE/'runner_v1.gd'])
 if checks['status']!='syntax_checked':write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'mechanism_v1.py',HERE/'runner_v1.gd',HERE/'observe_v1.gd',HERE/'protocol-v1.json',HERE/'idea-source-v1.json'],runner_script=HERE/'runner_v1.gd');write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run([candidate(k)for k in [0,1,2]],'receiver-controls'):
  q=purpose(c,r);rows.append(dict(case=c,purpose=q,evidence=ev));write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],purpose=q)),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0,prior_rejected_definition_calls=3,lineage_experiment_calls=6))
if __name__=='__main__':main()
