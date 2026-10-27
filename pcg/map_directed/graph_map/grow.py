"""Map gaps invoke the existing Workshop and real ordered-pair verifier."""
import argparse,json
from .engine import GraphMapEngine
from ..content_domains.junction_probe import cases
from ..director import REPO
from ..run import write
from pcg.prototype.workshop.production_loop import compile_request


def run(name,requests):
    out=REPO/'pcg/results'/name;out.mkdir(exist_ok=False);modules=[];responses=[]
    for request in requests:
        response=compile_request(request);responses.append(dict(request=request,status=response['status'],gaps=response.get('gaps',[]),variants=len(response.get('modules',[])),concept=response.get('concept')));modules+=response.get('modules',[])
    cs=[c for m in modules for c in cases(m)];write(out/'requests.json',requests);write(out/'generator-responses.json',responses);write(out/'modules.json',modules);write(out/'cases.json',dict(cases=cs));rows=[]
    write(out/'protocol.json',dict(candidate_variants=len(modules),directions=len(cs),consumer='existing Workshop + real original Motor',no_map_layout=True,production_admitted=False))
    engine=GraphMapEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'graph-demanded-macro'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),whole_map='NOT_RUN',production_admitted=False));return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--requests',required=True);a=p.parse_args();run(a.name,json.loads(open(a.requests).read()))
