"""Bounded calibration screens; no held-out execution or geometry selection."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,math
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

AUTH='feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json'
def kill(enemy,x,y):
    result=[]
    for _ in range(12):
        rows=[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded',migration_goal=[x-5,y-4,10,8],timeout=240)),dict(op='wait',trigger=dict(state='grounded_shot_ready',timeout=150)),cmd('shoot',aim_cell=dict(kind='enemy',id=enemy)),cmd('wait',12)]
        for v in rows:v['skip_if_enemy_dead']=enemy
        result+=rows
    return result

def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];base=core.read(folder/'cases.json')['cases'][0];variants=[]
    if n=='35':
        c=copy.deepcopy(base);c['generation_rule']['registration_source']='pcg/manual_review/first40_r35_v3.py'
        p=c['control_plan'];c['control_plan']=kill(c['enemies'][0]['id'],150,932)+kill(c['enemies'][1]['id'],150,932)+p[:28]+kill(c['enemies'][2]['id'],430,380)+p[28:];c['max_frames']=3000;variants=[c]
    elif n=='36':
        for dy in (.20,.23,.26):
            c=copy.deepcopy(base);c['generation_rule']['registration_source']='pcg/manual_review/first40_r36_v3.py'
            c['control_plan']=[dict(op='settle',target_x=240,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded',migration_goal=[235,578,10,8],timeout=480)),cmd('axis',value=1),cmd('shoot',direction=[-1,0]),dict(op='shoot',direction=[-math.sqrt(1-dy*dy),dy],trigger=dict(after=0,state='shot_ready',timeout=120)),dict(op='shoot',direction=[-1,0],trigger=dict(after=0,state='shot_ready',timeout=120)),dict(op='settle',target_x=872,deadband=4,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded',timeout=240)),cmd('wait',20)]
            variants.append(c)
    else:
        for dy in (.55,.6,.65):
            c=copy.deepcopy(base);c['control_plan'][8]['target_x']=410;c['control_plan'][9]['trigger']['migration_goal']=[405,918,10,8];c['control_plan'][16]['target_x']=690;c['control_plan'][17]['trigger']['migration_goal']=[685,698,10,8];c['control_plan'][20]['direction']=[-math.sqrt(1-dy*dy),dy];variants.append(c)
    for i,c in enumerate(variants):c['id']+='-screen-v3-'+str(i)
    # Bind only the selected author/runtime before snapshot; no module file edit.
    original=physics.author_for(variants[0]);runner=physics.runner_for(variants[0],original)
    from pcg.prototype.workshop.engine import WorkshopEngine
    eng=WorkshopEngine(core.REPO/'pcg/results'/('approved-b040-'+n+'-control-screen-v3'),batch_size=24,extra_sources=[__file__,*physics.author_sources([original],runner)],runner_script=runner);physics.deduplicate_snapshot(eng.out)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=7*len(variants),variants=variants,calibrationSeed=271028405,selection='first all-pass candidate, one clean and six moderate trials each',newIndependentHoldout=False,stopping='one bounded screen, no reroll'))
    expanded=[];labels={};counts=[0]*len(variants)
    for i,c in enumerate(variants):
        for level,number in [('clean',1),('moderate',6)]:
            for trial in range(number):
                v=instantiate(c,271028405,level,trial);expanded.append(v);labels[v['id']]=i
    rows=[]
    for c,r,e in eng.run(expanded,'bounded-calibration'):
        q=checked_purpose(original,c,r);i=labels[c['id']];counts[i]+=q['ok'];rows.append(dict(variant=i,check=q,evidence=e));print(n,i,q['ok'],q['reasons'],flush=True)
    selected=next((v for i,v in enumerate(variants)if counts[i]==7),None);core.write(eng.out/'screen.json',dict(rows=rows,counts=counts,selected=selected))

if __name__=='__main__':
    for r in core.read(AUTH)['rows']:
        if r['reviewId']in('35','36'):run(r)
