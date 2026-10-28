"""Finite alternative-input search, retaining successes as bypass findings."""
import argparse,copy,json
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.content_routes.run import ContentEngine
from pcg.map_directed.woven_region.run import cases_for

def run(source,name):
    source=Path(source);out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_probe_exists')
    out.mkdir(parents=True);c=json.loads((source/'compiled.json').read_text());main=cases_for(c,'main')[0];variants=[]
    rules=[('tunnel-no-shot','Shoot behind',0,'omit'),('tunnel-up-shot','Shoot behind',0,'up'),
        ('tunnel-long-jump-up','Shoot behind',0,'long-up'),('refund-no-first-shot','Hit a real enemy',0,'omit'),
        ('refund-no-second-shot','Hit a real enemy',1,'omit'),('refund-single-horizontal','Hit a real enemy',0,'single-horizontal')]
    for name_,intent,ordinal,op in rules:
        v=copy.deepcopy(main);v['id']='content-probe-'+name_;leg=next(l for l in v['pilot_program']if l.get('action_intent','').startswith(intent));shots=[x for x in leg['control_plan']if x['op']=='shoot']
        if op=='omit':shots[ordinal]['op']='wait';shots[ordinal].pop('direction',None)
        if op in ['up','long-up']:shots[0]['direction']=[0,1]
        if op=='long-up':next(x for x in leg['control_plan']if x['op']=='jump_release')['trigger']['after']=20
        if op=='single-horizontal':
            shots[0]['direction']=[-1,0];shots[1]['op']='wait';shots[1].pop('direction',None)
            next(x for x in leg['control_plan']if x['op']=='jump_release')['trigger']['after']=20
        v['probe']=dict(modified_leg=leg['id'],hypothesis=name_,whole_world=True,no_goal_action_requirement=True);variants.append(v)
    variants+=cases_for(c,'negative');write(out/'cases.json',dict(cases=variants));write(out/'compiled.json',c)
    write(out/'protocol.json',dict(candidates=len(variants),fixed_rules=rules,retries=0,selection_used=False,
        scope='Finite cheaper strategies in the actual complete world. A successful alternative is retained, not relabelled a failure.'))
    engine=ContentEngine(out/'physics');rows=[]
    for v,r,ev in engine.run(variants,'alternatives'):
        probe=v.get('probe')or v.get('counterfactual');legid=probe.get('modified_leg',probe.get('omitted_leg'));index=next(i for i,l in enumerate(v['pilot_program'])if l['id']==legid)
        row=dict(id=v['id'],route_completed=r['ok'],reached_modified_leg=r['pilot']['legs_completed']>=index,reason=r['reason'],ticks=r['ticks'],shots=r['shots'],probe=probe,evidence=ev)
        rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(completed=len(rows)==len(variants),rows=rows,cheaper_route_findings=[r['id']for r in rows if r['route_completed']],
        scope='Not a proof of universal necessity or non-bypass',production_admitted=False))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--name',required=True);a=p.parse_args();run(a.source,a.name)
