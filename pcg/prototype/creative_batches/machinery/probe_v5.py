import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v2 import candidates as old
from pcg.prototype.creative_batches.machinery.probe_v1 import platform,board
from pcg.prototype.creative_batches.machinery.probe_v4 import candidates as park
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.dynamic.generators import dynamic as dyn
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine

def candidates(recipe=None):
 out=[]
 for c in old():
  if c['family']=='saw-pursuit':
   c=copy.deepcopy(c);c['id']=c['id'].replace('v2','v5');c['thorns']=[dict(surface_id='roof-no-bypass',platform_index=2,face='top',start_offset=0,length=460,depth=16)]
   out.append(c)
 for hold in [12,20]:
  c=copy.deepcopy(next(c for c in old()if c['family']=='carrier-rendezvous'));c['id']='transfer-v5-'+str(hold);c['moving_platforms'][0]=platform('carrier',[300,448],[650,448],2.,7.)
  p=board();p[3]['trigger']['timeout']=1500
  p += [dyn('wait','platform_phase',query=dict(id='carrier',window=[.5,.51]),timeout=1600),dyn('wait','platform_phase',query=dict(id='other',window=[0,.02]),timeout=450),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=hold),dyn('wait','on_platform',query=dict(id='other'),timeout=150),cmd('axis',value=0),dyn('wait','platform_phase',query=dict(id='other',window=[.5,.52]),timeout=450),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1370,6)]
  c['control_plan']=p;c['max_frames']=3400;out.append(c)
 for c in park():
  c=copy.deepcopy(c);c['id']=c['id'].replace('v4','v5');p=c['control_plan'];p[14:20]=[wait_x(710),cmd('axis',value=0),dict(op='wait',trigger=dict(state='grounded',timeout=180)),cmd('axis',value=-1),wait_x(500,-1),cmd('axis',value=0),dyn('wait','on_platform',query=dict(id='carrier'),timeout=180)]
  c['control_plan']=p;out.append(c)
 return [c for c in out if recipe is None or c['family']==recipe]
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v5';e=WorkshopEngine(out,extra_sources=list(Path(__file__).parent.glob('*.py')));rows=[]
 for c,r,ev in e.run(candidates(),'repair-probe'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in r.get('frames',[])}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
