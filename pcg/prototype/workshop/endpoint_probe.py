"""Try ordinary jumps after the carrier has moved near its far endpoint."""
import argparse,copy,json
from .engine import ROOT,WorkshopEngine
from .experiments import source_cases,write
from .rules import cmd,settle
from .carrier_fixture import request,adapt

def run(name,map_case=False):
    bases=adapt(request()[1])['cases']if map_case else source_cases(['chase-landing'])[1]
    engine=WorkshopEngine(ROOT/'results'/name);cs=[]
    for base in bases:
        depart=next(i for i,p in enumerate(base['control_plan'])if p['op']=='jump'and i>1)
        for delay in [0,20,50]:
            c=copy.deepcopy(base);c['counterexample_kind']='ordinary-far-endpoint-'+str(delay);c['id']+='-counter-'+c['counterexample_kind']
            c['control_plan']=c['control_plan'][:depart]+[cmd('axis',value=0),cmd('wait',delay),cmd('axis',value=1),cmd('jump'),cmd('jump_release',30),settle(c['exit_port'][0])]
            cs.append(c)
    write(engine.out/'protocol.json',dict(maximum_cases=len(cs),delays=[0,20,50],selection='fixed before execution',new_resource_writes=False))
    rows=[]
    for c,r,e in engine.run(cs,'counterexample'):
        row=dict(id=c['id'],safe_stable=r['ok'],reason=r['reason'],shots=r.get('shots'),evidence=e);rows.append(row);print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(rows=rows,cheap_successes=[r for r in rows if r['safe_stable']]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--map',action='store_true');a=p.parse_args();run(a.name,a.map)
