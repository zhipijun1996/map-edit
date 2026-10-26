"""Fresh noise on an immutable complete region, without regenerating the layout."""
import argparse,copy,json,random
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..block_grid.verify import verify
from pcg.prototype.factory.core.engine import file_sha


def run(name,source):
    out=REPO/'pcg/results'/name;parent=REPO/source
    if out.exists():raise ValueError('immutable_region_holdout')
    out.mkdir();summary=json.loads((parent/'summary.json').read_text())
    if not summary['all_passed']:raise ValueError('calibration_must_pass_before_fresh_holdout')
    compiled=json.loads((parent/'compiled.json').read_text());original=json.loads((parent/'cases.json').read_text())['cases'];rng=random.Random('folded-region-input-972613');cs=[]
    for c in original[:3]:
        for i in range(2):
            v=copy.deepcopy(c);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
    write(out/'protocol.json',dict(parent=source,compiled_sha256=file_sha(parent/'compiled.json'),cases_sha256=file_sha(parent/'cases.json'),stream='folded-region-input-972613',phase='fresh_holdout',geometry_regenerated=False,production_admitted=False))
    write(out/'cases.json',dict(cases=cs));rows=[]
    for case,result,evidence in ContentEngine(out/'physics').run(cs,'full-region-fresh-input-noise'):
        a=verify(compiled,case,result);row=dict(id=case['id'],ok=a['ok'],physics_ok=result['ok'],reason=result['reason'],errors=a['errors'],failure=result.get('pilot',{}).get('failure'),ticks=result.get('ticks'),evidence=evidence);rows.append(row);write(out/'rows.json',rows);write(out/(case['id']+'-boundary-state.json'),a);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),all_passed=all(r['ok']for r in rows),rows=rows,parent=source,production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
