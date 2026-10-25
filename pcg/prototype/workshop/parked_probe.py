"""Additional explicit static-dock bypass search, retained even if it refutes A2."""
import argparse,copy,json
from .rules import chase,cmd,ground,wait_x,settle
from .engine import ROOT,WorkshopEngine
from .experiments import write

def run(name):
    engine=WorkshopEngine(ROOT/'results'/name);cs=[]
    for v in range(2):
        for takeoff in [200,220,238]:
            c=chase(v);c['id']+=f'-static-dock-{takeoff}'
            c['control_plan']=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',20),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='chase-carrier'),timeout=180)),cmd('axis',value=0),cmd('wait',20),cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-.8,.6]),settle(c['exit_port'][0],6)]
            cs.append(c)
    rows=[]
    for c,r,e in engine.run(cs,'static-dock-counter'):
        row=dict(id=c['id'],safe_stable=r['ok'],shots=r.get('shots'),reason=r['reason'],carrier_events=r.get('workshop',{}).get('events',[]),evidence=e);rows.append(row);print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(rows=rows,successful_bypasses=[r for r in rows if r['safe_stable']]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
