"""Bounded static-dock/far-endpoint counterexamples for the A2 revision."""
import argparse,copy,itertools,json,math
from .rules import cmd,wait_x,settle
from .engine import ROOT,WorkshopEngine,HERE
from .experiments import write,source_cases,counter_run,produce
from .map_demand import request,adapt

def parked(c):
    out=[];lead=c['moving_platforms'][0]['start'][0]+c['moving_platforms'][0]['size'][0]/2-14
    for takeoff,first_hold,dy,last_hold in itertools.product([180,220,238],[12,20,30],[0,.4,.6,.8660254037844386],[8,16,24]):
        # 3*3*4*3=108 policies per fixed interface, all chosen before execution.
        v=copy.deepcopy(c);label=f'static-dock-{takeoff}-{first_hold}-{dy}-{last_hold}';v['id']+='-counter-'+label;v['counterexample_kind']=label
        v['control_plan']=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',first_hold),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='chase-carrier'),timeout=180)),cmd('axis',value=0),cmd('wait',20),cmd('axis',value=1),wait_x(lead),cmd('jump'),cmd('jump_release',last_hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)]
        out.append(v)
    return out

def counters(name,map_case=False):
    if map_case:
        _,s=request();response=adapt(s)
        if response['status']!='requires_physics':raise ValueError(response)
        requested=([s],response['cases'])
    else:requested=source_cases(['chase-landing'])
    counter_run(name+'/standard',['chase-landing'],requested)
    engine=WorkshopEngine(ROOT/'results'/name/'parked');cs=[v for c in requested[1]for v in parked(c)]
    write(engine.out/'protocol.json',dict(source='protocol-carrier-rework-v2.json',maximum_cases=len(cs),selection='fixed full Cartesian enumeration',necessity_proof=False))
    rows=[]
    for c,r,e in engine.run(cs,'counterexample'):
        row=dict(id=c['id'],safe_stable=r['ok'],reason=r['reason'],evidence=e);rows.append(row)
        if r['ok']:print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(cases=len(rows),cheap_successes=[r for r in rows if r['safe_stable']]))
    return requested

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--map',action='store_true');p.add_argument('--produce',action='store_true');a=p.parse_args()
    requested=counters(a.name,a.map)
    if a.produce:
        summary=json.loads((ROOT/'results'/a.name/'parked/summary.json').read_text())
        if summary['cheap_successes']:raise ValueError('static dock bypass still exists; no holdout selection')
        print(produce(a.name+'/holdout',['chase-landing'],a.name+'/standard,'+a.name+'/parked',requested,'protocol-carrier-rework-v2.json'))
