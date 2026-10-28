import argparse,json
from .engine import ROOT,WorkshopEngine
from .production_recipes import RECIPES,candidates,purpose
from .experiments import write

def run(name):
    e=WorkshopEngine(ROOT/'results'/name);cs=[c for recipe in RECIPES for interface in range(2)for c in candidates(recipe,interface)];rows=[]
    write(e.out/'protocol.json',dict(stage='clean discovery only',maximum_cases=len(cs),candidate_selection='first clean-purpose pass per interface, then cheap counterexamples; not admission'))
    for c,r,ev in e.run(cs,'clean-screen'):
        p=purpose(c,r);rows.append(dict(case=c,purpose=p,result=r,evidence=ev));print(json.dumps(dict(id=c['id'],ok=p['ok'],reasons=p['reasons'],last=[r['frames'][-1][k]for k in ['x','y']]if r.get('frames')else None)),flush=True)
    write(e.out/'rows.json',rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
