"""Fixed-budget clean discovery; no holdout sampling or admission here."""
import argparse,json
from .engine import ROOT,WorkshopEngine
from .rules import FAMILIES,candidates,specifications,generate

def run(name,families=None):
    engine=WorkshopEngine(ROOT/'results'/name);rows=[]
    cs=[c for f in families or FAMILIES for v in range(2)for c in candidates(f,v)]
    (engine.out/'challenge-specifications.json').write_text(json.dumps(specifications(),ensure_ascii=False,indent=2))
    (engine.out/'protocol.json').write_text(json.dumps(dict(scope='calibration only',candidates=len(cs),selection_used=False)))
    for c,r,e in engine.run(cs,'calibration'):
        row=dict(case=c,result=r,evidence=e);rows.append(row)
        print(json.dumps(dict(id=c['id'],ok=r['ok'],reason=r['reason'],last=[r['frames'][-1][k]for k in ['x','y','grounded']]if r.get('frames')else None,shots=r.get('shots'),events=r.get('plains',{}).get('events',[]),workshop=r.get('workshop')),ensure_ascii=False),flush=True)
    (engine.out/'calibration.json').write_text(json.dumps(rows))
    return engine.out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--families',nargs='+',choices=FAMILIES);a=p.parse_args();run(a.name,a.families)
