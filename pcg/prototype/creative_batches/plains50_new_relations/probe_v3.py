"""Replacement proposals after D04/D05 stayed below stable-arrival gate."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import refund,cmd,settle
HERE=Path(__file__).parent

def adverse_refund(v=0,second=18):
 c=refund(0);c['id']=f'p50-adverse-refund-{v}-d{second}';c['family']='adverse-refund-reversal'
 enemy_x=230+v*10;c['enemies'][0]['position']=[enemy_x,422]
 x=330+v*25;y=110-v*10;c['platforms'][1]=[x-90,y+18,210,80];c['exit_port']=[x,y];c['goal']=[x-25,y-4,50,8]
 c['reward_sites'][0]['position']=[x,y];c['reward_sites'][0]['region']=[x-30,y-5,60,10];c['control_plan'][5]['trigger']['after']=second;c['control_plan'][-1]=settle(x,6)
 c['rule_parameters']=dict(relationship='air-hit resource gain sends body away from high shore; recovered shot reverses direction',enemy_x=enemy_x,landing=[x,y],original_family='air-refund');return c

def refund_gate(v=0):
 c=refund(v);c['id']=f'p50-refund-gate-{v}';c['family']='refill-short-gate'
 c['latches']=[dict(id='refill-gate-bell',bell=[172,218],gate=[300+v*20,-120,20,238-v*20],open_seconds=.75,return_access=[420+v*30,90-v*20])]
 c['control_plan'][5]=cmd('shoot',after=18,aim_cell=dict(kind='bell',id='refill-gate-bell'))
 c['rule_parameters']=dict(c['rule_parameters'],relationship='use recovered second shot to open short high door while rising',gate_seconds=.75,bell=[172,218],original_family='air-refund + timed-cache');return c

def candidates():return [adverse_refund(v,d)for v in [0,1]for d in [14,18]]+[refund_gate(v)for v in [0,1]]
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v3';e=WorkshopEngine(out,extra_sources=[Path(__file__)]);rows=[]
 for c,r,ev in e.run(candidates(),'replacement-proposals'):
  fs=r.get('frames',[]);row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,accepted=[dict(frame=f['frame'],x=f['x'],y=f['y'],events=f['accepted'])for f in fs if f.get('accepted')],evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
