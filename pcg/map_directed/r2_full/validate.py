"""Bounded full-map evidence: original spawn, real inputs, no in-route resets."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from .compiler import compile_map
from .pressure import enrich
from .bell_room import install
from .orchestrate import make_case,logical_route,partitioned_cover,FullMapEngine
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.quality import digest


def case_for(compiled,targets,name,optional=False,rewards=None):
    case=make_case(compiled,logical_route(compiled,targets),name,required_rewards=rewards)
    case['r2_optional_challenges']=[{k:v for k,v in item.items()if k!='program'}for item in compiled.get('optional_challenges',[])]
    case['extra_script']=str(Path(__file__).with_name('bell_extra.gd'))
    if optional:
        for challenge in compiled['optional_challenges']:
            program=case['pilot_program']
            index=next(i for i,p in enumerate(program)if p.get('edge_to')==challenge['node_id']and p.get('edge_terminal'))+1
            inserted=[]
            for i,w in enumerate(challenge['program']):
                leg=copy.deepcopy(w);leg.update(id='optional-'+challenge['id']+'-'+str(i),
                    edge_id='optional:'+challenge['id'],edge_from=challenge['node_id'],edge_to=challenge['node_id'],
                    edge_terminal=False,budget_ticks=w.get('budget_ticks',360));inserted.append(leg)
            case['pilot_program']=program[:index]+inserted+program[index:]
            case['r2_semantics']['required_rewards'].append(challenge['id'])
    if targets[-1]==compiled['exploration_graph']['entry']:
        # PlatformingModuleDefinition requires distinct entry/exit positions.
        # Finish at an actual existing dock after physically returning through
        # the original entry center; never invent a port one pixel away.
        node=compiled['nodes'][targets[-1]];eid=case['r2_semantics']['logical_route'][-1]['edge_id']
        for i,w in enumerate(node['center_to_port'][eid]):
            leg=copy.deepcopy(w);leg.update(id='returned-entry-dock-'+str(i),edge_id='entry-room-return',budget_ticks=360)
            case['pilot_program'].append(leg)
        port=node['ports'][eid]['target'];case.update(goal=port['region'],exit_port=port['position'])
    case['map_budget_ticks']=min(36000,max(3600,len(case['pilot_program'])*90))
    case['r2_semantics']['concrete_geometry_sha256']=digest({k:case.get(k)for k in ['platforms','one_way_platform_indices','thorns','saws','latches','gate_specs']})
    return case


def build_cases(compiled,mode):
    if mode=='bell':return [case_for(compiled,['r12','boss'],'bell-expedition',optional=True)]
    if mode=='loops':return [case_for(compiled,targets,name)for name,targets in [
        ('lower-cycle',['r14','r18','r5']),('upper-cycle',['r10','r18','r5'])]]
    if mode=='phases':
        cases=[]
        for case in build_cases(compiled,'loops'):
            for phase in [0.,.25,.5,.75]:
                trial=copy.deepcopy(case);trial['id']+='-phase-'+str(phase)
                for saw in trial['saws']:saw['initial_phase']=phase
                trial['counterfactual_or_phase']={'initial_saw_phase':phase,'selection':'fixed before running'}
                cases.append(trial)
        return cases
    if mode=='negative':
        blocked=case_for(compiled,['boss'],'negative-locked-boss')
        for node in blocked['r2_semantics']['nodes']:
            if node['id']=='r6':node['opens']=[]
        blocked['counterfactual_or_phase']={'expected':'reject','cause':'actual boss collider remains locked'}
        missing=build_cases(compiled,'loops')[0];missing['id']='r2-full-negative-missing-landing'
        index=next(p['target']['support_indices'][0]for p in missing['pilot_program'] if p.get('timing_relation_id')=='timing/e14')
        missing['platforms'][index][1]+=128
        missing['counterfactual_or_phase']={'expected':'reject','cause':'actual required landing moved below declared target'}
        no_shot=build_cases(compiled,'bell')[0];no_shot['id']='r2-full-negative-omitted-bell-shot'
        for leg in no_shot['pilot_program']:
            if leg.get('edge_id')=='optional:r12-bell-cache'and leg['kind']=='module':
                leg['control_plan']=[p for p in leg['control_plan']if p['op']!='shoot']
        no_shot['counterfactual_or_phase']={'expected':'reject','cause':'omitted original bell-opening shot'}
        return [blocked,missing,no_shot]
    if mode=='cover':
        result=partitioned_cover(compiled)
        for c in result:
            c['r2_optional_challenges']=[{k:v for k,v in item.items()if k!='program'}for item in compiled['optional_challenges']]
            c['extra_script']=str(Path(__file__).with_name('bell_extra.gd'))
        return result
    if mode=='routes':
        return [case_for(compiled,['boss'],'main'),case_for(compiled,['exp0_2','r5','boss'],'reward-west',rewards=['exp0_2']),
            case_for(compiled,['exp1_2','r5','boss'],'reward-east',rewards=['exp1_2'])]
    raise ValueError('unknown_validation_mode')


def run(name,mode):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_run_exists')
    out.mkdir(parents=True)
    compiled=install(enrich(compile_map(static_gap_hazards=True)))
    cases=build_cases(compiled,mode)
    write(out/'compiled.json',compiled);write(out/'cases.json',{'cases':cases})
    write(out/'protocol.json',dict(schema='pcg/full-r2-validation/v1',region='plains',seed='0',mode=mode,
        budget=dict(cases=len(cases),maximum_ticks_per_case=36000,maximum_pilot_legs=2048,adaptive_retries=0),
        route_scope='Each case starts at original map entry, no reset/teleport/refill within its continuous world',
        acceptance='exact XY + real support rays + stable speed + original damage + actual graph/reward flags',
        population_scope='one frozen previously approved R2 topology; no universal reachability or human approval'))
    engine=FullMapEngine(out/'physics');rows=[]
    for c,r,evidence in engine.run(cases,'full-r2-'+mode):
        rows.append(dict(case_id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),
            legs_completed=r.get('pilot',{}).get('legs_completed'),legs_total=len(c['pilot_program']),
            failure=r.get('pilot',{}).get('failure'),mechanics=r.get('extra'),evidence=evidence))
        write(out/'summary.json',dict(schema='pcg/full-r2-validation-result/v1',source=compiled['source'],
            coverage=compiled['coverage'],rows=rows,all_passed=len(rows)==len(cases)and all(row['ok']for row in rows),
            human_fun='unverified',production_admitted=False))
        print(json.dumps({k:rows[-1][k]for k in ['case_id','ok','reason','ticks','legs_completed','legs_total','failure']},ensure_ascii=False),flush=True)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['bell','loops','cover','routes','phases','negative'],required=True)
    a=p.parse_args();print(run(a.name,a.mode))
