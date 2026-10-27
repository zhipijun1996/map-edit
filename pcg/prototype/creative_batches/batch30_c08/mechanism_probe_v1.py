import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[HERE.parent/'batch30_c04/stable_support_names_v1.gd']+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]
def make(label,release=False,close_at=None):
 c=base('b30-c08-mechanism-'+label);c['family']='charger-gate-space-test';c['capabilities']=['move','jump','shot_recoil'];c['platforms']=[[-180,438,900,100]];c['spawn']=[200,420];c['entry_port']=[200,420];c['exit_port']=[220,420];c['goal']=[175,416,50,8];c['max_frames']=420;c['trace_all']=False
 c['latches']=[dict(id='release',bell=[250,400],gate=[540,-200,20,638],paired_gate=[40,-200,20,638],initial_open='A',open_seconds=0)]
 c['enemies']=[dict(id='borrowed-charger',definition='plains_charger',position=[0,422],initial_idle_cooldown=.2)]
 if release:
  c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='release')),settle(200)]
  if close_at is not None:c['control_plan'] += [cmd('wait',close_at),cmd('shoot',aim_cell=dict(kind='bell',id='release')),cmd('wait',80)]
  else:c['control_plan'] += [cmd('wait',240)]
 else:c['control_plan']=[cmd('wait',240),settle(200)]
 c['mechanism_test']=dict(label=label,released=release,close_at=close_at);return c
def cases():return[make('closed'),make('released',True),*[make('released-close-'+str(t),True,t)for t in [36,42,48,180]]]
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(cases(),'charger-real-gate-space'):
  fs=r.get('frames',[]);actors=[f.get('plains',{}).get('enemies',[{}])[0]for f in fs if f.get('plains',{}).get('enemies')];pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0]
  row=dict(id=c['id'],test=c['mechanism_test'],ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),enemy_x_range=[min((v['x']for v in actors),default=None),max((v['x']for v in actors),default=None)],enemy_final=r.get('plains',{}).get('enemies'),pair=pair,enemy_state_events=[v for v in r.get('plains',{}).get('events',[])if v.get('type')=='enemy_state'],samples=[dict(frame=f['frame'],enemy=f['plains']['enemies'][0])for f in fs[::20]if f.get('plains',{}).get('enemies')],evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'mechanism-results.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
