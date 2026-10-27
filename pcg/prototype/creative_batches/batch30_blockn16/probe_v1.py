import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
def first8():
 cs=[rules.candidate(596,20),rules.candidate(580,24)]
 v=rules.candidate(596,20);v['id']+='-aim6';v['noise']=dict(seed=271131626,timing_frames=0,aim_degrees=6);cs.append(v)
 for x in [532,468]:
  v=rules.candidate(x,20);v['id']+='-counter-detached';v['counterexample_kind']='detached-'+str(x);cs.append(v)
 v=rules.candidate();v['id']+='-counter-ordinary';v['counterexample_kind']='ordinary';v['control_plan'][7]=cmd('wait');cs.append(v)
 v=rules.candidate();v['id']+='-counter-ground-preopen';v['counterexample_kind']='ground-preopen';v['control_plan']=copy.deepcopy(v['control_plan'][:5])+[cmd('shoot',aim_cell=dict(kind='bell',id='wall-bell')),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=[0,1]),settle(1000),ground(),cmd('wait',20)];cs.append(v)
 v=rules.candidate();v['id']+='-miss-real-ground-retry';v['probe_kind']='same_world_recovery_fixture';v['control_plan']=copy.deepcopy(v['control_plan'][:7])+[cmd('shoot',direction=[-1,0]),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',24),cmd('shoot',aim_cell=dict(kind='bell',id='wall-bell')),settle(1000),ground(),cmd('wait',20)];cs.append(v)
 return cs
def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn16-core-v1',extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(first8(),'first-eight'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=1))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
