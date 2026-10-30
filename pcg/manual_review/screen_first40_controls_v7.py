"""One bounded correction of final dock jump; no geometry/holdout selection."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def main():
    base=core.read('pcg/manual_review/implementation/first-40-final-v1/game-challenge-ferry-ascent/cases.json')['cases'][0]
    variants=[]
    for x in (940,936,944):
        c=copy.deepcopy(base);c['id']+='-dock-screen-v7-'+str(x)
        c['generation_rule']['registration_source']='pcg/manual_review/first40_r35_v5.py'
        p=c['control_plan'];p[-9]['target_x']=x;p[-8]['trigger']['dynamic']['value']=x-2
        p[-4]=dict(op='jump_release',height_threshold=8,trigger=dict(state='height_at_most',timeout=40))
        p[-5:-5]=[dict(op='settle',target_x=1000,deadband=4,trigger=dict(after=0))]
        variants.append(c)
    author=physics.author_for(variants[0]);runner=physics.runner_for(variants[0],author)
    eng=WorkshopEngine(core.REPO/'pcg/results/approved-b040-35-control-screen-v7',batch_size=24,extra_sources=[__file__,*physics.author_sources([author],runner)],runner_script=runner)
    physics.deduplicate_snapshot(eng.out)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=75,variants=variants,calibrationSeed=271028411,selection='first clean and all 12 mild and at least 10 of 12 moderate; unchanged formal thresholds',newIndependentHoldout=False,stopping='one bounded screen'))
    expanded=[];labels={};levels=[dict(clean=0,mild=0,moderate=0)for _ in variants];rows=[]
    for i,c in enumerate(variants):
        for level,number in [('clean',1),('mild',12),('moderate',12)]:
            for trial in range(number):
                v=instantiate(c,271028411,level,trial);expanded.append(v);labels[v['id']]=(i,level)
    for c,r,e in eng.run(expanded,'bounded-dock-calibration'):
        q=checked_purpose(author,c,r);i,level=labels[c['id']];levels[i][level]+=q['ok'];rows.append(dict(variant=i,check=q,evidence=e));print(i,level,q['ok'],q['reasons'],flush=True)
    selected=next((v for i,v in enumerate(variants)if levels[i]['clean']==1 and levels[i]['mild']==12 and levels[i]['moderate']>=10),None)
    core.write(eng.out/'screen.json',dict(rows=rows,levelCounts=levels,selected=selected));print(levels,flush=True)

if __name__=='__main__':main()
