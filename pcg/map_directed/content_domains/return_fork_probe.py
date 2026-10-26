"""Three route fork and finite cheap reverse attempts on the same real terrain."""
import argparse,copy,json
from .stack_landforms import return_fork
from .junction_probe import cases
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from pcg.prototype.workshop.rules import cmd,settle


def run(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_three_route_fork')
    out.mkdir();m=return_fork();cs=cases(m);positive={c['id']for c in cs}
    for hold in [1,8,18,30]:
        for aim in [.6,.8,1.0]:
            c=copy.deepcopy(m['case']);start=m['ports']['upper']['dock'];end=m['ports']['ingress']['dock'];plan=[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',2,direction=[(1-aim*aim)**.5,aim]),settle(end['position'][0],8)]
            c.update(id='reverse-counterexample/'+str(hold)+'/'+str(aim),spawn=start['position'],entry_port=start['position'],exit_port=end['position'],goal=end['region'],pilot_program=[dict(id='test-reverse',edge_id='not-declared',kind='module',target=end,control_plan=plan,budget_ticks=900)],map_budget_ticks=1800,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'));cs.append(c)
    write(out/'modules.json',[m]);write(out/'cases.json',dict(cases=cs));rows=[];engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'three-route-fork-and-reverse-search'):
        row=dict(id=c['id'],ok=r['ok'],positive=c['id']in positive,reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(positive_passed=sum(r['ok']for r in rows if r['positive']),positive_total=len(positive),reverse_successes=sum(r['ok']for r in rows if not r['positive']),reverse_attempts=len(cs)-len(positive),reverse_proof='Finite attempts only; not a universal no-path claim',production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
