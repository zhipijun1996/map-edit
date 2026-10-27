import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_d05_validation import rules_v2 as original
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent
def main():
 source=[original.fixture(i,2)for i in [0,1]];cases=[]
 for c in source:
  v=rules.adapted(c);v['id']+='-missed-bell-recovery';cases.append(v)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockd05-recovery-v1',extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(original.__file__),*original.SOURCE_DEPENDENCIES,HERE/'recovery-protocol-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'same-world-recovery'):
  local=copy.deepcopy(r)
  for f in local.get('frames',[]):f['x']-=rules.DX;f['y']-=rules.DY
  q=original.purpose(source[c['interface']],local);owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
  q['causal']['unreserved_body_frames']=outside[:12]
  if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
  q['ok']=not q['reasons'];row=dict(id=c['id'],purpose=q,result=dict(ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),coins=r.get('workshop',{}).get('coins')),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),scope='clean exact original recovery control only, no general recovery guarantee'))
if __name__=='__main__':main()
