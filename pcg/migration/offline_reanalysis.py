"""DRAFT append-only analysis of already recorded, unchanged Godot experiments.

No simulation, candidate selection or new holdout occurs here. Activation needs
that coordinated verifier window which imports the specific v2 causal observer.
"""
from __future__ import annotations
import argparse
import copy
import gzip
import json
import shutil
from pathlib import Path
from . import core
from pcg.prototype.factory.core.quality import digest

SCHEMA='pcg/offline-causal-reanalysis/v1'


def validate_lineage(report,report_path):
    analysis=report.get('offlineAnalysis')
    if not analysis:return
    if analysis.get('schema')!=SCHEMA or analysis.get('newPhysicsAttempts')!=0 or analysis.get('newIndependentHoldout')is not False:
        raise ValueError('offline_analysis_must_not_claim_new_simulation_or_holdout')
    reference=analysis.get('sourceReport');core.verify_artifacts([reference])
    source_path=core.resolve_artifact(reference['path']);source=core.read(source_path)
    if source_path.resolve()==Path(report_path).resolve():raise ValueError('offline_analysis_cannot_reference_itself')
    if source_path.parent.resolve()!=Path(report_path).parent.resolve():raise ValueError('offline_analysis_must_reuse_original_experiment_directory')
    original_fields={k:v for k,v in source.items()if k not in('passed','offlineAnalysis')}
    current_fields={k:v for k,v in report.items()if k not in('passed','offlineAnalysis')}
    if original_fields!=current_fields:raise ValueError('offline_analysis_changed_experimental_inputs_routes_or_evidence')
    code=analysis.get('analysisCode',[])
    if not code:raise ValueError('offline_analysis_source_code_snapshot_missing')
    core.verify_artifacts(code)
    names={Path(p['path']).name for p in code}
    if not {'physics.py','causal_observer.py','causal_observer_v2.py','offline_reanalysis.py'}<=names:
        raise ValueError('offline_analysis_required_checker_source_missing')


def _counter_summary(report,run):
    from . import physics
    batches={b['batch']:b for b in core.read(core.resolve_artifact(report['batches']['path']))};cache={}
    def actual(evidence):
        key=evidence['batch']
        if key not in cache:
            batch=batches[key]
            with gzip.open(run/batch['gzip_path'],'rt')as stream:results=json.load(stream)['results']
            inputs=core.read(run/'physics'/(key+'.input.json'))['cases'];cache[key]=(inputs,results)
        inputs,results=cache[key];index=evidence['index'];return inputs[index],results[index]
    baselines={}
    for route in report['routes']:
        evaluation=core.read(core.resolve_artifact(route['calibration']['path']))
        for row in evaluation['rows']:
            if row['level']!='clean':continue
            case,raw=actual(row['evidence'])
            if physics.checked_purpose(physics.author_for(case),case,raw)['ok']:
                baselines[route['routeId']]=raw;break
    rows=[]
    if report.get('counterexamples'):
        for row in core.read(core.resolve_artifact(report['counterexamples']['path'])):
            case,raw=actual(row['evidence'])
            judged=physics._counter_judgment(case,raw,physics.author_for(case),baselines.get(case['route_spec']['id']))
            rows.append(dict(id=case['id'],originalEvidence=row['evidence'],**judged))
    return rows


def _boundary_summary(report,run):
    from . import physics
    rows=[]
    for batch in core.read(core.resolve_artifact(report['batches']['path'])):
        inputs=core.read(run/'physics'/(batch['batch']+'.input.json'))['cases']
        if not any('migration_probe' in c for c in inputs):continue
        with gzip.open(run/batch['gzip_path'],'rt')as stream:results=json.load(stream)['results']
        for i,(case,raw)in enumerate(zip(inputs,results)):
            if 'migration_probe'not in case:continue
            observed=physics.crossing(case,raw)
            if observed.get('observationReanalysis'):
                rows.append(dict(caseId=case['id'],originalRawOk=raw['ok'],observed=observed,
                    originalEvidence=dict(batch=batch['batch'],index=i,output=batch['gzip_path'],sha256=core.sha(run/batch['gzip_path']))))
    return rows


