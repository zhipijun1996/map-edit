"""Negotiated WEST low outlet; the failed east-outlet demand stays unsatisfied.

Actual new port role/geometry/program/spec; original Cells and original quality.
"""
import argparse,copy,json
from pathlib import Path
from . import recipes_v2 as core
from . import produce_v2 as pipeline
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine as OriginalEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest

RECIPES=('refund-retreat-fork',)
def layouts(recipe,interface):
    if recipe not in RECIPES:raise ValueError('unsupported retreat demand')
    cs=core.layouts('refund-fork',interface)
    for c in cs:
        c['platforms'][2]=[-500,680,1600,60]
        next(p for p in c['ports']if p['id']=='C').update(position=[-450,662],normal=[-1,0])
        c['id']=c['id'].replace('refund-fork','refund-retreat-fork')
        c['layout_title']=f'回充登高或西侧避敌低路 / {len(c["ports"])}口'
        rid=c['route_spec']['id']
        if rid=='lower-exit':
            c['control_plan']=[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',12),wait_x(-205,-1),cmd('axis',value=0),ground(),settle(-450)]
        if rid=='reward-rejoin':
            c['control_plan']=c['control_plan'][:-2]+[cmd('axis',value=1),wait_x(600),cmd('axis',value=0),ground(),settle(-450)]
        if c['route_spec']['to_port']=='C':c.update(exit_port=[-450,662],goal=[-475,658,50,8])
        c['rule_parameters'].update(negotiated_low_exit='west lower retreat; original east outlet explicitly unsatisfied',recipe=recipe)
        c['generation_rule']=dict(id='plains50-ports/'+recipe,version=1,parameters=c['rule_parameters'])
    physical_keys=['capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports','reward_sites']
    uid=digest(dict(recipe=recipe,interface=interface,physical={k:cs[0].get(k,[])for k in physical_keys}))
    spec=copy.deepcopy(cs[0]['map_specification']);spec['id']=f'plains50/ports/{recipe}/{interface}'
    spec['objective']=dict(recipe=recipe,interface=interface,physical_layout_sha256=uid,branch_ports=cs[0]['ports'],superseded_demand='east lower outlet unsatisfied; this demand accepts west retreat')
    spec['ports']['required_normals']=[p['normal']for p in cs[0]['ports']]
    for c in cs:c.update(layout_uid=uid,map_specification=spec,idea_ids=['plains50-ports/refund-retreat-fork'])
    return cs

purpose=core.purpose
alternatives=core.alternatives

class BoundEngine(OriginalEngine):
    def __init__(self,*args,extra_sources=None,**kwargs):
        super().__init__(*args,extra_sources=list(extra_sources or [])+[Path(__file__),Path(core.__file__)],**kwargs)

def probe(name):
    engine=BoundEngine(ROOT/'results'/name);rows=[]
    write(engine.out/'protocol.json',dict(schema='pcg/negotiated-refund-retreat/v1',cases=6,maximum_real_cases=900,maximum_source_revisions=2,old_east='failed original regular calibration, not enrolled',new_spec='west retreat exit, original enemy/refund high rewards',independent_holdout_after_full_calibration=True))
    cases=[c for i in range(2)for c in layouts(RECIPES[0],i)];write(engine.out/'cases.json',dict(cases=cases))
    for c,r,e in engine.run(cases,'negotiated-retreat-probe'):
        p=purpose(c,r);rows.append(dict(id=c['id'],ok=p['ok'],reasons=p['reasons'],evidence=e));print(json.dumps(rows[-1]),flush=True)
    write(engine.out/'summary.json',dict(rows=rows,physics_cases=engine.sim.cases,new_candidates=0))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe','produce']);p.add_argument('--name',required=True);a=p.parse_args()
    if a.mode=='probe':probe(a.name)
    else:
        import sys
        pipeline.recipes=sys.modules[__name__];pipeline.WorkshopEngine=BoundEngine
        pipeline.run(a.name,only=RECIPES)
