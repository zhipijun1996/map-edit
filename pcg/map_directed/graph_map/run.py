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


def run(name,graph,policy,sources,attempts=4,seconds=60,preselected=None,calibration=False):
    out=REPO/'pcg/results'/name;started=time.perf_counter();c=build(out,graph,policy,sources,attempts,seconds,preselected)
    if c is None:return out
    return verify_world(out,c,graph,calibration,started)


def verify_world(out,c,graph,calibration=False,started=None):
    started=time.perf_counter()if started is None else started
    cs=create(c)
    if calibration:cs=cs[:1]
    write(out/'cases.json',dict(cases=cs));rows=[];audits=[];engine=GraphMapEngine(out/'physics')
    for case,r,e in engine.run(cs,'same-graph-whole-map'):
        a=verify(c,case,r);audits.append(dict(id=case['id'],**a));write(out/'boundary-state-verification.json',audits)
        row=dict(id=case['id'],ok=a['ok'],physics_ok=r['ok'],reason=r['reason'],boundary_errors=a['errors'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','ok','physics_ok','reason','boundary_errors','ticks','failure']},ensure_ascii=False),flush=True)
    summary=dict(rows=rows,calibration_only=calibration,status='finite_whole_map_pass'if all(r['ok']for r in rows)else'whole_map_failed',passed=sum(r['ok']for r in rows),total=len(cs),macro_placements=len(c['modules']),actual_module_components=sum(max(1,len(m.get('content_components',[])))for m in c['modules']),principal_routes=len(c['exploration_graph'].get('principal_routes',[])),branch_kinds=sorted({b['kind']for b in graph['branches']}),seconds=time.perf_counter()-started,all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),production_admitted=False,human_fun='UNREVIEWED',bypass_proof='NOT_RUN',economic_balance='UNCALIBRATED',human_minutes='UNKNOWN')
    write(out/'summary.json',summary)
    if summary['all_passed']and not calibration:write(out/'candidate-enrollment.json',dict(records=CandidateLibrary().enroll_payloads(out),production_admitted=False))
    return out


def reverify(name,source):
    import hashlib,shutil
    source=Path(source).resolve();out=REPO/'pcg/results'/name;out.mkdir(exist_ok=False,parents=True)
    for key in ['compiled.json','exploration.json','policy.json','precanonical.json','assembly-audit.json','input-binding.json','protocol.json']:
        if(source/key).exists():shutil.copy2(source/key,out/key)
    c=json.loads((out/'compiled.json').read_text())
    write(out/'reverification-source.json',dict(source=str(source.relative_to(REPO)),compiled_sha256=hashlib.sha256((source/'compiled.json').read_bytes()).hexdigest(),geometry_changed=False,reason='Fresh current observer and exact binary Router axis capture; no reference trace or Module edits'))
    return verify_world(out,c,c['exploration_graph'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);group=p.add_mutually_exclusive_group(required=True);group.add_argument('--plan',type=Path);group.add_argument('--compiled-run',type=Path);p.add_argument('--sources',nargs='+');p.add_argument('--seconds',type=int,default=60);p.add_argument('--attempts',type=int,default=4);a=p.parse_args()
    if a.compiled_run:print(reverify(a.name,a.compiled_run))
    else:
        if not a.sources:p.error('--sources is required for new materialization')
        g=json.loads((a.plan/'exploration.json').read_text());policy=load(a.plan/'policy.json');print(run(a.name,g,policy,a.sources,a.attempts,a.seconds))
