"""Larger spatial separation for a folded region, preserving positive directions."""
import argparse,json
from .stack_landforms import return_fork
from .mirror import mirror
from .junction_probe import cases
from .engine import ContentEngine
from ..director import REPO
from ..run import write


def run(name,row=-6):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_drop_fork_probe')
    out.mkdir();ms=[return_fork(row,flag)for flag in [False,True]];ms+= [mirror(m)for m in ms[:]]
    cs=[c for m in ms for c in cases(m)];write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));rows=[];engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'regional-cliff-drop'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--row',type=int,default=-6);a=p.parse_args();run(a.name,a.row)
