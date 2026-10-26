import argparse,copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from . import fixtures_v1 as fixtures

HERE=Path(__file__).parent


def cases():
    out=[]
    for j in range(2):
        c=fixtures.candidate(0,j,0);indices=[i for i,q in enumerate(c['control_plan'])if q['op']=='shoot']
        assert len(indices)==4
        for k,index in enumerate(indices):
            v=copy.deepcopy(c);v['control_plan'][index]['op']='wait';v['id']+=f'-counter-omit-shot{k}';v['counterexample_kind']=f'omit-shot{k}';out.append(v)
        for launch in [1070,1080,1090]:
            v=copy.deepcopy(c);v['control_plan'][10]['trigger']['dynamic']['value']=launch;v['control_plan'][indices[1]]['op']='wait';v['id']+=f'-counter-late-takeoff{launch}-omit-C01second';v['counterexample_kind']=f'late-takeoff{launch}-omit-C01second';out.append(v)
    return out


def run(name):
    e=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),HERE/'counter-protocol-v1.json',Path(fixtures.__file__),Path(classify.__code__.co_filename)]+fixtures.SOURCE_DEPENDENCIES,runner_script=fixtures.RUNNER_SCRIPT)
    cs=cases();write(e.out/'protocol.json',json.loads((HERE/'counter-protocol-v1.json').read_text()));write(e.out/'cases.json',dict(cases=cs));rows=[]
    for c,raw,ev in e.run(cs,'joined-content-omission-counter'):
        r,audit=classify(c,raw);claimed={x['id']for x in r.get('workshop',{}).get('events',[])if x['type']=='chest_claim'and x.get('accepted')};safety=r.get('hp')==5 and not r.get('plains',{}).get('player_damage')and not r.get('returns');allowed=not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
        rawgoal=bool(r.get('ok'))and set(c['required_rewards'])<=claimed and r.get('workshop',{}).get('coins')==24 and safety
        row=dict(id=c['id'],kind=c['counterexample_kind'],same_external_goal_and_capabilities=rawgoal and allowed,raw_safe_stable_both_rewards=rawgoal,forbidden_observer_events={k:r.get(k)for k in ['air_jumps','wall_jumps','grapples']},shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),coins=r.get('workshop',{}).get('coins'),reason=r.get('reason'),observer_interpretation=audit,evidence=ev)
        rows.append(row);print(json.dumps(row),flush=True)
    write(e.out/'summary.json',dict(actual_cases=e.sim.cases,same_goal_successes=[x for x in rows if x['same_external_goal_and_capabilities']],raw_stable_reward_successes=[x for x in rows if x['raw_safe_stable_both_rewards']],rows=rows,scope='Fixed omissions and latertakeoffs in exact composition only; no proof of necessity',new_modules=0,production_admitted=False))
    return e.out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
