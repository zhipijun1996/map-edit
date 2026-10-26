"""Whole-region continuous tests; each folded stage is completed before leaving."""
import argparse,copy,json,time,traceback
from .region_build import build
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..graph_landforms.run import steps
from ..region_scale.materialize import case_for
from ..block_grid.verify import verify
from ..library import CandidateLibrary


def cases(c):
    g=c['exploration_graph'];plans=[]
    for label in ['upper','lower']:
        nodes=[k for p in g['stages']for k in p[label]];plans.append((label,nodes,False))
    nodes=[]
    for p in g['stages']:
        nodes.append(p['fork'])
        if p['reward']:nodes +=[p['reward'],p['fork']]
        nodes+=p['upper'if p['stage']%2==0 else'lower'][1:]
    plans.append(('reward-expeditions',nodes,True));nodes=[]
    for p in g['stages']:
        nodes+=p['upper'];nodes+=list(reversed(p['lower']))[1:]
        if p['reward']:nodes +=[p['reward'],p['fork']]
        nodes+=p['lower'][1:]
    plans.append(('all-directed-arcs',nodes,True));out=[]
    for label,nodes,reward in plans:
        case=case_for(c,steps(c,nodes),label);case.update(title='风铃平原 · 回风崖径',preview_title='多次分叉汇合 / 岩崖换层 / 奖励回程',map_budget_ticks=36000,
             extra_script=str(REPO/'pcg/map_directed/catalog_feed/reentrant_extra.gd'),required_reward_ids=[s['id']for s in c['case']['reward_sites']]if reward else[],reward_claim_limit=3 if reward else 0,maximum_coins=54 if reward else 0)
        for leg in case['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
        case['presentation_areas']=[dict(id='F0',identity='windmill_plateau',position=c['nodes']['F0']['center']['position']),dict(id=g['goal'],identity='clock_court',position=c['nodes'][g['goal']]['center']['position'])]
        out.append(case)
    return out


def run(name,seed,sources,stages=5):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_folded_region')
    out.mkdir();started=time.perf_counter();write(out/'protocol.json',dict(seed=seed,stages=stages,sources=sources,search_attempts=8,expansions_per_attempt=120000,phase='calibration',no_platform_fallback=True,production_admitted=False))
    try:
        c=build(out,seed,sources,stages)
        if c is None:write(out/'summary.json',dict(status='needs_design',physics='NOT_RUN'));return
        cs=cases(c);write(out/'cases.json',dict(cases=cs));rows=[]
        for case,result,evidence in ContentEngine(out/'physics').run(cs,'folded-region'):
            a=verify(c,case,result);row=dict(id=case['id'],ok=a['ok'],physics_ok=result['ok'],reason=result['reason'],errors=a['errors'],failure=result.get('pilot',{}).get('failure'),ticks=result.get('ticks'),evidence=evidence);rows.append(row);write(out/'rows.json',rows);write(out/(case['id']+'-boundary-state.json'),a);print(json.dumps(row),flush=True)
        write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),all_passed=all(r['ok']for r in rows),rows=rows,seconds=time.perf_counter()-started,production_admitted=False,human_fun='unreviewed'))
        if all(r['ok']for r in rows):write(out/'candidate-enrollment.json',dict(records=CandidateLibrary().enroll_payloads(out),production_admitted=False))
    except Exception as e:write(out/'failure.json',dict(error=str(e),traceback=traceback.format_exc()));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--stages',type=int,default=5);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.seed,a.sources,a.stages)
