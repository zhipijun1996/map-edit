"""Run the bounded Map → search → fill → candidate → whole-map experiment."""
from __future__ import annotations
import argparse
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import time
from .director import REPO,design,challenge_specs,inspect_library
from .composition import assemble
from .library import CandidateLibrary
from .fill import fill
from pcg.prototype.plains.engine import PlainsEngine
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest,module_hash
from pcg.contract.export import export


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


class MapEngine(PlainsEngine):
    def __init__(self,out):
        super().__init__(out,6)
        files=sorted((REPO/'pcg/map_directed').glob('*.py'))+sorted((REPO/'pcg/map_directed').glob('*.mjs'))+sorted((REPO/'pcg/map_directed/godot').glob('*.gd'))
        for p in files:
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
            q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.sim.runner_script=str(REPO/'pcg/map_directed/godot/map_runner.gd')
        self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,
            source_manifest_sha256=digest(self.hashes),scope='one concrete continuous map per case; no inherited module pass')
        write(self.out/'source_binding.json',self.binding)


def validated_fork(match):
    source=match['sourceCase'];path=REPO/source['cases']['path']
    if file_sha(path)!=source['cases']['sha256']:raise ValueError('historical_case_file_drift')
    cases={c['id']:c for c in json.loads(path.read_text())['cases']};routes={}
    for route in source['routeCases']:
        for artifact in route['artifacts']:
            p=(REPO/artifact['path']).resolve()
            if not p.is_relative_to(REPO) or file_sha(p)!=artifact['sha256']:raise ValueError('historical_physics_artifact_drift')
        c=cases[route['sourceCaseId']]
        if module_hash(c)!=route['moduleSha256']:raise ValueError('historical_route_case_drift')
        routes[route['routeId']]=c
    return routes


def perturbations(cases):
    out=[]
    for c in cases:
        for phase in [0.,.25,.5,.75]:
            x=copy.deepcopy(c);x['id']+=f'-phase-{phase}'
            for saw in x['saws']:saw['initial_phase']=phase
            x['map_semantics']['initial_phase_sample']=phase
            out.append(x)
    return out


