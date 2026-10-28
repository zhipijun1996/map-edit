"""Bounded calibration screens; no held-out execution or geometry selection."""
import copy,math
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

AUTH='feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json'
def kill(enemy):
    result=[]
    for _ in range(8):
        rows=[dict(op='wait',trigger=dict(state='grounded_shot_ready',timeout=150)),cmd('shoot',aim_cell=dict(kind='enemy',id=enemy)),cmd('wait',12)]
        for v in rows:v['skip_if_enemy_dead']=enemy
        result+=rows
    return result

def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];base=core.read(folder/'cases.json')['cases'][0];variants=[]
    if n=='35':
        c=copy.deepcopy(base);c['generation_rule']['registration_source']='pcg/manual_review/first40_r35_v2.py'
        p=c['control_plan'];c['control_plan']=kill(c['enemies'][0]['id'])+kill(c['enemies'][1]['id'])+p[:28]+kill(c['enemies'][2]['id'])+p[28:];variants=[c]
    elif n=='36':
        for delay,dy in ((13,.12),(14,.16),(15,.12)):
            c=copy.deepcopy(base);c['control_plan'][0]['target_x']=284;c['control_plan'][1]['trigger']['migration_goal']=[279,578,10,8];c['control_plan'][4]['trigger']['after']=2;c['control_plan'][6]['trigger']['after']=delay
            for i in (5,6):c['control_plan'][i]['direction']=[-math.sqrt(1-dy*dy),dy]
            variants.append(c)
    else:
        for dy in (.55,.6,.65):
            c=copy.deepcopy(base);c['control_plan'][20]['direction']=[-math.sqrt(1-dy*dy),dy];variants.append(c)
    for i,c in enumerate(variants):c['id']+='-screen-v1-'+str(i)
    # Bind only the selected author/runtime before snapshot; no module file edit.
    original=physics.author_for(variants[0]);runner=physics.runner_for(variants[0],original)
    from pcg.prototype.workshop.engine import WorkshopEngine
    eng=WorkshopEngine(core.REPO/'pcg/results'/('approved-b040-'+n+'-control-screen-v1'),batch_size=24,extra_sources=[__file__,*physics.author_sources([original],runner)],runner_script=runner);physics.deduplicate_snapshot(eng.out)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=7*len(variants),variants=variants,calibrationSeed=271028403,selection='first all-pass candidate, one clean and six moderate trials each',newIndependentHoldout=False,stopping='one bounded screen, no reroll'))
    expanded=[];labels={};counts=[0]*len(variants)
    for i,c in enumerate(variants):
        for level,number in [('clean',1),('moderate',6)]:
            for trial in range(number):
                v=instantiate(c,271028403,level,trial);expanded.append(v);labels[v['id']]=i
    rows=[]
    for c,r,e in eng.run(expanded,'bounded-calibration'):
        q=checked_purpose(original,c,r);i=labels[c['id']];counts[i]+=q['ok'];rows.append(dict(variant=i,check=q,evidence=e));print(n,i,q['ok'],q['reasons'],flush=True)
    selected=next((v for i,v in enumerate(variants)if counts[i]==7),None);core.write(eng.out/'screen.json',dict(rows=rows,counts=counts,selected=selected))

if __name__=='__main__':
    for r in core.read(AUTH)['rows']:
        if r['reviewId']in('35','36','37'):run(r)
