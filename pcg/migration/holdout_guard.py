"""Durable observed-holdout locks for future migration experiments.

This extends experiment bookkeeping, never certifies gameplay. Existing complete
reports may be re-analysed, replayed or packaged. A new formal run cannot reuse
conditions already observed for the same original content, even after renaming.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import copy
import fcntl
import json
import re
import secrets
from pathlib import Path
from . import core
from pcg.prototype.factory.core.quality import digest,SCENARIO_FIELDS

LOCKS=core.STATE/'holdout-locks-v1.json'
POOLS=core.STATE/'holdout-pools'


class HoldoutConflict(ValueError):
    def __init__(self,details):
        self.details=details
        super().__init__(json.dumps(details,ensure_ascii=False,sort_keys=True))


@contextmanager
def _lock():
    path=LOCKS.with_suffix('.lock');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+')as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def _state():
    return core.read(LOCKS)if LOCKS.exists()else dict(schema='pcg/observed-holdout-locks/v1',
        processedReports={},observations=[],independentPools=[],
        policy='Observed conditions are not fresh independent holdout for a changed candidate. Read-only evidence reuse remains allowed.')


def _identity(folder):
    meta=core.read(Path(folder)/'migration.json');version=meta.get('sourceVersion','').removeprefix('sha256:')
    source=meta.get('sourcePath','')
    if not re.fullmatch('[a-f0-9]{64}',version)or not source or source.startswith('/')or'..'in Path(source).parts:
        raise ValueError('holdout_guard_requires_valid_original_source_identity')
    return dict(sourceVersion='sha256:'+version,sourcePath=source,key=version)


def _cases(folder):
    folder=Path(folder);path=folder/'physics-input-cases.json'
    if not path.exists():path=folder/'cases.json'
    return path,core.read(path)['cases']


def _program_signature(cases):
    # Ignore IDs/titles/registration and observer metadata: renaming a template
    # or replacing only its measurement wrapper cannot buy another random pool.
    fields=set(SCENARIO_FIELDS)|{'control_plan','axes','actions','latches','enemies','reward_sites',
        'original_pickups','original_tuning_profile','required_rewards','expected_reward',
        'required_original_pickups','required_carrier_park','purpose_kind','migration_boundary_plans'}
    return digest([{key:case[key]for key in sorted(fields)if key in case}for case in cases])


def _pool(protocol):
    return dict(baseSeed=protocol['holdoutSeed'],routeSeedStride=1009,
        trialsPerNoiseLevel=protocol.get('trialsPerNoiseLevel',12),
        mild=dict(timingFrames=1,aimDegrees=2),moderate=dict(timingFrames=3,aimDegrees=6))


def _effective_protocol(folder):
    from .pool_protocols import runtime_protocol
    return runtime_protocol(folder)


def _ingest(state,report_path):
    report_path=Path(report_path);relative=core.relative(report_path);hashed=core.sha(report_path)
    previous=state['processedReports'].get(relative)
    if previous:
        if previous!=hashed:raise ValueError('historical_holdout_report_changed:'+relative)
        return
    report=core.read(report_path)
    if report.get('schema')!='pcg/foundation-migration-physics/v1':return
    exposures=[(i,r)for i,r in enumerate(report.get('routes',[]))if isinstance(r.get('holdout'),dict)]
    if not exposures:
        state['processedReports'][relative]=hashed;return
    root=report_path.parent;binding=core.read(root/'input-binding.json')
    folder=core.resolve_artifact(binding['module']['path']).parent
    identity=_identity(folder)
    protocol_ref=report['protocol'];core.verify_artifacts([protocol_ref])
    protocol=core.read(core.resolve_artifact(protocol_ref['path']));pool=_pool(protocol)
    canonical=core.resolve_artifact(binding['cases']['path'])
    if not canonical.exists()or core.sha(canonical)!=binding['cases']['sha256']:
        # A packaged replay adds recordings, so the exact original physics
        # input may be beside the current document under its explicit name.
        canonical=folder/'physics-input-cases.json'
        if not canonical.exists()or core.sha(canonical)!=binding['cases']['sha256']:
            raise ValueError('cannot_bind_observed_holdout_to_original_program:'+relative)
    values=core.read(canonical);cases=values['cases']if isinstance(values,dict)else values
    for index,route in exposures:
        core.verify_artifacts([route['holdout']])
        evaluation=core.read(core.resolve_artifact(route['holdout']['path']))
        state['observations'].append(dict(source=identity,pool=pool,poolKey=digest(pool),
            routeId=route['routeId'],routeIndex=index,actualHoldoutSeed=protocol['holdoutSeed']+index*1009,
            contentVersion=report['contentVersion'],programSignature=_program_signature(cases),
            report=dict(path=relative,sha256=hashed),holdout=route['holdout'],protocol=protocol_ref,
            sourceInputBinding=dict(path=core.relative(root/'input-binding.json'),sha256=core.sha(root/'input-binding.json')),
            failed=not route.get('passed',False),qualityStatus=evaluation.get('quality_gate',{}).get('status','UNKNOWN')))
    state['processedReports'][relative]=hashed


def refresh():
    """Incrementally lock actual completed migration reports; leave history intact."""
    with _lock():
        state=_state()
        for report in sorted((core.REPO/'pcg/results').glob('*/migration-physics.json')):_ingest(state,report)
        state['counts']=dict(observedRoutes=len(state['observations']),
            originalSources=len({o['source']['key']for o in state['observations']}),
            failedHoldoutRoutes=sum(o['failed']for o in state['observations']))
        core.write(LOCKS,state)
    return state


def observe_report(folder,report_path):
    # folder is supplied by the caller for reviewability, while identity is
    # derived from the immutable experiment input binding, not a caller label.
    state=refresh();return state['counts']


def check(folder,*,existing_report=None,protocol_path=None,refresh_locks=True):
    folder=Path(folder).resolve();state=refresh()if refresh_locks else _state()
    identity=_identity(folder);doc=core.read(folder/'module.mapnote.json')
    version=doc['generationContract']['contentVersion'];canonical,cases=_cases(folder)
    if existing_report is not None and Path(existing_report).exists():
        report=core.read(existing_report)
        if report.get('contentVersion')!=version:
            raise HoldoutConflict(dict(status='holdout_pool_locked',phase='holdout_guard',
                conflicts=['existing_report_belongs_to_another_content_version'],source=identity))
        return dict(status='read_only_evidence_reuse',allowed=True,mayStartNewPhysics=False,
            report=dict(path=core.relative(existing_report),sha256=core.sha(existing_report)),source=identity,
            scope='Re-analysis, native replay, packaging or deep verification of this same full report; no fresh holdout claim.')
    protocol_path=Path(protocol_path or _effective_protocol(folder));protocol=core.read(protocol_path)
    pool=_pool(protocol);pool_key=digest(pool)
    observed=[o for o in state['observations']if o['source']['key']==identity['key']]
    if not observed:return dict(status='unobserved_original_source',allowed=True,mayStartNewPhysics=True,source=identity,pool=pool)
    same=[o for o in observed if o['poolKey']==pool_key]
    if same:
        raise HoldoutConflict(dict(status='holdout_pool_locked',phase='holdout_guard',source=identity,
            candidateContentVersion=version,requestedPool=pool,
            conflicts=['holdout_conditions_already_observed_for_original_source'],
            previousEvidence=[dict(routeId=o['routeId'],failed=o['failed'],report=o['report'],holdout=o['holdout'])for o in same],
            searched=['original sourceVersion across all template names and route labels','actual held-out seed/perturbation conditions'],
            negotiable=['reuse unchanged full-report evidence without new physics',
                'for observer-only changes, re-analyse original raw with explicit source binding',
                'freeze a genuine revised candidate and independently preregister a fresh executable pool'],
            automaticRetry=False))
    declarations=[p for p in state['independentPools']if p['poolKey']==pool_key and p['source']['key']==identity['key']]
    declaration=next((p for p in declarations if p['frozenCandidate']['contentVersion']==version
        and p['frozenCandidate']['canonicalCasesSha256']==core.sha(canonical)),None)
    if declaration is None:
        raise HoldoutConflict(dict(status='holdout_pool_locked',phase='holdout_guard',source=identity,
            conflicts=['new_seed_is_not_an_independently_preregistered_pool_for_this_frozen_candidate'],
            requestedPool=pool,previousEvidence=[o['report']for o in observed],
            negotiable=['independent pool registration before any experiment using that pool'],automaticRetry=False))
    core.verify_artifacts([declaration['protocol'],declaration['declaration']])
    if declaration['protocol']['sha256']!=core.sha(protocol_path):raise ValueError('registered_pool_protocol_bytes_changed')
    if core.sha(_effective_protocol(folder))!=core.sha(protocol_path):
        raise HoldoutConflict(dict(status='holdout_pool_locked',phase='holdout_guard',source=identity,
            conflicts=['registered_pool_not_selected_by_actual_harness_protocol'],
            registration=declaration['declaration'],
            negotiable=['wire this frozen protocol into the actual Harness and independent report verifier before execution'],
            automaticRetry=False))
    return dict(status='independent_registered_pool',allowed=True,mayStartNewPhysics=True,source=identity,pool=pool,
        registration=declaration['declaration'])


def register_pool(folder,pool_id):
    """Allocate once after freezing a genuinely revised candidate, never reroll.

    Allocate conditions once after freezing the genuinely revised candidate,
    then bind the registered protocol in its metadata. Actual quality, held-out
    execution, raw verification and native package checks remain mandatory.
    """
    from . import physics
    folder=Path(folder).resolve();core.safe_id(pool_id);refresh()
    with _lock():
        state=_state();identity=_identity(folder);doc=core.read(folder/'module.mapnote.json');canonical,cases=_cases(folder)
        version=doc['generationContract']['contentVersion'];signature=_program_signature(cases)
        observed=[o for o in state['observations']if o['source']['key']==identity['key']]
        if not observed:raise ValueError('initial_unobserved_candidate_does_not_need_a_replacement_pool')
        if any(o['programSignature']==signature for o in observed):
            raise ValueError('unchanged_physics_program_or_observer_only_change_requires_raw_reanalysis_not_new_seed')
        registered=[p for p in state['independentPools']if p['source']['key']==identity['key']]
        previous=next((p for p in registered if p['frozenCandidate']['programSignature']==signature),None)
        if previous:
            from .pool_protocols import bind_registered_pool
            bind_registered_pool(folder,previous['id'])
            return dict(status='already_registered_no_reroll',registration=previous,requiresRuntimeProtocolIntegration=False)
        maximum=core.read(physics.FULL_PROTOCOL).get('maximumAdaptationRevisions',2)
        if len(registered)>=maximum:raise ValueError('preregistered_revision_pool_budget_exhausted')
        target=POOLS/pool_id
        if target.exists()or any(p['id']==pool_id for p in state['independentPools']):raise ValueError('independent_pool_id_already_used')
        # No caller seed argument exists. Conditions are allocated once only
        # after candidate bytes are frozen, then checked against all started runs.
        frozen=dict(contentVersion=version,documentSha256=core.sha(folder/'module.mapnote.json'),
            canonicalCasesSha256=core.sha(canonical),programSignature=signature)
        used={o['pool']['baseSeed']for o in state['observations']}
        used.update(p['pool']['baseSeed']for p in state['independentPools'])
        for file in (core.REPO/'pcg/results').glob('*/protocol.json'):
            value=core.read(file)
            if isinstance(value,dict)and'holdoutSeed'in value:used.add(value['holdoutSeed'])
        seed=secrets.randbelow(2**31-1)+1
        while seed in used:seed=secrets.randbelow(2**31-1)+1
        allocation_nonce=secrets.token_hex(32)
        if frozen['documentSha256']!=core.sha(folder/'module.mapnote.json')or frozen['canonicalCasesSha256']!=core.sha(canonical):
            raise ValueError('candidate_bytes_changed_during_pool_allocation')
        protocol=copy.deepcopy(core.read(physics.FULL_PROTOCOL));protocol['holdoutSeed']=seed
        protocol['independentPoolId']=pool_id
        declaration=dict(schema='pcg/independent-holdout-registration/v1',id=pool_id,source=identity,frozenCandidate=frozen,
            pool=_pool(protocol),priorEvidence=[o['report']for o in observed],
            seedAllocation='system entropy once after candidate freeze; no caller seed, no alternative-pool selection',
            allocationNonce=allocation_nonce,candidateFrozenBeforeAllocation=True,
            baseProtocol=dict(path=core.relative(physics.FULL_PROTOCOL),sha256=core.sha(physics.FULL_PROTOCOL)),
            runtimeProtocolIntegration='REGISTERED_POOL_RUNTIME_V1',humanApproval='UNKNOWN')
        target.mkdir(parents=True);core.write(target/'protocol.json',protocol);core.write(target/'registration.json',declaration)
        row=dict(id=pool_id,source=identity,frozenCandidate=frozen,pool=declaration['pool'],poolKey=digest(declaration['pool']),
            protocol=dict(path=core.relative(target/'protocol.json'),sha256=core.sha(target/'protocol.json')),
            declaration=dict(path=core.relative(target/'registration.json'),sha256=core.sha(target/'registration.json')))
        state['independentPools'].append(row);core.write(LOCKS,state)
        from .pool_protocols import bind_registered_pool
        bind_registered_pool(folder,pool_id)
        return dict(status='registered_frozen_executable_pool',registration=row,requiresRuntimeProtocolIntegration=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('audit')
    p=commands.add_parser('check');p.add_argument('folder');p.add_argument('--existing-report')
    p=commands.add_parser('register');p.add_argument('folder');p.add_argument('--id',required=True)
    args=parser.parse_args()
    try:
        result=refresh()['counts']if args.command=='audit'else check(args.folder,existing_report=args.existing_report)if args.command=='check'else register_pool(args.folder,args.id)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except HoldoutConflict as error:
        print(json.dumps(error.details,ensure_ascii=False,indent=2));raise SystemExit(2)
