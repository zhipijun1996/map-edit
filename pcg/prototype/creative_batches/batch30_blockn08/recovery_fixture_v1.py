"""Registered optional clean miss/access retry, same actor/world/reward ledger."""
import json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent

def candidate():
 c=rules.candidate(0,'loop');c['id']+='-miss-access-real-primary-retry';start=len(rules.old.outbound(0));ret=c['control_plan'][start:]
 assert ret[4]['op']=='shoot'and ret[8]['op']=='wait'
 ret[4]=cmd('shoot',direction=[0,-1])
 # Wait60 is a conservative projectile flight cap for816px at original1200/s
 # plus commit margin. Player stands on real bank; no fall-timing assumption.
 ret[9:9]=[cmd('shoot',aim_cell=dict(kind='bell',id='fold-pair')),cmd('wait',60)]
 c['control_plan']=c['control_plan'][:start]+ret;return c

def main():
 c=candidate();e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn08-miss-retry-clean-v1',extra_sources=[Path(__file__),HERE/'control-selection-v1.json',*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([c],'same-world-miss-retry'):
  q=checked_purpose(rules,c,r);q['causal']['actual_extra_recovery_shot']=r.get('shots')==5;q['causal']['recovery_generalization']='UNKNOWN:onecleanonly';row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,same_geometry_as_nominal=True,new_modules=0,quality_scope='Only1cleanfailure/retry; nooriginalregular/heldrecoveryclaim'))
if __name__=='__main__':main()
