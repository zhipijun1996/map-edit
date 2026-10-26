"""One real Graph -> Block -> Module -> Godot pipeline, with bounded gaps."""
import argparse,copy,json,random,time,traceback
from pathlib import Path
from .build import build
from .engine import BlockEngine
from .verify import verify
from ..director import REPO,regional
from ..run import write
from ..catalog_feed.reentrant_fixture import prepare_cases
from ..region_scale.materialize import case_for
from ..shape_search.search import translated
from ..library import CandidateLibrary

def cases(c):
    cs=prepare_cases(c,protect_approach=True)
    g=c['exploration_graph'];first=cs[0]['r2_semantics']['logical_route'];blocked=frozenset([first[0]['edge_id']])
    _,nodes=regional.shortest_path(g,g['entry'],g['goal'],blocked)
    if not nodes:raise ValueError('no_distinct_second_main_route')
    steps=[]
    for a,b in zip(nodes,nodes[1:]):
        e=next(e for e in g['edges']if(e['from']==a and e['to']==b)or(e['bidirectional']and e['from']==b and e['to']==a));steps.append(dict(edge_id=e['id'],**{'from':a,'to':b}))
    v=case_for(c,steps,'alternate-main');v.update(extra_script=cs[0]['extra_script'],required_reward_ids=[],reward_claim_limit=2,maximum_coins=48)
    # Reuse the exact existing dynamic guard recipe from a covering tour.
    guarded=cs[3];guards={q['edge_id']:q for q in guarded['pilot_program']if q['id'].endswith('dynamic-seam-guard')}
    program=[]
    for leg in v['pilot_program']:
        if str(leg['target']['id']).startswith('seam/')and leg['edge_id']in guards:
            q=copy.deepcopy(guards[leg['edge_id']]);q.update(id=leg['id']+'-dynamic-seam-guard',edge_from=leg['edge_from'],edge_to=leg['edge_to']);program.append(q)
        program.append(leg)
    v['pilot_program']=program;cs.append(v)
    for v in cs:
        v.update(title='风铃平原 · Graph + Block128 + Module',preview_title='Block128直接拼接 / 独立整图验证',map_seed=g['seed'])
        v['presentation_areas']=[dict(id=k,identity='windmill_plateau'if k.endswith('0')else'creek_well',position=n['center']['position'])for k,n in c['nodes'].items()if k.startswith(('L','R'))]
        v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m['action_clearance']]
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
    return cs

def run(name,seed,source_index=2,held=False):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_block_map_exists')
    out.mkdir(parents=True);start=time.perf_counter()
    write(out/'protocol.json',dict(seed=seed,block_size=128,source_graph=f'contact-grammar-evaluation-{source_index}-v3',maximum_search_expansions=50000,
        held=held,holdout_seed='block-input-24101',whole_world=True,world_resets_within_route=0,map_added_terrain=0,full_region_target=False,production_admitted=False))
    try:
        c=build(out,seed,REPO/f'pcg/results/contact-grammar-evaluation-{source_index}-v3',REPO/'pcg/results/block-grid-hub-probe-v2',REPO/'pcg/results/block-grid-source-probe-v5')
        if c is None:write(out/'summary.json',dict(status='unsatisfied',physics='NOT_RUN',production_admitted=False));return out
        cs=cases(c)
        if held:
            rng=random.Random('block-input-24101/'+seed)
            for original in [cs[0],cs[2],cs[4]]:
                for i in range(2):
                    v=copy.deepcopy(original);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
        write(out/'cases.json',dict(cases=cs));engine=BlockEngine(out/'physics');rows=[];audits=[]
        for case,r,e in engine.run(cs,'graph-block-module'):
            audit=verify(c,case,r);audits.append(dict(id=case['id'],**audit));write(out/'boundary-state-verification.json',audits)
            row=dict(id=case['id'],ok=audit['ok'],physics_ok=r['ok'],reason=r['reason'],block_errors=audit['errors'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e)
            rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','ok','physics_ok','reason','block_errors','ticks','failure']},ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),passed=sum(r['ok']for r in rows),total=len(cs),rows=rows,seconds=time.perf_counter()-start,
            scope='Block-native technical pilot. Does not satisfy full region scale, human time, major-item economy or Boss',production_admitted=False,human_fun='unreviewed'))
        if len(rows)==len(cs)and all(r['ok']for r in rows):
            records=CandidateLibrary().enroll_payloads(out)
            write(out/'candidate-enrollment.json',dict(records=records,general_relations='UNKNOWN',production_admitted=False,human_fun='unreviewed'))
    except Exception as error:write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--source-index',type=int,default=2);p.add_argument('--held',action='store_true');a=p.parse_args();print(run(a.name,a.seed,a.source_index,a.held))
