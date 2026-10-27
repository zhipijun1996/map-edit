"""One immutable run from the existing policy graph to native whole-world tests."""
import argparse,copy,json,time,traceback,random
from pathlib import Path
from .build import build
from .cases import create
from .engine import GraphMapEngine
from ..block_grid.policy import load
from ..block_grid.verify import verify
from ..director import REPO
from ..run import write
from ..library import CandidateLibrary


def run(name,graph,policy,sources,attempts=4,seconds=60,preselected=None):
    out=REPO/'pcg/results'/name;started=time.perf_counter();c=build(out,graph,policy,sources,attempts,seconds,preselected)
    if c is None:return out
    cs=create(c);write(out/'cases.json',dict(cases=cs));rows=[];audits=[];engine=GraphMapEngine(out/'physics')
    for case,r,e in engine.run(cs,'same-graph-whole-map'):
        a=verify(c,case,r);audits.append(dict(id=case['id'],**a));write(out/'boundary-state-verification.json',audits)
        row=dict(id=case['id'],ok=a['ok'],physics_ok=r['ok'],reason=r['reason'],boundary_errors=a['errors'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','ok','physics_ok','reason','boundary_errors','ticks','failure']},ensure_ascii=False),flush=True)
    summary=dict(status='finite_whole_map_pass'if all(r['ok']for r in rows)else'whole_map_failed',passed=sum(r['ok']for r in rows),total=len(cs),macro_placements=len(c['modules']),actual_module_components=sum(max(1,len(m.get('content_components',[])))for m in c['modules']),principal_routes=len(c['exploration_graph'].get('principal_routes',[])),branch_kinds=sorted({b['kind']for b in graph['branches']}),seconds=time.perf_counter()-started,all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),production_admitted=False,human_fun='UNREVIEWED',bypass_proof='NOT_RUN',economic_balance='UNCALIBRATED',human_minutes='UNKNOWN')
    write(out/'summary.json',summary)
    if summary['all_passed']:write(out/'candidate-enrollment.json',dict(records=CandidateLibrary().enroll_payloads(out),production_admitted=False))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--plan',type=Path,required=True);p.add_argument('--sources',nargs='+',required=True);p.add_argument('--seconds',type=int,default=60);p.add_argument('--attempts',type=int,default=4);a=p.parse_args();g=json.loads((a.plan/'exploration.json').read_text());policy=load(a.plan/'policy.json');print(run(a.name,g,policy,a.sources,a.attempts,a.seconds))
