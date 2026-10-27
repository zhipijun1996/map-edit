"""Preselected cheaper gate/brake policies and disclosed lower-bank options."""
import argparse,copy,json
from .macro import macro_cases,recipe,scoped
from .rules import cmd,ground,wait_x,settle,launch
from .engine import ROOT,WorkshopEngine
from .experiments import write

def policies(variant):
    routes,_=macro_cases(variant);a,b=recipe(variant);out=[]
    def add(base,label,plan,scope='same_entry_cheaper'):
        c=copy.deepcopy(base);c['id']+='-counter-'+label;c['control_plan']=copy.deepcopy(plan)
        c['counterexample_kind']=label;c['counterexample_scope']=scope;out.append(c)
    cache=routes[1];descent=routes[2]
    for base in [cache,descent]:
        for i,step in enumerate(base['control_plan']):
            if step['op']!='shoot':continue
            plan=copy.deepcopy(base['control_plan']);plan[i]=dict(op='wait',trigger=copy.deepcopy(step['trigger']))
            add(base,'omit-shot-'+str(i),plan)
    for hold in [0,4,8,12,20,30]:
        for x in [180,220,238]:
            add(cache,f'ordinary-jump-{x}-{hold}',[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',hold),settle(cache['exit_port'][0],4)])
    for delay in [0,6,12]:
        plan=copy.deepcopy(cache['control_plan']);i=next(i for i,s in enumerate(plan)if s['op']=='shoot');shot=plan.pop(i);shot['trigger']=dict(after=delay)
        add(cache,'early-ground-'+str(delay),[shot]+plan)
    lip=b['platforms'][0][0]+b['platforms'][0][2]
    for x in [lip+20,lip+40,lip+60,lip+80,lip+105,lip+125]:
        add(descent,'drop-turn-'+str(x),[cmd('axis',value=1),wait_x(x),settle(b['exit_port'][0])])
    for x in [80,180,220]:
        add(cache,'overtop-'+str(x),launch(20,25,1,x)+[settle(cache['exit_port'][0],6)])
    for hold in [0,4,8,12,20,30]:
        lower=scoped(b,'lower-approach','E','B','reward',[])
        add(lower,'lower-jump-'+str(hold),[cmd('axis',value=0),cmd('jump'),cmd('jump_release',hold),cmd('axis',value=1),settle(b['exit_port'][0],6)],'different_lower_entry')
        upper=copy.deepcopy(routes[0]);upper.pop('ports');upper.pop('route_spec');upper.update(spawn=[335,632],entry_port=[335,632],expected_reward=10)
        add(upper,'return-shelf-jump-'+str(hold),[cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),settle(b['exit_port'][0],6)],'different_return_shelf_entry')
    assert len(out)<=60
    return out

def run(name):
    engine=WorkshopEngine(ROOT/'results'/name);cs=[c for v in range(2)for c in policies(v)]
    write(engine.out/'protocol.json',dict(schema='pcg/workshop-macro-counter/v1',maximum_policies_per_interface=60,actual_policies=len(cs),selection='Fixed listed grid before execution',different_entry='report independently; never claim initial-state necessity',proof_of_necessity=False))
    write(engine.out/'cases.json',dict(cases=cs));rows=[]
    for c,r,e in engine.run(cs,'counterexample'):
        row=dict(id=c['id'],kind=c['counterexample_kind'],scope=c['counterexample_scope'],safe_stable=bool(r['ok']),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),reason=r['reason'],evidence=e)
        rows.append(row);write(engine.out/'rows.json',rows)
        if row['safe_stable']:print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(cases=len(rows),same_entry_successes=[r for r in rows if r['safe_stable']and r['scope']=='same_entry_cheaper'],different_entry_successes=[r for r in rows if r['safe_stable']and r['scope']!='same_entry_cheaper'],necessity_proof=False))
    print(engine.out,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
