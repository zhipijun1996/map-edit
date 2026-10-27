"""Predeclared bounded generation audit; retain rejected seeds and stages."""
import argparse,copy,json,time,traceback
from pathlib import Path
from .build import build
from ..block_grid.plan import allocate,condition_types,run as plan
from ..block_grid.policy import principal_routes,review
from ..director import REPO,regional
from ..run import write


def run(name,sources):
    out=REPO/'pcg/results'/name;out.mkdir(parents=True,exist_ok=False)
    seeds=['graph-map-new-interface-0','graph-map-new-interface-1','graph-map-new-full-0']
    write(out/'protocol.json',dict(seeds=seeds,sources=sources,attempts_per_seed=2,wall_seconds_per_attempt=30,geometry_probe_limit=3500000,may_delete_required_routes=False,physics='Separate stage, never inferred from layout',selection='All predeclared seeds reported; no seed search for publication'))
    rows=[]
    for index,seed in enumerate(seeds):
        started=time.perf_counter()
        try:
            if index<2:
                p=json.loads((REPO/'pcg/results/graph-map-whole-evaluation-v2/policy.json').read_text())
                g=regional.construct(seed,'plains',12,reward_expeditions=3,reward_return_modes=['foldback','loop_back','merge'],core_edge_factor=1.0,approach_steps=(5,10),reuse_perimeter_anchors=True,spread_branch_anchors=True)
                g.update(seed=seed,region='plains');allocate(g,seed)
                # Smaller declared interface profile has its own finite currency
                # budget; full regional production policy stays unchanged.
                coins=[a for a in g['reward_allocations']if a['kind']=='currency'];keep={a['id']for a in coins[:8]};g['reward_allocations']=[a for a in g['reward_allocations']if a['kind']!='currency'or a['id']in keep];g['principal_routes']=principal_routes(g,3);condition_types(g)
            else:
                folder=plan(name+'-full-plan',seed);g=json.loads((folder/'exploration.json').read_text());p=json.loads((folder/'policy.json').read_text())
            write(out/('input-'+str(index)+'.json'),dict(graph=g,policy=p))
            result=build(out/str(index),g,p,sources,attempts=2,seconds=30)
            row=dict(seed=seed,profile=p['id'],status='spatial_feasible'if result else'spatial_budget_unsatisfied',placements=len(result['modules'])if result else 0,physics='NOT_RUN',production_admitted=False,seconds=time.perf_counter()-started)
        except Exception as e:
            row=dict(seed=seed,status='rejected',error=str(e),traceback=traceback.format_exc(),physics='NOT_RUN',production_admitted=False,seconds=time.perf_counter()-started)
        rows.append(row);write(out/'summary.json',dict(rows=rows,production_admitted=False));print(json.dumps(row,ensure_ascii=False),flush=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source-protocol',required=True);a=p.parse_args();sources=json.loads(Path(a.source_protocol).read_text())['sources'];run(a.name,sources)
