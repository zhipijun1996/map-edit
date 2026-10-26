"""Small, explicitly bounded contact-grammar experiment on existing consumers."""
import argparse,copy,json,random,time,traceback
from pathlib import Path
from .reentrant_fixture import build,prepare_cases
from .run import FeedEngine
from ..director import REPO
from ..run import write
from ..shape_search.search import translated

def run(name,seed,source=None,held=False,indices=None,negative=False,regression_source=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_experiment_exists')
    out.mkdir(parents=True);started=time.perf_counter()
    write(out/'protocol.json',dict(seed=seed,source=source,held=held,shape_attempts=3,search_budget_per_attempt=50000,
        world_resets_within_route=0,added_map_terrain=0,automatic_retries=0,
        scope='Bounded rock-well contact grammar with existing action library; not unrestricted regional topology generation',
        evaluation_seeds=['contact-grammar-eval-0','contact-grammar-eval-1','contact-grammar-eval-2'],
        holdout_seed='contact-grammar-input-99109',previous_failed_holdouts_now_calibration=['contact-grammar-input-77319','contact-grammar-input-88241'],production_admitted=False))
    try:
        c=json.loads((Path(source)/'compiled.json').read_text())if source else build(out,seed)
        if source:write(out/'compiled.json',c)
        write(out/'map-recipe.json',dict(schema='pcg/direct-module-map-recipe/v1',seed=seed,
            modules=[dict(instance=m['id'],document=m['canonical_document'],placement=m['spec']['placement'])for m in c['modules']],
            seams=c['seams'],hard_checks=c['hard_checks']))
        cs=prepare_cases(c)
        if indices is not None:cs=[cs[i]for i in indices]
        identities={'L0':'windmill_plateau','L1':'creek_well','L2':'creek_well','R0':'clock_court','R1':'repair_gallery','R2':'clock_court'}
        identities.update(L3='repair_gallery',R3='creek_well')
        for v in cs:
            v['preview_title']='风铃平原 · 岩井回环样图 / 趣味待评'
            v['presentation_areas']=[dict(id=k,identity=identities[k],position=n['center']['position'])for k,n in c['nodes'].items()if k in identities]
            v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m.get('action_clearance',[])]
            v['presentation_keep_clear'] += [[n['center']['position'][0]-42,n['center']['position'][1]-65,84,90]for n in c['nodes'].values()]
        if regression_source:
            prior=Path(regression_source);bad={r['id']for r in json.loads((prior/'rows.json').read_text())if not r['ok']}
            prior_cases=[v for v in json.loads((prior/'cases.json').read_text())['cases']if v['id']in bad]
            current={v['id']:v for v in cs};extra=[]
            for old in prior_cases:
                base=old['id'].split('-held-')[0];v=copy.deepcopy(current[base]);v['id']='regression-'+old['id'];v['noise']=copy.deepcopy(old['noise']);v['calibration_replay_of_failed_holdout']=str(prior);extra.append(v)
            cs+=extra
        if held:
            rng=random.Random('contact-grammar-input-99109/'+seed);extra=[]
            for original in cs[:3]:
                for i in range(2):
                    v=copy.deepcopy(original);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1)
                    v['holdout']=True;extra.append(v)
            cs+=extra
        if negative:
            original=cs[0];cs=[]
            for hold in [None,24]:
                v=copy.deepcopy(original);v['id']+='-omit-recoil'+('-long-jump'if hold else'')
                for leg in v['pilot_program']:
                    for op in leg.get('control_plan',[]):
                        if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
                        if hold and op['op']=='jump_release':op['trigger']['after']=hold
                v['counterfactual']='Same whole world and destination; omit gun recoil, optionally extend jump hold';cs.append(v)
        write(out/'cases.json',dict(cases=cs));engine=FeedEngine(out/'physics');rows=[]
        for case,r,ev in engine.run(cs,'reentrant-contact'):
            row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=ev)
            rows.append(row);write(out/'rows.json',rows)
            print(json.dumps({k:row[k]for k in ['id','ok','reason','ticks','shots','failure']},ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),passed=sum(r['ok']for r in rows),total=len(cs),rows=rows,wall_seconds=time.perf_counter()-started,human_fun='unreviewed',production_admitted=False))
    except Exception as error:
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--source');p.add_argument('--held',action='store_true');p.add_argument('--negative',action='store_true');p.add_argument('--indices',nargs='+',type=int);p.add_argument('--regression-source');a=p.parse_args();print(run(a.name,a.seed,a.source,a.held,a.indices,a.negative,a.regression_source))
