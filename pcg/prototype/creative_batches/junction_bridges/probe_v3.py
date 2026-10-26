import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from . import rules_v3 as rules

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mild',type=int,default=0);p.add_argument('--moderate-lifts',type=int,default=0);a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),Path(__file__).with_name('protocol-v1.json')]);cs=[c for i in range(2)for c in rules.layouts(rules.RECIPES[0],i)];rows=[]
 if a.moderate_lifts:
  from pcg.prototype.workshop.evaluate import instantiate
  cs=[instantiate(c,261026731,'moderate',i)for c in cs if c['route_spec']['id']in ['lower-to-upper','descend-then-lift']for i in range(a.moderate_lifts)]
 elif a.mild:
  from pcg.prototype.workshop.evaluate import instantiate
  cs=[instantiate(c,261026731,'mild',i)for c in cs for i in range(a.mild)]
 for c,r,ev in e.run(cs,'authored-route-probe'):
  ps=rules.purpose(c,r);row=dict(id=c['id'],ok=ps['ok'],purpose=ps,reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),last=({k:r['frames'][-1].get(k)for k in ['frame','x','y','vx','vy','grounded','support_id']}if r.get('frames')else{}),min_y=min((f['y']for f in r.get('frames',[])),default=None),fired=r.get('fired_commands'),evidence=ev)
  rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(r['ok']for r in rows),rows=rows))
if __name__=='__main__':main()
