"""Observe corridor clearance, then use original vertical recoil to reach M."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

ROOT=core.REPO/'pcg/manual_review/implementation/first-40-repair17-v1/batch30-d04-0'
def main():
    eng,canonical,authors=physics._engine(ROOT,'approved-b040-17-return-control-screen-v1',physics.FULL_PROTOCOL);base=canonical[1];p=base['control_plan'];variants=[]
    # Replace the bridge-to-M block only; retain the real outward and later return.
    end=next(i for i,c in enumerate(p)if i>30 and c['op']=='settle'and c.get('target_x')==610)
    start=next(i for i,c in enumerate(p)if i>25 and c['op']=='settle'and c.get('target_x')==780)
    for x in (764,765,766):
        c=copy.deepcopy(base);q=[dict(op='settle',target_x=x,deadband=.5,trigger=dict(after=0)),wait_x(x+1,-1),ground(),cmd('wait',8),dict(op='axis',value=0,cancel_settle=True,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_y',direction='lte',value=400),timeout=120)),settle(650),ground(),cmd('wait',12)]
        c['control_plan']=p[:start]+q+p[end:];c['id']+='-corridor-'+str(x);variants.append(c)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=21,variants=variants,calibrationSeed=271028406,selection='first all-seven-pass candidate; one clean and six moderate each',newIndependentHoldout=False))
    expanded=[];labels={};counts=[0]*3;rows=[]
    for i,c in enumerate(variants):
        for level,num in [('clean',1),('moderate',6)]:
            for j in range(num):v=instantiate(c,271028406,level,j);expanded.append(v);labels[v['id']]=i
    for c,r,e in eng.run(expanded,'corridor-return-screen'):
        i=labels[c['id']];q=checked_purpose(authors[1],c,r);counts[i]+=q['ok'];rows.append(dict(variant=i,check=q,evidence=e));print(i,q['ok'],q['reasons'],flush=True)
    core.write(eng.out/'screen.json',dict(counts=counts,rows=rows,selected=next((c for i,c in enumerate(variants)if counts[i]==7),None)))
if __name__=='__main__':main()
