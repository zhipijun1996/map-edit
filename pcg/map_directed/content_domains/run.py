import argparse,copy,json,time,traceback,random
from .build import build
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..block_grid.verify import verify
from ..graph_landforms.run import steps
from ..r2_full.orchestrate import edge_cover_route
from ..region_scale.materialize import case_for
from ..shape_search.search import translated
from ..library import CandidateLibrary

def cases(c):
    g=c['exploration_graph'];plans=[('upper',steps(c,g['principal_routes'][0]['nodes']),False),('lower',steps(c,g['principal_routes'][1]['nodes']),False),('reward-return',steps(c,['start','reward','start','lowerA','lowerB','merge']),True),('cross-route',steps(c,['start','upperA','upperB','merge','lowerB','lowerA','start','lowerA','lowerB','merge']),False),('all-directions',edge_cover_route(c),True)];out=[]
    for name,path,reward in plans:
        v=case_for(c,path,name);v.update(title='风铃平原 · 真实库内容驱动',preview_title='全库匹配 / Block直拼 / 原有挑战与回程',extra_script=str(REPO/'pcg/map_directed/catalog_feed/reentrant_extra.gd'),required_reward_ids=[s['id']for s in c['case']['reward_sites']]if reward else[],reward_claim_limit=1 if reward else 0,maximum_coins=18 if reward else 0,map_seed=g['seed'])
        v['presentation_areas']=[dict(id=k,identity=t,position=c['nodes'][k]['center']['position'])for k,t in [('start','windmill_plateau'),('merge','clock_court'),('reward','repair_gallery')]];v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m['action_clearance']]
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
        out.append(v)
    return out

def run(name,seed,sources,held=False):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable content Map exists')
    out.mkdir();t=time.perf_counter();write(out/'protocol.json',dict(seed=seed,sources=sources,held=held,holdout_seed='content-native-input-84983',all_library_queries=True,platform_fallback=False,production_admitted=False))
    try:
        c=build(out,seed,sources)
        if c is None:write(out/'summary.json',dict(status='needs_design',physics='NOT_RUN',all_passed=False));return
        cs=cases(c)
        if held:
            rng=random.Random('content-native-input-84983/'+seed)
            for original in cs[:3]:
                for i in range(2):
                    v=copy.deepcopy(original);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
        if held:
            regression=REPO/'pcg/results/content-domains-map-held-v1'
            old_cases=json.loads((regression/'cases.json').read_text())['cases'];bad={r['id']for r in json.loads((regression/'rows.json').read_text())if not r['ok']}
            for old in old_cases:
                if old['id']not in bad:continue
                base=next(v for v in cs[:3]if old['id'].startswith(v['id']+'-held-'))
                v=copy.deepcopy(base);v['id']+='-regression-'+old['id'].rsplit('-held-',1)[-1];v['noise']=old['noise'];cs.append(v)
        write(out/'cases.json',dict(cases=cs));rows=[];audits=[]
        for case,r,e in ContentEngine(out/'physics').run(cs,'content-native-map'):
            a=verify(c,case,r);audits.append(dict(id=case['id'],**a));write(out/'boundary-state-verification.json',audits);row=dict(id=case['id'],ok=a['ok'],physics_ok=r['ok'],reason=r['reason'],block_errors=a['errors'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','ok','physics_ok','reason','block_errors','ticks','failure']},ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=all(r['ok']for r in rows),passed=sum(r['ok']for r in rows),total=len(cs),rows=rows,seconds=time.perf_counter()-t,production_admitted=False,human_fun='unreviewed'))
        if all(r['ok']for r in rows):write(out/'candidate-enrollment.json',dict(records=CandidateLibrary().enroll_payloads(out),production_admitted=False))
    except Exception as e:write(out/'failure.json',dict(error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--sources',nargs='+',required=True);p.add_argument('--held',action='store_true');a=p.parse_args();run(a.name,a.seed,a.sources,a.held)
