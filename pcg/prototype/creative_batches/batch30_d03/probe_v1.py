import json,math
from pathlib import Path
from pcg.prototype.workshop.rules import refund,cmd,settle,reward,finish
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def cases():
 out=[]
 for top in [-50,-80]:
  for delay in [14,18]:
   c=refund(0);c['id']=f'b30-d03-up-{top}-d{delay}';c['family']='finite-enemy-route';c['platforms'][1]=[260,top,220,70]
   c['reward_sites']=[];reward(c,350,top-18,12)
   plan=[cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='ammo-sentry')),cmd('shoot',delay,aim_cell=dict(kind='enemy',id='ammo-sentry')),cmd('shoot',18,direction=[-.5,math.sqrt(.75)]),settle(350,6)]
   finish(c,350,top-18,plan);c['max_frames']=720;c['trace_all']=False;out.append(c)
 return out

def report(c,r,e):
 fs=r.get('frames',[]);shots=[dict(frame=f['frame'],x=f['x'],y=f['y'],grounded=f['grounded'],rounds=f['shot_charges'],support=f.get('support_id'))for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
 return dict(case=c,result=r,evidence=e,summary=dict(ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=shots,enemy_hits=[e for e in r.get('plains',{}).get('events',[])if e['type']in ['enemy_hit','damage','enemy_defeated']],enemy=r.get('plains',{}).get('enemies'),last=({k:fs[-1].get(k)for k in ['frame','x','y','support_id']}if fs else{}),minimum_y=min((f['y']for f in fs),default=None)))

if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03-probe-v1',extra_sources=[Path(__file__),HERE/'protocol-v1.json']);rows=[]
 for c,r,ev in e.run(cases(),'shared-health-lift-probe'):
  row=report(c,r,ev);rows.append(row);print(json.dumps(dict(id=c['id'],**row['summary'])),flush=True)
 write(e.out/'probe-results.json',rows)
