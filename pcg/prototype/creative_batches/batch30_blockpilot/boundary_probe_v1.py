"""Original-Godot exact boundary fixture probes; no production admission."""
import argparse,json
from pathlib import Path
from . import boundary_v1 as fixture
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate

def run(name,levels):
    out=ROOT/'results'/name
    if out.exists():raise ValueError('immutable_boundary_probe')
    e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(fixture.__file__),*fixture.SOURCE_DEPENDENCIES],runner_script=fixture.RUNNER_SCRIPT)
    base=fixture.case();cases=[v for level in levels for v in ([base]if level=='clean'else[instantiate(base,261040101,level,i)for i in range(6)])]
    write(out/'protocol.json',json.loads((Path(__file__).parent/'boundary-protocol-v1.json').read_text()));write(out/'source-cases.json',dict(cases=cases));rows=[]
    for c,r,b in e.run(cases,'exact-boundary'):
        q=fixture.purpose(c,r);rows.append(dict(id=c['id'],purpose=q,evidence=b,result_summary={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']}));write(out/'rows.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons']),ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(actual_physics_cases=e.sim.cases,passed=sum(x['purpose']['ok']for x in rows),total=len(rows),new_modules=0,mirror_challenge='UNKNOWN',generic_seams='UNKNOWN',production_admitted=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--levels',nargs='+',default=['clean'],choices=['clean','mild','moderate']);a=p.parse_args();run(a.name,a.levels)
