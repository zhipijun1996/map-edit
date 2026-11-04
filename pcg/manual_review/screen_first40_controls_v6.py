"""Bounded calibration screens; no held-out execution or geometry selection."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,math
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

AUTH='feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json'
def kill(enemy,x,y,number=12):
    result=[]
    for _ in range(number):
        rows=[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded_shot_ready',migration_goal=[x-5,y-4,10,8],timeout=240)),cmd('shoot',aim_cell=dict(kind='enemy',id=enemy)),cmd('wait',4)]
        for v in rows:v['skip_if_enemy_dead']=enemy
        result+=rows
    return result

def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];base=core.read(folder/'cases.json')['cases'][0];variants=[]
    if n=='35':
        c=copy.deepcopy(base);c['generation_rule']['registration_source']='pcg/manual_review/first40_r35_v4.py'
        p=c['control_plan'];c['control_plan']=kill(c['enemies'][0]['id'],150,932)+kill(c['enemies'][1]['id'],150,932,48)+p[:28]+kill(c['enemies'][2]['id'],400,380,16)+p[28:];c['max_frames']=3300;variants=[c]
    elif n=='36':
        for target in (538,540,542):
            c=copy.deepcopy(base);c['generation_rule']['registration_source']='pcg/manual_review/first40_r36_v4.py';p=c['control_plan'][:4];p[0]['target_x']=310;p[1]['trigger']['migration_goal']=[305,578,10,8]
            c['control_plan']=p+[dict(op='shoot',direction=[-1,0],height_threshold=548,trigger=dict(after=0,state='shot_ready_above',timeout=90)),cmd('jump_release'),dict(op='shoot',direction=[-1,0],height_threshold=560,brake_target_y=target,trigger=dict(after=0,state='shot_ready_below',timeout=120)),dict(op='settle',target_x=872,deadband=4,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded',timeout=240)),cmd('wait',20)];variants.append(c)
    else:
        for dy in (.55,.6,.65):
            c=copy.deepcopy(base);c['control_plan'][8]['target_x']=410;c['control_plan'][9]['trigger']['migration_goal']=[405,918,10,8];c['control_plan'][16]['target_x']=690;c['control_plan'][17]['trigger']['migration_goal']=[685,698,10,8];c['control_plan'][20]['direction']=[-math.sqrt(1-dy*dy),dy];variants.append(c)
    for i,c in enumerate(variants):c['id']+='-screen-v6-'+str(i)
    # Bind only the selected author/runtime before snapshot; no module file edit.
    original=physics.author_for(variants[0]);runner=physics.runner_for(variants[0],original)
    from pcg.prototype.workshop.engine import WorkshopEngine
    eng=WorkshopEngine(core.REPO/'pcg/results'/('approved-b040-'+n+'-control-screen-v6'),batch_size=24,extra_sources=[__file__,*physics.author_sources([original],runner)],runner_script=runner);physics.deduplicate_snapshot(eng.out)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=13*len(variants),variants=variants,calibrationSeed=271028410,selection='first clean-pass, six-of-six mild and at least four-of-six moderate candidate; formal regular thresholds unchanged',newIndependentHoldout=False,stopping='one bounded screen, no reroll'))
    expanded=[];labels={};counts=[0]*len(variants);levels=[dict(clean=0,mild=0,moderate=0)for _ in variants]
    for i,c in enumerate(variants):
        for level,number in [('clean',1),('mild',6),('moderate',6)]:
            for trial in range(number):
                v=instantiate(c,271028410,level,trial);expanded.append(v);labels[v['id']]=(i,level)
    rows=[]
    for c,r,e in eng.run(expanded,'bounded-calibration'):
        q=checked_purpose(original,c,r);i,level=labels[c['id']];counts[i]+=q['ok'];levels[i][level]+=q['ok'];rows.append(dict(variant=i,check=q,evidence=e));print(n,i,q['ok'],q['reasons'],flush=True)
    selected=next((v for i,v in enumerate(variants)if levels[i]['clean']==1 and levels[i]['mild']==6 and levels[i]['moderate']>=4),None);core.write(eng.out/'screen.json',dict(rows=rows,counts=counts,levelCounts=levels,selected=selected))

if __name__=='__main__':
    for r in core.read(AUTH)['rows']:
        if r['reviewId']in('35',):run(r)
