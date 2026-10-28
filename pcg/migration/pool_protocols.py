"""DRAFT runtime wiring for frozen, independently registered holdout pools.

This module is inert until the coordinated physics/CLI patch is applied. It
validates definitions and source bindings; it neither simulates nor admits a
Module. Original v1/v2 report protocols keep their exact historical semantics.
"""
from __future__ import annotations
import copy
from pathlib import Path
from . import core,holdout_guard as guard
from pcg.prototype.factory.core.quality import digest

MUTABLE_PROTOCOL_KEYS={'holdoutSeed','independentPoolId'}


def _legacy_paths():
    from . import physics
    return list(dict.fromkeys((Path(physics.PROTOCOL).resolve(),Path(physics.FULL_PROTOCOL).resolve())))


def _default(folder):
    from . import physics
    _,cases=guard._cases(folder)
    return physics.FULL_PROTOCOL if (Path(folder)/'adaptation.json').exists()or any(c.get('migration_adaptation')for c in cases)else physics.PROTOCOL


def _entry(pool_id):
    rows=[row for row in guard._state()['independentPools']if row['id']==pool_id]
    if len(rows)!=1:raise ValueError('unknown_or_ambiguous_registered_holdout_pool:'+str(pool_id))
    return rows[0]


def _skeleton(protocol):
    return {key:value for key,value in protocol.items()if key not in MUTABLE_PROTOCOL_KEYS}


def _validate(folder,row,protocol,*,new_run=False):
    identity=guard._identity(folder);doc=core.read(Path(folder)/'module.mapnote.json');canonical,cases=guard._cases(folder)
    core.verify_artifacts([row['protocol'],row['declaration']])
    registered=core.read(core.resolve_artifact(row['protocol']['path']));declaration=core.read(core.resolve_artifact(row['declaration']['path']))
    if protocol!=registered:raise ValueError('registered_holdout_protocol_content_mismatch')
    if protocol.get('independentPoolId')!=row['id']or declaration.get('id')!=row['id']:raise ValueError('holdout_pool_identity_mismatch')
    if row['source']!=identity or declaration.get('source')!=identity:raise ValueError('holdout_pool_bound_to_another_original_source')
    frozen=row['frozenCandidate']
    if declaration.get('frozenCandidate')!=frozen:raise ValueError('pool_registry_and_frozen_declaration_disagree')
    if frozen['contentVersion']!=doc['generationContract']['contentVersion']:raise ValueError('holdout_pool_bound_to_another_content_version')
    if frozen['canonicalCasesSha256']!=core.sha(canonical)or frozen['programSignature']!=guard._program_signature(cases):
        raise ValueError('holdout_pool_bound_to_another_frozen_program')
    if new_run and frozen['documentSha256']!=core.sha(Path(folder)/'module.mapnote.json'):
        raise ValueError('candidate_document_changed_after_pool_allocation')
    if row['poolKey']!=digest(guard._pool(protocol))or declaration.get('pool')!=guard._pool(protocol):
        raise ValueError('registered_pool_condition_fingerprint_changed')
    base=declaration.get('baseProtocol')
    if not isinstance(base,dict):raise ValueError('registered_pool_missing_frozen_base_protocol')
    core.verify_artifacts([base]);base_path=core.resolve_artifact(base['path']).resolve()
    if base_path not in _legacy_paths():raise ValueError('registered_pool_base_is_not_a_known_legacy_protocol')
    baseline=core.read(base_path)
    if _skeleton(protocol)!=_skeleton(baseline):
        raise ValueError('registered_pool_changed_quality_selection_noise_body_or_budget')
    if protocol['holdoutSeed']==baseline['holdoutSeed']:raise ValueError('registered_pool_reuses_base_holdout_seed')
    nonce=declaration.get('allocationNonce')
    if not isinstance(nonce,str)or len(nonce)!=64 or any(c not in'0123456789abcdef'for c in nonce):
        raise ValueError('registered_pool_missing_once_allocated_random_nonce')
    if declaration.get('candidateFrozenBeforeAllocation')is not True:raise ValueError('candidate_was_not_frozen_before_pool_conditions')
    return row


def bind_registered_pool(folder,pool_id):
    """Attach a registry reference without editing frozen document/case bytes."""
    folder=Path(folder).resolve();row=_entry(pool_id)
    _validate(folder,row,core.read(core.resolve_artifact(row['protocol']['path'])),new_run=True)
    meta=core.read(folder/'migration.json')
    binding=dict(id=row['id'],protocol=row['protocol'],declaration=row['declaration'],registryEntrySha256=digest(row))
    existing=meta.get('holdoutPool')
    if existing is not None and existing!=binding:raise ValueError('frozen_candidate_already_bound_to_a_different_pool')
    meta['holdoutPool']=binding;core.write(folder/'migration.json',meta)
    return binding


