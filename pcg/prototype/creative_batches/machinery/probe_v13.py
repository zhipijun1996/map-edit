import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v12 import candidates as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
HERE=Path(__file__).parent

def candidates():
 cs=old()
 for c in cs:c['id']=c['id'].replace('v12','v13');c['control_plan'][4]['trigger']['timeout']=420
 return cs
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v13';e=WorkshopEngine(out,extra_sources=list(HERE.glob('*.py'))+list(HERE.glob('*v11.gd')),runner_script=HERE/'dock_runner_v11.gd');rows=[]
 for c,r,ev in e.run(candidates(),'interlock-probe'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in r.get('frames',[])}),events=r.get('plains',{}).get('events'),evidence=ev);rows.append(row);print(json.dumps({k:v for k,v in row.items()if k!='events'}),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
