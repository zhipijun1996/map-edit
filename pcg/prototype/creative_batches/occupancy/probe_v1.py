import copy,json,math
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import base,cmd,wait_x,settle,reward,finish
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def candidates():
    out=[]
    for takeoff in [240,260]:
        for gap in [18,24]:
            c=base(f'enemy-sensor-{takeoff}-{gap}');c['family']='enemy-sensor-hold'
            c['platforms']=[[-160,438,1100,100]]
            c['enemies']=[dict(id='keeper',definition='plains_sentry',position=[330,422],initial_idle_cooldown=.6)]
            c['latches']=[dict(id='living-sensor',bell=[350,430],gate=[500,-300,20,738],open_seconds=.05,occupancy=dict(mode='enemy_alive',rect=[345,410,10,28]))]
            reward(c,650,420,12)
            plan=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,aim_cell=dict(kind='enemy',id='keeper')),cmd('shoot',gap,direction=[-.9886859966642595,.15]),settle(650,6)]
            c=finish(c,650,420,plan);c['max_frames']=500;out.append(c)
    return out

def run():
    e=WorkshopEngine(ROOT/'results/workshop-creative-occupancy-probe-v1',extra_sources=[p for p in HERE.iterdir()if p.suffix in ['.py','.gd','.tscn']],runner_script=HERE/'runner_v1.gd');rows=[]
    for c,r,ev in e.run(candidates(),'probe'):
        rows.append(dict(case=c,result=r,evidence=ev));print(json.dumps(dict(id=c['id'],ok=r['ok'],reason=r['reason'],hp=r.get('hp'),events=r.get('plains',{}).get('events',[]),last=r.get('frames',[])[-1:])),flush=True)
    write(e.out/'rows.json',rows)
if __name__=='__main__':run()