def runtime_protocol(folder,explicit=None,*,new_run=False):
    """Select metadata's registered pool, or retain the historical default."""
    folder=Path(folder).resolve();meta=core.read(folder/'migration.json');binding=meta.get('holdoutPool')
    requested=Path(explicit).resolve()if explicit is not None else None
    if not binding:
        if requested is not None and requested not in _legacy_paths():
            raise ValueError('explicit_holdout_protocol_is_not_bound_in_candidate_metadata')
        return requested or Path(_default(folder)).resolve()
    row=_entry(binding.get('id'))
    if binding!={"id":row['id'],"protocol":row['protocol'],"declaration":row['declaration'],"registryEntrySha256":digest(row)}:
        raise ValueError('candidate_holdout_pool_metadata_changed')
    selected=core.resolve_artifact(row['protocol']['path']).resolve()
    if requested is not None and requested!=selected:raise ValueError('explicit_protocol_disagrees_with_frozen_pool_metadata')
    _validate(folder,row,core.read(selected),new_run=new_run)
    return selected


def _usage_path(row):
    return core.resolve_artifact(row['declaration']['path']).parent/'usage.json'


def assert_unstarted(folder,protocol_path):
    """A registered pool gets one formal holdout execution, not lucky reruns."""
    protocol=core.read(protocol_path)
    if'independentPoolId'not in protocol:return
    row=_validate(folder,_entry(protocol['independentPoolId']),protocol,new_run=True)
    if _usage_path(row).exists():raise ValueError('registered_holdout_pool_already_started_reuse_report_only')


def reserve_holdout(folder,protocol_path,experiment_name):
    """Called immediately before the first held-out evaluation, after calibration."""
    protocol=core.read(protocol_path)
    if'independentPoolId'not in protocol:return None
    with guard._lock():
        row=_validate(folder,_entry(protocol['independentPoolId']),protocol,new_run=True)
        target=_usage_path(row);expected=dict(schema='pcg/registered-holdout-execution/v1',
            poolId=row['id'],source=row['source'],frozenCandidate=row['frozenCandidate'],
            experimentName=core.safe_id(experiment_name),registryEntrySha256=digest(row),
            protocol=row['protocol'],declaration=row['declaration'])
        if target.exists():
            if core.read(target)!=expected:raise ValueError('independent_pool_reserved_for_another_execution')
        else:core.write(target,expected)
        return dict(path=core.relative(target),sha256=core.sha(target))


def report_binding(folder,protocol_path,experiment_name):
    protocol=core.read(protocol_path)
    if'independentPoolId'not in protocol:return None
    row=_validate(folder,_entry(protocol['independentPoolId']),protocol)
    usage=_usage_path(row)
    if usage.exists()and core.read(usage)['experimentName']!=experiment_name:raise ValueError('holdout_execution_name_mismatch')
    return dict(id=row['id'],registryEntrySha256=digest(row),protocol=row['protocol'],declaration=row['declaration'],
        usage=dict(path=core.relative(usage),sha256=core.sha(usage))if usage.exists()else None,
        scope='One independently preregistered pool for exactly this frozen source/content/program.')


def evidence_protocol(folder,protocol,*,report=None,report_path=None):
    """Historical proofs stay accepted; new pools need full canonical binding."""
    for legacy in _legacy_paths():
        if protocol==core.read(legacy):return dict(mode='historical_v1_v2')
    row=_validate(folder,_entry(protocol.get('independentPoolId')),protocol)
    if report is None or not isinstance(report.get('holdoutPool'),dict):raise ValueError('report_missing_registered_holdout_pool_binding')
    if not _usage_path(row).exists():raise ValueError('registered_report_did_not_execute_independent_holdout')
    binding=report['holdoutPool'];expected=report_binding(folder,core.resolve_artifact(row['protocol']['path']),core.read(_usage_path(row))['experimentName'])
    if binding!=expected:raise ValueError('report_registered_holdout_binding_changed')
    if binding.get('usage')is None:raise ValueError('registered_report_did_not_execute_independent_holdout')
    core.verify_artifacts([binding['usage']])
    if report_path is not None:
        # Re-analysis may be appended in the same original experiment folder.
        if Path(report_path).parent.name!=core.read(_usage_path(row))['experimentName']:
            raise ValueError('registered_holdout_report_is_not_its_reserved_execution')
    return dict(mode='registered_independent_pool',registryEntrySha256=digest(row),
        artifacts=[row['protocol'],row['declaration'],binding['usage']])


def source_dependencies(folder,protocol_path):
    """Freeze the actual declaration/protocol with code, not global mutable ledger."""
    protocol=core.read(protocol_path);paths=[Path(__file__),Path(guard.__file__)]
    if'independentPoolId'in protocol:
        row=_validate(folder,_entry(protocol['independentPoolId']),protocol,new_run=True)
        paths += [core.resolve_artifact(row[k]['path'])for k in('protocol','declaration')]
    return paths


def cache_identity(folder,protocol,report=None):
    if any(protocol==core.read(path)for path in _legacy_paths()):return dict(mode='historical_v1_v2')
    row=_entry(protocol.get('independentPoolId'));_validate(folder,row,protocol)
    usage=_usage_path(row)
    return dict(registryEntrySha256=digest(row),protocolSha256=core.sha(core.resolve_artifact(row['protocol']['path'])),
        declarationSha256=core.sha(core.resolve_artifact(row['declaration']['path'])),
        usageSha256=core.sha(usage)if usage.exists()else None,
        reportBinding=copy.deepcopy((report or{}).get('holdoutPool')))
