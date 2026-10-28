"""Small real Godot qualification of shared 3/4-port layouts."""
import argparse,json
from pathlib import Path
from . import recipes_v1 as recipes
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

def run(name):
    engine=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),Path(recipes.__file__)])
    cases=[c for recipe in recipes.RECIPES for i in range(2)for c in recipes.layouts(recipe,i)]
    write(engine.out/'protocol.json',dict(stage='probe only; NOT admission',cases=len(cases),calibration_seed=261026500,holdout_seed=261026501,max_source_revisions=2,real_case_budget_per_proposal=900))
    write(engine.out/'cases.json',dict(cases=cases));rows=[]
    for c,r,e in engine.run(cases,'multiport-probe'):
        p=recipes.purpose(c,r);row=dict(id=c['id'],ok=p['ok'],purpose=p,evidence=e,last=({k:r['frames'][-1].get(k)for k in ['x','y','support_id']}if r.get('frames')else{}),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'))
        rows.append(row);print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(rows=rows,passed=sum(r['ok']for r in rows),cases=len(rows),new_modules=0));return engine.out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
