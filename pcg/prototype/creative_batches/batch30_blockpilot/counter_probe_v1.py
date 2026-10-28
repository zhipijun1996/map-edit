"""A small preregistered cheap-route precheck; full counters remain upstream."""
import argparse,json
from pathlib import Path
from . import api_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

HERE=Path(__file__).parent
INDICES=[0,13,16,17,25,29,33]

def run(name):
    out=ROOT/'results'/name
    if out.exists():raise ValueError('immutable_block_counter_run')
    e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT)
    cases=[v for i in [0,1]for j,v in enumerate(rules.alternatives(rules.layouts(rules.RECIPES[0],i)[0]))if j in INDICES]
    write(out/'protocol.json',dict(maximum_cases=14,predeclared_counter_indices=INDICES,complete_full_counter_count_per_route=34,full_gate_not_replaced=True))
    write(out/'source-cases.json',dict(cases=cases));rows=[]
    for c,r,v in e.run(cases,'block-counter-precheck'):
        q=rules.purpose(c,r)
        same=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
        rows.append(dict(id=c['id'],kind=c['counterexample_kind'],same_external_goal=same,invalidates_design=same and not q['ok'],purpose=q,evidence=v,result_summary={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']}))
        write(out/'rows.json',rows);print(json.dumps(dict(id=c['id'],same_external_goal=same,invalidates_design=rows[-1]['invalidates_design']),ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(actual_physics_cases=e.sim.cases,same_goal=sum(x['same_external_goal']for x in rows),design_refutations=sum(x['invalidates_design']for x in rows),full_counter_and_holdout='NOT_RUN',new_modules=0,production_admitted=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
