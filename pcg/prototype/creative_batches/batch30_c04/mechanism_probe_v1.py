import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','attack_observer_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]

def make(label,position=80,initial='B',close_at=None):
 c=base('b30-c04-mechanism-'+label);c['family']='cover-relay-mechanism-test';c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[-160,438,1000,100]];c['spawn']=[position,420];c['entry_port']=[position,420];c['exit_port']=[position+20,420];c['goal']=[position-25,416,50,8]
 c['latches']=[dict(id='relay',bell=[40 if position==80 else 540,390],gate=[170,300,20,138],paired_gate=[390,300,20,138],initial_open=initial,open_seconds=0)]
 c['enemies']=[dict(id='relay-sentry',definition='plains_sentry',position=[240 if position==80 else 320,422],initial_idle_cooldown=.05)]
 c['trace_all']=False;c['max_frames']=240
 c['control_plan']=[cmd('wait',140),settle(position)]if close_at is None else[cmd('wait',close_at),cmd('shoot',aim_cell=dict(kind='bell',id='relay')),cmd('wait',100),settle(position)]
 c['mechanism_test']=dict(label=label,position=position,initial=initial,close_at=close_at)
 return c

def cases():
 out=[make('old-covered',initial='B'),make('old-exposed',initial='A'),make('new-covered',position=480,initial='A'),make('new-exposed',position=480,initial='B')]
 for t in [43,48,53]:out.append(make('close-A-after-shot-'+str(t),initial='A',close_at=t))
 for t in [43,48,53]:out.append(make('close-B-after-shot-'+str(t),position=480,initial='B',close_at=t))
 return out

def summarize(c,r,ev):
 covers=[f.get('workshop',{}).get('cover',{})for f in r.get('frames',[])];last=r.get('workshop',{}).get('cover',{})
 return dict(id=c['id'],test=c['mechanism_test'],stable=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),player_damage=r.get('plains',{}).get('player_damage'),enemy_states=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='enemy_state'],actual_projectile_frames=sum(bool(f.get('projectiles'))for f in covers),projectile_exits=last.get('projectile_exits',[]),ray_labels=sorted({ray['ray_hit']for f in covers for ray in f.get('rays',[])}),evidence=ev)

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(cases(),'original-projectile-cover'):
  row=summarize(c,r,ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'mechanism-results.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
