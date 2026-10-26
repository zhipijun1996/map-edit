"""PR-D03 resource-feasibility probes only; not a generator or candidate."""
import json
from pathlib import Path
from pcg.prototype.workshop.rules import refund,cmd,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
HERE=Path(__file__).parent

def cases():
 out=[]
 for delay in [14,18,22,26]:
  c=refund(0);c['id']=f'plains50-D03-finite-health-d{delay}';c['family']='D03-resource-feasibility-probe';c['max_frames']=360;c['trace_all']=True
  p=c['control_plan'][:5]
  p.extend(cmd('shoot',delay,aim_cell=dict(kind='enemy',id='ammo-sentry'))for _ in range(3))
  p.append(settle(350,6));c['control_plan']=p;c['proposal_status']='missing_two_route_generator_and_persistent_recovery';out.append(c)
 return out
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-plains50-D03-resource-probe-v1',extra_sources=[Path(__file__)]);rows=[]
 for c,r,ev in e.run(cases(),'resource-probe'):
  shots=[f for f in r.get('frames',[])if any(a['type']=='shot'for a in f.get('accepted',[]))]
  events=r.get('plains',{}).get('events',[])
  rows.append(dict(case=c,result=r,evidence=ev));print(c['id'],r['reason'],r.get('shots'),[(x['frame'],x.get('shot_charges'))for x in shots],r.get('plains',{}).get('enemies'),flush=True)
 (e.out/'probe-results.json').write_text(json.dumps(rows))
