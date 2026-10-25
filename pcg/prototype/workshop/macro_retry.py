"""Deliberate missed pocket -> lower recovery -> repeat, one physical world."""
import argparse,copy,json
from .macro import macro_cases,recipe,purpose
from .engine import ROOT,HERE,WorkshopEngine
from .rules import cmd,ground,wait_x,settle
from .evaluate import instantiate
from .experiments import write
from ..factory.core.quality import digest,module_hash

def fixtures():
    out=[]
    for v in range(2):
        routes,_=macro_cases(v);c=copy.deepcopy(routes[0]);a,b=recipe(v)
        shots=[i for i,s in enumerate(c['control_plan'])if s['op']=='shoot'];i=shots[1]
        c['control_plan'][i]=dict(op='wait',trigger=copy.deepcopy(c['control_plan'][i]['trigger']))
        retry_gate=[settle(a['exit_port'][0]),wait_x(205),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,aim_cell=dict(kind='bell',id='short-bell')),ground(),cmd('wait',20)]
        lip=b['platforms'][0][0]+b['platforms'][0][2]
        retry_brake=[settle(lip+120),wait_x(lip+105),cmd('shoot',direction=[.9886859966642595,.15]),settle(b['exit_port'][0]),ground(),cmd('wait',20)]
        c['control_plan']+=[ground(),cmd('wait',20)]+routes[3]['control_plan']+[ground(),cmd('wait',20)]+retry_gate+retry_brake
        c['id']+='-miss-and-retry';c['max_frames']=1800;c['retry_fixture']=True;out.append(c)
    return out

def check(c,r):
    p=purpose(c,r);reasons=p['reasons'][:];frames=r.get('frames',[]);events=r.get('workshop',{}).get('events',[])
    cache=next((e['frame']for e in events if e['type']=='chest_claim'and e['id']=='brake-cache'),None)
    lower=recipe(c['rule_parameters']['variant'])[0]['platforms'][3][1]-18
    missed=[f['frame']for f in frames if f['grounded']and abs(f['y']-lower)<1 and (cache is None or f['frame']<cache)]
    regained=[f['frame']for f in frames if missed and f['frame']>missed[0]and f['grounded']and abs(f['x']-80)<25 and abs(f['y']-420)<1 and (cache is None or f['frame']<cache)]
    opens=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open']
    if not missed or not regained or cache is None or len(opens)<2:reasons.append('same_world_miss_recovery_retry_missing')
    claims=[e['id']for e in events if e['type']=='chest_claim'and e['accepted']]
    if claims!=['gate-cache','brake-cache']:reasons.append('reward_repeated_or_wrong_order')
    return dict(ok=not reasons,reasons=reasons,first_missed_bank=missed[0]if missed else None,regained_original_shore=regained[0]if regained else None,second_cache_frame=cache,original_bell_opens=len(opens),claimed_ids=claims)

def run(name,holdout=False):
    engine=WorkshopEngine(ROOT/'results'/name);protocol=json.loads((HERE/'protocol-macro-port-v3.json').read_text());seed=protocol['continuous_holdout_seed']if holdout else protocol['calibration_seed']
    write(engine.out/'protocol.json',dict(parent=protocol,scope='miss second shot, fall to lower bank, climb back, re-open original closed gate, retry second cache; no scene/resource/wallet reset',seed=seed,holdout=holdout,maximum_cases=26))
    cs=[]
    for base in fixtures():
        cs.append(base)
        for i in range(12):cs.append(instantiate(base,seed,'mild',i))
    rows=[];reviews=[];write(engine.out/'cases.json',dict(cases=cs))
    for c,r,e in engine.run(cs,'retry-holdout'if holdout else'retry-calibration'):
        p=check(c,r);rows.append(dict(id=c['id'],ok=p['ok'],check=p,reason=r['reason'],evidence=e));write(engine.out/'rows.json',rows)
        if p['ok']and '-mild-'not in c['id']:
            frozen=copy.deepcopy(c);frozen.update(factory_id=digest(c),factory_evidence=e,review_alias=c['id'],recorded_frames=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']]);frozen['module_sha256']=module_hash(frozen);reviews.append(frozen)
        print(json.dumps(rows[-1]),flush=True)
    write(engine.out/'review_cases.json',dict(cases=reviews));write(engine.out/'summary.json',dict(all_passed=all(r['ok']for r in rows),cases=len(rows),holdout=holdout,seed=seed,production_admitted=False))
    return engine.out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--holdout',action='store_true');a=p.parse_args();run(a.name,a.holdout)
