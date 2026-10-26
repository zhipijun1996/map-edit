"""One graph, two physically different paths, real merge and reward foldback."""
import argparse,copy,json,random,time,traceback
from .build import build
from .engine import GraphEngine
from ..director import REPO
from ..run import write
from ..block_grid.verify import verify
from ..r2_full.orchestrate import logical_route,edge_cover_route
from ..region_scale.materialize import case_for
from ..shape_search.search import translated
from ..library import CandidateLibrary

def steps(c,nodes):
    return [dict(edge_id=next(e['id']for e in c['exploration_graph']['edges']if(e['from']==a and e['to']==b)or(e['bidirectional']and e['from']==b and e['to']==a)),**{'from':a,'to':b})for a,b in zip(nodes,nodes[1:])]

def cases(c):
    g=c['exploration_graph'];requests=[('upper-main',steps(c,g['principal_routes'][0]['nodes']),False),('lower-main',steps(c,g['principal_routes'][1]['nodes']),False),
        ('reward-foldback',steps(c,['start','cliff','cache','cliff','switchback','landmark']),True),
        ('cross-route-loop',steps(c,['start','rise','ridge','landmark','switchback','cliff','start','cliff','switchback','landmark']),False),
        ('all-declared-directions',edge_cover_route(c),True)]
    out=[]
    for name,path,rewards in requests:
        v=case_for(c,path,name);v.update(title='风铃平原 · 同图驱动 · 高崖与溪谷',preview_title='两条空间路线 / 地标汇合 / 深处宝箱回程',
            extra_script=str(REPO/'pcg/map_directed/catalog_feed/reentrant_extra.gd'),required_reward_ids=[s['id']for s in c['case']['reward_sites']]if rewards else[],reward_claim_limit=1 if rewards else 0,maximum_coins=18 if rewards else 0,map_seed=g['seed'])
        identities={'start':'windmill_plateau','landmark':'clock_court','cliff':'creek_well','cache':'repair_gallery'}
        v['presentation_areas']=[dict(id=k,identity=identity,position=c['nodes'][k]['center']['position'])for k,identity in identities.items()]
        v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m['action_clearance']]
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
        out.append(v)
    return out

def run(name,seed,source,held=False):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable graph-driven run exists')
    out.mkdir();start=time.perf_counter();write(out/'protocol.json',dict(seed=seed,source=source,search_attempts=12,expansions_per_attempt=12000,held=held,holdout_seed='same-graph-input-51391',legacy_graph_consumed=False,old_rock_well_templates=0,map_added_terrain=0,world_resets_inside_route=0,production_admitted=False))
    try:
        c=build(out,seed,REPO/source)
        if c is None:write(out/'summary.json',dict(status='needs_design',physics='NOT_RUN',all_passed=False));return
        cs=cases(c)
        if held:
            rng=random.Random('same-graph-input-51391/'+seed)
            for original in cs[:3]:
                for i in range(2):
                    v=copy.deepcopy(original);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
        write(out/'cases.json',dict(cases=cs));rows=[];audits=[]
        for case,r,e in GraphEngine(out/'physics').run(cs,'same-graph-map'):
            a=verify(c,case,r);audits.append(dict(id=case['id'],**a));write(out/'boundary-state-verification.json',audits)
            row=dict(id=case['id'],ok=a['ok'],physics_ok=r['ok'],reason=r['reason'],block_errors=a['errors'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e);rows.append(row);write(out/'rows.json',rows)
            print(json.dumps({k:row[k]for k in ['id','ok','physics_ok','reason','block_errors','ticks','failure']},ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),passed=sum(r['ok']for r in rows),total=len(cs),rows=rows,seconds=time.perf_counter()-start,production_admitted=False,human_fun='unreviewed',scope='One complete small acceptance graph; no Boss or full regional scale'))
        if all(r['ok']for r in rows):write(out/'candidate-enrollment.json',dict(records=CandidateLibrary().enroll_payloads(out),production_admitted=False))
    except Exception as error:write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--source',required=True);p.add_argument('--held',action='store_true');a=p.parse_args();run(a.name,a.seed,a.source,a.held)
