import argparse,json,copy
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import wait_x,settle,ground,cmd
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',required=True,choices=['noise','counters','return']);a=p.parse_args();sel=HERE/'control-selection-v1.json';s=json.loads(sel.read_text());near=rules.candidate(**s['selected_near']);detached=rules.candidate(**s['matched_detached'])
 if a.stage=='noise':cs=[instantiate(c,271131626,l,k)for c in [near,detached]for l in ['mild','moderate']for k in range(6)]
 elif a.stage=='counters':cs=counters.preliminary(near)
 else:
  c=copy.deepcopy(near);c['id']+='-same-world-B-then-return-A';c['probe_kind']='same_world_return_fixture';c['goal']=[17,586,14,8];c['control_plan']+=[wait_x(993),ground(),cmd('wait',20),settle(24),ground(),cmd('wait',20)];cs=[c]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(counters.__file__),sel,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if a.stage=='counters':row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=1))
  if a.stage=='return':
   visits=[f for f in r['frames']if f.get('grounded')and abs(f['x']-1000)<=7 and abs(f['y']-334)<=1 and abs(f['vx'])<=1];row['fixture_only_B_supported_stable_frames']=len(visits);row['actual_end']=r['frames'][-1];row['static_definition_exit_B_is_not_actual_return_end']=True
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),design_refutations=[r['id']for r in rows if r.get('classification',{}).get('invalidates_design')],rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
