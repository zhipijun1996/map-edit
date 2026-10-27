import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','noise','counters'],default='clean');p.add_argument('--interface',type=int,default=0);p.add_argument('--controls',type=int,nargs='+',default=[0,1,2,3]);a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);source=[rules.materialize(a.interface,i)for i in a.controls]
 cs=source if a.mode=='clean'else[instantiate(c,261033055,level,i)for c in source for level in ['mild','moderate']for i in range(6)]if a.mode=='noise'else[v for c in source for v in rules.alternatives(c)]
 rows=[]
 for c,r,ev in e.run(cs,a.mode):
  q=rules.purpose(c,r);last=r.get('frames',[{}])[-1];row=dict(id=c['id'],interface=c['interface'],control=c['rule_parameters']['control'],purpose=q,result=dict(ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),coins=r.get('workshop',{}).get('coins'),shots=r.get('shots'),jumps=r.get('jumps'),last={k:last.get(k)for k in ['frame','x','y','support_id']}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