def reanalyse(folder,source_report,name='offline-causal-v2'):
    from . import physics,causal_observer,causal_observer_v2,causal_observer_v3,pool_protocols,holdout_guard
    if not hasattr(physics,'causal_observer_v2'):
        raise ValueError('global_counter_episode_v2_not_integrated_wait_for_coordinated_verifier_window')
    folder=Path(folder).resolve();source_report=Path(source_report).resolve();core.safe_id(name)
    proof=dict(path=core.relative(source_report),sha256=core.sha(source_report))
    original=core.read(source_report);run=source_report.parent;target=run/('migration-physics-'+name+'.json')
    # This re-derives every original threshold, seed, raw identity, whole-body
    # seam, world goal and counter. The historical passed flag is not admission.
    physics.verify_report(folder,proof,deep=True)
    sources=[Path(physics.__file__),Path(causal_observer.__file__),Path(causal_observer_v2.__file__),Path(causal_observer_v3.__file__),
             Path(pool_protocols.__file__),Path(holdout_guard.__file__),Path(__file__),Path(__file__).with_name('review_counter_scope_v1.py'),Path(__file__).with_name('review_counter_scope_v2.py'),Path(__file__).with_name('review_counter_scope_v3.py'),Path(__file__).with_name('review_counter_scope_v4.py'),Path(__file__).with_name('review_counter_scope_v5.py'),Path(__file__).with_name('review_counter_scope_v6.py'),Path(__file__).with_name('review_counter_scope_v7.py'),Path(__file__).with_name('review_counter_scope_v8.py'),Path(__file__).with_name('review_boundary_observer_v1.py')]
    hashes={core.relative(p):core.sha(p)for p in sources};token=digest(dict(sourceReport=proof,analysisSources=hashes))[:24]
    snapshots=run/'offline-analysis'/token
    code=[]
    for source in sources:
        target_source=snapshots/source.name
        target_source.parent.mkdir(parents=True,exist_ok=True)
        if target_source.exists():
            if core.sha(target_source)!=core.sha(source):raise ValueError('immutable_offline_analysis_snapshot_changed')
        else:shutil.copy2(source,target_source)
        code.append(dict(path=core.relative(target_source),sha256=core.sha(target_source)))
    updated=copy.deepcopy(original);updated['passed']=True
    updated['offlineAnalysis']=dict(schema=SCHEMA,sourceReport=proof,analysisCode=code,
        kind='specific_actual_causal_episode_attribution_only',newPhysicsAttempts=0,newIndependentHoldout=False,
        geometryControlResourcesAndOriginalTrialsChanged=False,
        originalAttemptCount=original['actualAttempts'],counterReanalysis=_counter_summary(original,run),
        boundaryReanalysis=_boundary_summary(original,run),
        scope='Original real Godot evidence, unchanged candidate, independently re-derived gates; no new experiment or human approval.')
    validate_lineage(updated,target)
    if target.exists():
        if core.read(target)!=updated:raise ValueError('offline_analysis_name_already_has_different_immutable_result')
    else:core.write(target,updated)
    final_proof=dict(path=core.relative(target),sha256=core.sha(target))
    physics.verify_report(folder,final_proof,deep=True)
    return dict(status='offline_reanalysis_passed',report=final_proof,sourceReport=proof,
        actualOriginalAttempts=original['actualAttempts'],newPhysicsAttempts=0,newIndependentHoldout=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder');parser.add_argument('--report',required=True);parser.add_argument('--name',default='offline-causal-v2')
    args=parser.parse_args();print(json.dumps(reanalyse(args.folder,args.report,args.name),ensure_ascii=False,indent=2))
