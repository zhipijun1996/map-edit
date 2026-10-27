import json
from pathlib import Path
from . import rules_v2 as rules
from . import recovery_v1 as checks
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
def cases():
 out=[]
 for restore in [True,False]:
  c=rules.materialize(1,'low',0);c['id']+='-recovery-wrong-left-late42-'+('restore'if restore else'no-restore');c['max_frames']=1800
  c['control_plan']=[cmd('axis',value=-1),wait_x(160,-1),cmd('axis',value=0),cmd('wait',42),cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair')),settle(230),ground(),cmd('wait',12),cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair'))if restore else cmd('wait'),cmd('wait',35),settle(330),wait_x(326),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),settle(510),ground(),cmd('wait',10)]
  c['validation_fixture']=dict(kind='wrong_edge_late_high_miss_then_low_recovery',module_enrollment=False,restore=restore,late_wait=42);out.append(c)
 return out
def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-c06-slender-recovery-v1',extra_sources=[Path(__file__),Path(rules.__file__),Path(checks.__file__),HERE/'slender-recovery-protocol-v1.json']+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases(),'slender-recovery'):
  q=checks.purpose(c,r);expected=c['validation_fixture']['restore'];test=q['ok']if expected else(not r.get('ok')and 'low-cache'not in q['causal']['claimed_rewards']and not any(x.get('open')=='B'for x in q['causal']['actual_pair_events']))
  row=dict(id=c['id'],purpose=q,test_passed=test,expect_restore=expected,result=dict(ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),coins=r.get('workshop',{}).get('coins'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['frame','x','y','support_id']}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows),tests_passed=sum(x['test_passed']for x in rows)))
if __name__=='__main__':main()