def execute(name,seed='map-growth-01',prepare_only=False,library_root=None):
    started=time.perf_counter();out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_run_directory_exists')
    out.mkdir(parents=True);events=[]
    def log(event,**fields):
        row=dict(sequence=len(events),event=event,**fields);events.append(row)
        write(out/'generation-log.json',events);print(event,json.dumps(fields,ensure_ascii=False)[:250],flush=True)
    plan=design(seed);specs=challenge_specs(plan)
    write(out/'map-plan.json',plan);write(out/'challenge-specifications.json',specs)
    log('map_designed',algorithm=plan['source_algorithm'],source_cycle=plan['source_cycle'],logic=plan['logic_validation'])
    matches={s['id']:inspect_library(s) for s in specs};write(out/'library-query.json',matches)
    if not matches[specs[0]['id']]['matches']:raise ValueError('no_existing_verified_fork_candidate')
    chosen=matches[specs[0]['id']]['matches'][0]
    fork=validated_fork(chosen)
    log('reuse_scoped_module',module=chosen['id'],contentVersion=chosen['contentVersion'],
        generic_assembly_admitted=chosen['productionInterfaceEligible'],mode='isolated concrete instance validation')
    library=CandidateLibrary(library_root);spec=copy.deepcopy(specs[1]);pool=library.find(spec)
    # Existing candidates may fit only after the same bounded map space
    # negotiation; do not make fresh generation hide an available library hit.
    widened=copy.deepcopy(spec);widened['space']['max_width']=2000
    widened_pool=library.find(widened)
    engine=None
    if pool or widened_pool:
        if not pool:
            log('director_local_revision',condition='space.max_width',before=900,after=2000,
                reason='validated candidate real occupied width',revision=1)
            spec=widened;pool=widened_pool
        selected=pool[0];ascent=selected['case'];candidate=selected['record']
        log('reuse_generated_candidate',record=selected['path'],contentVersion=candidate['contentVersion'],generator_invoked=False)
    else:
        log('module_library_gap',spec=spec['id'],reason='no existing two-port ascent at required 100wu rise and footprint',
            generic_assembly_matches=0)
        engine=PlainsEngine(out/'module-search',12)
        result=fill(spec,engine)
        log('generator_response',status=result['status'],request_sha256=result['request_sha256'],
            failures=result.get('unsatisfied',[]))
        if result['status']=='unsatisfied':
            conditions=result.get('unsatisfied',[])
            if not conditions or any(x['reason']!='spatial_width_exceeds_max' for x in conditions):
                write(out/'blocked.json',result);return out
            spec=widened
            log('director_local_revision',condition='space.max_width',before=900,after=2000,
                reason='actual generator occupancy feedback; topology, abilities and difficulty intent retained',revision=1)
            result=fill(spec,engine)
        write(out/'module-fill-result.json',result)
        if result['status']!='technical_candidate':
            log('bounded_search_stopped',reason=result['reason'],budget_exhausted=True)
            return out
        ascent=result['case'];cases_path=out/'new-module-review-cases.json';write(cases_path,{'cases':[ascent]})
        export(cases_path,out/'new-module-contracts',run=engine.out)
        manifest=json.loads((out/'new-module-contracts/manifest.json').read_text())
        doc=out/'new-module-contracts'/manifest['modules'][0]['file']
        artifacts=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p)) for p in [
            out/'module-fill-result.json',out/'module-search/source_binding.json',out/'module-search/batches.json',doc]]
        candidate=library.enroll(ascent,doc,result['quality'],artifacts)
        log('candidate_enrolled',contentVersion=candidate['contentVersion'],technical_status=candidate['technical_status'],
            production_admitted=False,human_quality=candidate['human_quality'],
            production_rejections=library.promotion_reasons(candidate),
            diversity_cells=result['protocol']['feasible_behavior_cells'])
        # A second lookup must succeed without invoking the generator. This is
        # actual persisted reuse, not a counter increment or in-memory cache.
        again=CandidateLibrary(library.root).find(spec)
        if not any(x['record']['contentVersion']==candidate['contentVersion']for x in again):raise ValueError('new_candidate_not_reusable')
        log('persisted_library_requery',matches=len(again),generator_invoked=False)
    write(out/'effective-challenge-specifications.json',[specs[0],spec])
    cases,composition=assemble(plan,fork,ascent)
    composition['components'][0].update(moduleId=chosen['id'],contentVersion=chosen['contentVersion'])
    composition['components'][1].update(moduleId=candidate['id'],contentVersion=candidate['contentVersion'])
    write(out/'composition.json',composition);write(out/'cases.json',{'cases':cases})
    log('concrete_map_composed',components=2,connector_cells=1,geometry_check=composition['geometry_check'])
    if prepare_only:return out
    map_engine=MapEngine(out/'whole-map-physics');results=[];replays=[]
    for case,result,evidence in map_engine.run(perturbations(cases),'whole-map-phases'):
        results.append(dict(id=case['id'],ok=result['ok'],reason=result['reason'],ticks=result['ticks'],hp=result['hp'],
            map_validation=result.get('map_validation'),evidence=evidence))
        if case['map_semantics']['initial_phase_sample']==0. and result['ok']:
            x=copy.deepcopy(case);x.update(factory_id='map-directed-loop/v1',factory_evidence=evidence,
                recorded_frames=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in result['frames']],
                title={'main':'M01 · 下路到钟台','reward_rejoin':'M02 · 高台取奖后汇合','reward_return':'M03 · 高台取奖、回访入口后完成'}[case['map_semantics']['route_id']])
            x['module_sha256']=module_hash(x);replays.append(x)
    write(out/'whole-map-results.json',results);write(out/'replay_cases.json',{'cases':replays})
    summary=dict(schema='map-notes/map-driven-growth-result/v1',map_seed=seed,
        whole_map_cases=len(results),whole_map_passes=sum(r['ok']for r in results),
        candidate_version=candidate['contentVersion'],production_admitted=False,human_fun='unverified',
        physics_baseline=map_engine.binding['game_source_commit'],latest_game_audited='26e7f2a4',
        runtime='offline bounded experiment; no online generation budget claim',
        canonical_general_assembly='blocked; only concrete map policies receive scoped physics evidence',
        wall_seconds=time.perf_counter()-started,
        status='concrete_map_policies_passed'if all(r['ok']for r in results)else'whole_map_failed')
    write(out/'summary.json',summary);log('whole_map_validation',**summary)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',required=True);p.add_argument('--seed',default='map-growth-01');p.add_argument('--prepare-only',action='store_true');p.add_argument('--library-root',type=Path)
    args=p.parse_args();print(execute(args.name,args.seed,args.prepare_only,args.library_root))
