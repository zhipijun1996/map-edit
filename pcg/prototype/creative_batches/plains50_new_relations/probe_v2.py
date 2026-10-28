"""Second bounded geometry revision after first real probe failures."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.creative_batches.plains50_new_relations.probe_v1 import crate,return_park,descent
HERE=Path(__file__).parent

def crate2(v=0):
 c=crate(v,16);c['id']=f'p50-slide-catch-v2-{v}';x=840+v*30;c['platforms'][1][0]=x
 c['reward_sites'][0]['position'][0]=x+100;c['reward_sites'][0]['region'][0]=x+70;c['exit_port'][0]=x+100;c['goal']=[x+75,c['exit_port'][1]-4,50,8];c['control_plan'][-1]=settle(x+100,6)
 c['rule_parameters'].update(receiver_x=x,revision='lower horizontal demand after actual support contact but failed high shore');return c

def return2(v=0):
 c=return_park(v);c['id']=f'p50-return-invest-v2-{v}';far=540+v*20;c['platforms'][1][0]=far;c['reward_sites'][0]['position'][0]=far+100;c['reward_sites'][0]['region'][0]=far+70
 c['moving_platforms'][0].update(start=[270,400+v*10],finish=[530+v*20,400+v*10]);p=c['control_plan'];p[7]=settle(far+100,6);p[10]=wait_x(far-20,-1);p[13]=wait_x(400+v*15,-1);c['rule_parameters'].update(far_shore=far,return_y=400+v*10);return c

def descent2(v=0):
 c=descent(0);c['id']=f'p50-descent-v2-{v}';c['latches'][0]['bell']=[540,280];c['platforms'][-1]=[300,100,30,180]
 c['moving_platforms'][0].update(start=[360,330],finish=[760+v*15,630]);c['platforms'][1][1]=365+v*10
 c['exit_port'][1]=347+v*10;c['reward_sites'][0]['position'][1]=347+v*10;c['reward_sites'][0]['region'][1]=342+v*10;c['goal'][1]=343+v*10
 c['rule_parameters'].update(near_bank_rock=[300,100,30,180],bell=[540,280],receiver_y=365+v*10,repair='real tooth occludes bank muzzle; deck is30 lower to pass underneath tooth');return c

def candidates():return [crate2(v)for v in [0,1]]+[return2(v)for v in [0,1]]+[descent2(v)for v in [0,1]]
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v2';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'probe_v1.py',HERE/'runner_v1.gd',HERE/'sliding_support_v1.gd'],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(candidates(),'new-relations-revision2'):
  fs=r.get('frames',[]);ss=[f for f in fs if f.get('support_id')in ['sliding-crate','return-step','descending-deck']]
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),support_frames=len(ss),last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
