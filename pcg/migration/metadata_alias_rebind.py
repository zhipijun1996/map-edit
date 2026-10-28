"""Transactional rebind of an existing alias after diagnostics-only metadata edits.

The original equivalence proof is never weakened. A fresh _compare re-derives
both certificates and every physical/interface invariant; only the primary
migration.json artifact binding may differ. Caller owns core._migration_lock.
"""
from __future__ import annotations
import copy,hashlib,json,tempfile
from pathlib import Path
from . import core,deduplicate

SCHEMA='pcg/diagnostics-alias-proof-rebind/v1'


def _bytes(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def _digest(data):return hashlib.sha256(data).hexdigest()
def _artifact(path):return dict(path=core.relative(path),sha256=core.sha(path))
def _checkpoint(name):pass  # Fault injection for transaction regression tests.


def _write_bytes(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False)as f:f.write(data);staged=Path(f.name)
    staged.replace(path)


def _paths(t):
    if t.get('schema')!=SCHEMA:raise ValueError('unknown_diagnostics_alias_transaction')
    module=core.safe_id(t['moduleId']);meta=(core.REPO/t['metadataPath']).resolve();aliases=(core.REPO/t['aliasesPath']).resolve()
    if meta!=core.ACTIVE/module/'migration.json'or aliases!=core.ACTIVE/'aliases.json':raise ValueError('unsafe_diagnostics_alias_transaction_paths')
    for field in ('previousMetadataHex','newMetadataHex'):
        if _digest(bytes.fromhex(t[field]))!=t[field+'Sha256']:raise ValueError('corrupt_diagnostics_alias_metadata_image')
    return meta,aliases


def _rollback(path,t):
    meta,aliases=_paths(t)
    actual=core.sha(meta)if meta.is_file()else None
    if actual not in {t['previousMetadataHexSha256'],t['newMetadataHexSha256']}:raise ValueError('diagnostics_metadata_changed_after_interruption')
    observed=aliases.read_bytes().hex()if aliases.exists()else None
    if observed not in (t.get('previousAliasesHex'),t.get('newAliasesHex')):raise ValueError('diagnostics_alias_registry_changed_after_interruption')
    _write_bytes(meta,bytes.fromhex(t['previousMetadataHex']))
    if t['previousAliasesHex']is None:aliases.unlink(missing_ok=True)
    else:_write_bytes(aliases,bytes.fromhex(t['previousAliasesHex']))
    t['status']='rolled_back';core._save_transaction(path,t)


def recover_pending():
    rows=[]
    for path in (core.STATE/'transactions').glob('diagnostics-alias-rebind-*.json'):
        t=core.read(path);_paths(t)
        if t['status']not in ('complete','rolled_back'):_rollback(path,t)
        rows.append(dict(path=core.relative(path),status=t['status']))
    return rows


def _artifacts_by_path(items):return {str(core.resolve_artifact(x['path'])):x['sha256']for x in items}


def apply_if_affected(folder,updated,diagnostic_receipt):
    """Apply metadata + fresh alias proof atomically, or return None if unrelated."""
    folder=Path(folder).resolve();module=folder.name;alias_path=core.ACTIVE/'aliases.json'
    registry=deduplicate._aliases();affected={k:v for k,v in registry['aliases'].items()if v.get('primaryId')==module}
    if not affected:return None
    before=core.read(folder/'migration.json')
    # Only one diagnostics-history append and the exact report unknowns may vary.
    old_history=before.get('diagnosticsReconciliationHistory',[]);new_history=updated.get('diagnosticsReconciliationHistory',[])
    protected=copy.deepcopy(updated);protected['unresolved']=before['unresolved']
    if 'diagnosticsReconciliationHistory'in before:protected['diagnosticsReconciliationHistory']=before['diagnosticsReconciliationHistory']
    else:protected.pop('diagnosticsReconciliationHistory',None)
    report=core.read(core.resolve_artifact(before['physicsReport']['path']))
    if protected!=before or new_history[:-1]!=old_history or len(new_history)!=len(old_history)+1 or updated['unresolved']!=report['unknown']:
        raise ValueError('alias_rebind_only_exact_diagnostics_metadata_change')
    core.verify_artifacts([diagnostic_receipt])
    old_proofs={key:deduplicate.verify_proof(alias['proof'])for key,alias in affected.items()}
    old_bytes=(folder/'migration.json').read_bytes();new_bytes=_bytes(updated);old_alias_bytes=alias_path.read_bytes()
    token=_digest(old_bytes)[:16]+'-'+_digest(new_bytes)[:16]
    path=core.STATE/'transactions'/f'diagnostics-alias-rebind-{module}-{token}.json'
    destination=core.STATE/'diagnostics-alias-rebindings-v1'/module/token
    t=dict(schema=SCHEMA,status='prepared',moduleId=module,metadataPath=core.relative(folder/'migration.json'),aliasesPath=core.relative(alias_path),
        previousMetadataHex=old_bytes.hex(),previousMetadataHexSha256=_digest(old_bytes),newMetadataHex=new_bytes.hex(),newMetadataHexSha256=_digest(new_bytes),
        previousAliasesHex=old_alias_bytes.hex(),newAliasesHex=None,affectedAliases=list(affected),diagnosticReceipt=diagnostic_receipt)
    if path.exists():
        previous=core.read(path);_paths(previous)
        if previous['status']=='complete':raise ValueError('completed_diagnostics_rebind_metadata_reappeared')
        if previous['status']!='rolled_back':raise ValueError('recover_pending_diagnostics_rebind_first')
    core._save_transaction(path,t)
    try:
        destination.mkdir(parents=True,exist_ok=True)
        for name,blob in [('previous-primary-migration.json',old_bytes),('previous-aliases.json',old_alias_bytes)]:
            target=destination/name
            if target.exists()and target.read_bytes()!=blob:raise ValueError('immutable_diagnostics_alias_history_conflict')
            if not target.exists():_write_bytes(target,blob)
        core.write(folder/'migration.json',updated);_checkpoint('after_metadata')
        revised=copy.deepcopy(registry)
        for key,alias in affected.items():
            old_proof=old_proofs[key]
            duplicate=core.resolve_artifact('modules/'+core.safe_id(key)+'/module.mapnote.json').parent
            comparison=deduplicate._compare(duplicate,folder)
            for name in ('semanticFingerprint','portMapping','routeMapping','runtimeDependencyFingerprint','actualPhysicsSourceFingerprint','nonPhysicsToolingDeltas','physicsSourceFiles','identicalPhysicsAndCausalFiles','sourceValidation','primaryValidation'):
                if comparison[name]!=old_proof[name]:raise ValueError('diagnostics_alias_equivalence_changed:'+name)
            old_artifacts=_artifacts_by_path(old_proof['artifacts']);new_artifacts=_artifacts_by_path(comparison['artifacts'])
            expected=str((folder/'migration.json').resolve())
            if old_artifacts.keys()!=new_artifacts.keys()or {k for k in old_artifacts if old_artifacts[k]!=new_artifacts[k]}!={expected}:
                raise ValueError('diagnostics_alias_only_primary_metadata_binding_may_change')
            proof={**copy.deepcopy(old_proof),**comparison,'diagnosticsMetadataRebinding':dict(previousProof=alias['proof'],
                previousPrimaryMetadata=_artifact(destination/'previous-primary-migration.json'),previousAliasRegistry=_artifact(destination/'previous-aliases.json'),
                diagnosticsReceipt=diagnostic_receipt,transaction=core.relative(path),newPhysicsCases=0)}
            target=destination/(core.safe_id(key)+'-proof.json')
            if target.exists()and target.read_bytes()!=_bytes(proof):raise ValueError('immutable_diagnostics_rebound_proof_conflict')
            if not target.exists():core.write(target,proof)
            ref=_artifact(target);deduplicate.verify_proof(ref)
            row=revised['aliases'][key]
            row.setdefault('proofHistory',[]).append(dict(proof=copy.deepcopy(alias['proof']),diagnosticsReceipt=diagnostic_receipt,
                previousPrimaryMetadata=_artifact(destination/'previous-primary-migration.json'),previousAliasRegistry=_artifact(destination/'previous-aliases.json'),transaction=core.relative(path)))
            row['proof']=ref
        t['newAliasesHex']=_bytes(revised).hex();core._save_transaction(path,t)
        core.write(alias_path,revised);_checkpoint('after_aliases')
        for key in affected:deduplicate.resolve(key)
        t['status']='complete';core._save_transaction(path,t)
    except BaseException:
        _rollback(path,t);raise
    return dict(transaction=_artifact(path),affectedAliases=list(affected),previousPrimaryMetadata=_artifact(destination/'previous-primary-migration.json'),
        previousAliasRegistry=_artifact(destination/'previous-aliases.json'),newPhysicsCases=0)
