import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v5 import candidates as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine

def candidates():
 out=[]
 for c in old('park-return'):
  c=copy.deepcopy(c);c['id']=c['id'].replace('v5','v7');c['control_plan'][22]['trigger']['dynamic']['value']=920;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v7';e=WorkshopEngine(out,extra_sources=list(Path(__file__).parent.glob('*.py')));rows=[]
 for c,r,ev in e.run(candidates(),'park-repair'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),events=r.get('workshop',{}).get('events'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
