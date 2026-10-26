"""Finite new folding interfaces, including reflected geometry, real Motor only."""
import argparse,json
from .stack_landforms import cliff_fork,lower_merge
from .mirror import mirror
from .junction_probe import cases
from .engine import ContentEngine
from ..director import REPO
from ..run import write


def run(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_fold_probe')
    out.mkdir();original=[cliff_fork(),cliff_fork(True),lower_merge(),lower_merge(True)];ms=original+[mirror(m)for m in original]
    cs=[c for m in ms for c in cases(m)];write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'folding-landform-directions'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
