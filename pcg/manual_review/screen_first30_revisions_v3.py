"""Predeclared bounded control-only screen, never held-out seed selection."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .finalize_first30_v1 import AUTH,folder_for

def run(n):
    row=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']==n);folder=folder_for(row)
    eng,cases,authors=physics._engine(folder,'approved-b001-first30-'+n+'-control-screen-v3',physics.FULL_PROTOCOL);base=cases[0];variants=[]
    for i,value in enumerate((515,520,525)if n=='07'else(824,850,880)):
        c=copy.deepcopy(base);c['id']+='-screen-'+str(value)
        if n=='07':c['control_plan'][4]['trigger']['dynamic']['value']=value
        else:
            c['control_plan'].insert(10,dict(op='settle',target_x=value,deadband=4,trigger=dict(after=0)))
            for v in c['control_plan'][11:]:
                if v['op']=='axis':v['cancel_settle']=True
        variants.append(c)
    core.write(eng.out/'screen-protocol.json',dict(variants=variants,seed=271028701,maximumAttempts=21,perVariant=dict(clean=1,moderate=6),selection='first variant with all seven checks passing; no held-out observations',stopping='one screen; preserve failed candidates; no reroll'))
    allcases=[];labels={}
    for i,c in enumerate(variants):
        for level,count in [('clean',1),('moderate',6)]:
            for j in range(count):
                v=instantiate(c,271028701,level,j);allcases.append(v);labels[v['id']]=i
    counts=[0]*3;rows=[]
    for c,r,e in eng.run(allcases,'bounded-control-calibration'):
        q=checked_purpose(authors[0],c,r);index=labels[c['id']];counts[index]+=bool(q['ok']);rows.append(dict(variant=index,check=q,evidence=e));print(n,index,q['ok'],q['reasons'],flush=True)
    selected=next((variants[i]for i,count in enumerate(counts)if count==7),None)
    core.write(eng.out/'screen.json',dict(counts=counts,rows=rows,selected=selected))

if __name__=='__main__':
    for n in ('10',):run(n)
