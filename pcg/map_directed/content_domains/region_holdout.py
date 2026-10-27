"""Fresh noise on an immutable complete region, without regenerating the layout."""
import argparse,copy,json,random
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..block_grid.verify import verify
from ..block_grid.policy import load,review
from pcg.prototype.factory.core.engine import file_sha


def run(name,source):
    out=REPO/'pcg/results'/name;parent=REPO/source
    if out.exists():raise ValueError('immutable_region_holdout')
    out.mkdir();summary=json.loads((parent/'summary.json').read_text())
    if not summary.get('physics_all_passed',summary.get('all_passed',False)):raise ValueError('calibration_must_pass_before_fresh_holdout')
    compiled=json.loads((parent/'compiled.json').read_text());design=review(compiled['exploration_graph'],load());write(out/'design-review.json',design)
    if not design['ok']:
        write(out/'summary.json',dict(status='design_rejected',physics='NOT_RUN',physics_all_passed=False,regional_requirements_satisfied=False,design_errors=design['errors'],production_admitted=False));return out
    original=json.loads((parent/'cases.json').read_text())['cases'];rng=random.Random('exploration-graph-input-972613');cs=[]
    for c in original[:3]:
        for i in range(2):
            v=copy.deepcopy(c);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
    write(out/'protocol.json',dict(parent=source,compiled_sha256=file_sha(parent/'compiled.json'),cases_sha256=file_sha(parent/'cases.json'),stream='exploration-graph-input-972613',phase='fresh_holdout',geometry_regenerated=False,design_gate='block_grid.policy.review',production_admitted=False))
    write(out/'cases.json',dict(cases=cs));rows=[]
    for case,result,evidence in ContentEngine(out/'physics').run(cs,'full-region-fresh-input-noise'):
        a=verify(compiled,case,result);row=dict(id=case['id'],ok=a['ok'],physics_ok=result['ok'],reason=result['reason'],errors=a['errors'],failure=result.get('pilot',{}).get('failure'),ticks=result.get('ticks'),evidence=evidence);rows.append(row);write(out/'rows.json',rows);write(out/(case['id']+'-boundary-state.json'),a);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(status='physics_holdout_only',passed=sum(r['ok']for r in rows),total=len(rows),physics_all_passed=bool(rows)and all(r['ok']for r in rows),regional_requirements_satisfied=False,rows=rows,parent=source,production_admitted=False))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
