"""Synchronize obsolete pending diagnostics with already verified report unknowns.

Only migration.json.unresolved and its explicit reconciliation history may change.
No certificate, Module document, native asset, human state or permission is edited.
"""
from __future__ import annotations
import argparse,copy,datetime,hashlib,json
from pathlib import Path
from . import core,metadata_alias_rebind

REPORT=core.STATE/'metadata-diagnostics-reconcile-v1.json'


def _artifact(path):return dict(path=core.relative(path),sha256=core.sha(path))
def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def inspect(folder,journal=None):
    folder=Path(folder).resolve();journal=journal if journal is not None else core.ledger()
    if folder.parent!=core.ACTIVE.resolve():raise ValueError('diagnostics_only_current_active_module')
    meta=core.read(folder/'migration.json');doc=core.read(folder/'module.mapnote.json');version=doc['generationContract']['contentVersion']
    key=meta.get('sourcePath');entry=journal['entries'].get(key,{})
    if (entry.get('migrationStatus')!='active'or entry.get('moduleId')!=meta.get('moduleId')or folder.name!=meta.get('moduleId')
            or entry.get('destination')!=core.relative(folder)or entry.get('contentVersion')!=version):
        raise ValueError('diagnostics_current_active_ledger_identity_required')
    if meta.get('status')!='passed_scoped':raise ValueError('diagnostics_passed_scoped_required')
    proof=meta.get('physicsReport')
    if not isinstance(proof,dict)or not proof.get('path')or not proof.get('sha256'):raise ValueError('diagnostics_actual_report_required')
    core.verify_artifacts([proof]);report=core.read(core.resolve_artifact(proof['path']))
    if report.get('passed')is not True:raise ValueError('diagnostics_actual_passed_report_required')
    if report.get('contentVersion')!=version:raise ValueError('diagnostics_report_content_version_mismatch')
    unknown=report.get('unknown')
    if not isinstance(unknown,list)or any(not isinstance(x,str)for x in unknown):raise ValueError('diagnostics_exact_report_unknown_list_required')
    if meta.get('godotLoad',{}).get('passed')is not True:raise ValueError('diagnostics_actual_native_admission_required')
    # Existing validator re-derives original raw/quality/holdout and actual native
    # replay. These calls never launch a new experiment or relax admission.
    core.validate(folder,require_certified=True)
    if not isinstance(meta.get('unresolved'),list):raise ValueError('diagnostics_existing_unresolved_list_required')
    return dict(moduleId=meta['moduleId'],folder=core.relative(folder),sourcePath=key,contentVersion=version,
        metadataBeforeSha256=core.sha(folder/'migration.json'),previousUnresolved=copy.deepcopy(meta['unresolved']),
        actualUnknown=copy.deepcopy(unknown),physicsReport=copy.deepcopy(proof),
        document=_artifact(folder/'module.mapnote.json'),nativeManifest=_artifact(folder/'godot-package.json'),
        nativeReplayIndex=_artifact(folder/'load-evidence/index.json'),metadata=meta,
        changed=_canonical(meta['unresolved'])!=_canonical(unknown))


def reconcile_one(folder,journal=None,*,update=True):
    metadata_alias_rebind.recover_pending()
    plan=inspect(folder,journal);folder=Path(folder).resolve();meta=plan.pop('metadata')
    if not plan['changed']:return {**plan,'status':'already_aligned'}
    receipt=dict(schema='pcg/metadata-diagnostics-reconciliation/v1',**plan,
        helperSource=_artifact(Path(__file__)),allowedChanges=['migration.json.unresolved','migration.json.diagnosticsReconciliationHistory.append'],
        noNewExperiments=True,noNewPermissions=True,humanReviewPreserved=meta.get('humanReview'),productionAdmittedPreserved=meta.get('productionAdmitted'),
        previousMetadata=copy.deepcopy(meta),
        scope='Display diagnostics synchronized to existing version-bound verified report unknowns; no new Route, capability, Port, human or Map approval.')
    fingerprint=hashlib.sha256(_canonical(receipt).encode()).hexdigest()
    receipt_path=core.STATE/'metadata-diagnostics-receipts-v1'/plan['moduleId']/(fingerprint+'.json')
    if not update:return {**plan,'status':'would_reconcile','receiptPath':core.relative(receipt_path)}
    if core.sha(folder/'migration.json')!=plan['metadataBeforeSha256']:raise ValueError('diagnostics_metadata_changed_during_plan')
    if receipt_path.exists():
        if _canonical(core.read(receipt_path))!=_canonical(receipt):raise ValueError('immutable_diagnostics_receipt_conflict')
    else:core.write(receipt_path,receipt)
    updated=copy.deepcopy(meta);updated['unresolved']=copy.deepcopy(plan['actualUnknown'])
    history=updated.setdefault('diagnosticsReconciliationHistory',[])
    if not isinstance(history,list):raise ValueError('diagnostics_existing_history_must_be_list')
    history.append(dict(receipt=_artifact(receipt_path),previousUnresolved=copy.deepcopy(plan['previousUnresolved']),
        synchronizedUnknown=copy.deepcopy(plan['actualUnknown']),physicsReport=copy.deepcopy(plan['physicsReport'])))
    # Assert exactly the intended fields before the atomic metadata replacement.
    protected=copy.deepcopy(updated);protected['unresolved']=meta['unresolved']
    if 'diagnosticsReconciliationHistory'in meta:protected['diagnosticsReconciliationHistory']=meta['diagnosticsReconciliationHistory']
    else:protected.pop('diagnosticsReconciliationHistory')
    if _canonical(protected)!=_canonical(meta):raise ValueError('diagnostics_unrelated_metadata_change')
    alias_rebinding=metadata_alias_rebind.apply_if_affected(folder,updated,_artifact(receipt_path))
    if alias_rebinding is None:core.write(folder/'migration.json',updated)
    for name in ('document','nativeManifest','nativeReplayIndex'):
        core.verify_artifacts([plan[name]])
    return {**plan,'status':'reconciled','receipt':_artifact(receipt_path),'aliasRebinding':alias_rebinding,'metadataAfterSha256':core.sha(folder/'migration.json')}


def run(*,update=True):
    rows=[]
    with core._migration_lock():
        journal=core.ledger()
        folders=sorted(core.ACTIVE.glob('*/migration.json'))
        for path in folders:rows.append(reconcile_one(path.parent,journal,update=update))
    report=dict(schema='pcg/current-metadata-diagnostics-reconcile/v1',createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        update=update,modules=len(rows),changed=sum(r['changed']for r in rows),rows=rows,
        source=_artifact(Path(__file__)),scope='Existing technical current library only. Original source failures and human holds unchanged; no certificate, gameplay, permissions or package bytes rewritten.')
    core.write(REPORT if update else REPORT.with_name(REPORT.stem+'-preview.json'),report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    r=run(update=not a.dry_run);print(json.dumps(dict(modules=r['modules'],changed=r['changed'],updated=r['update']),ensure_ascii=False))
