import argparse,json
from pathlib import Path
from . import rules_v2 as core
from . import recovery_v1 as recovery
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['confirm','clean','noise'],default='clean');a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(core.__file__),Path(recovery.__file__)]+recovery.SOURCE_DEPENDENCIES,runner_script=core.RUNNER_SCRIPT)
 if a.mode=='confirm':cs=core.layouts(core.RECIPES[0],0)
 elif a.mode=='clean':cs=[recovery.materialize(control,restore)for control in range(2)for restore in [True,False]]
 else:cs=[instantiate(recovery.materialize(0,True),261035073,level,i)for level in ['mild','moderate']for i in range(4)]
 rows=[]
 for c,r,ev in e.run(cs,a.mode):
  q=core.purpose(c,r)if a.mode=='confirm'else recovery.purpose(c,r);last=r.get('frames',[{}])[-1];expect=c.get('validation_fixture',{}).get('restore',True);test=q['ok']if expect else(not r.get('ok')and 'low-cache'not in q['causal']['claimed_rewards']and not any(x.get('open')=='B'for x in q['causal']['actual_pair_events']))
  row=dict(id=c['id'],purpose=q,test_passed=test,expect_restore=expect,result=dict(ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),coins=r.get('workshop',{}).get('coins'),last={k:last.get(k)for k in ['frame','x','y','support_id']}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows),tests_passed=sum(x['test_passed']for x in rows)))
if __name__=='__main__':main()
