import json,copy
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v2 import candidates as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine

def candidates():
 out=[]
 for c in old():
  if c['family']!='park-return':continue
  c=copy.deepcopy(c);c['id']=c['id'].replace('v2','v4');c['platforms'][1]=[650,245,160,60];c['reward_sites'][0].update(position=[720,227],region=[690,222,60,10]);
  # Leave the ledge with a precise settle target over the truly parked support.
  c['control_plan'][17]['trigger']['dynamic']['value']=590
  out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v4';e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(__file__).with_name('probe_v1.py'),Path(__file__).with_name('probe_v2.py')]);rows=[]
 for c,r,ev in e.run(candidates(),'park-repair'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in r.get('frames',[])}),events=r.get('workshop',{}).get('events'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
