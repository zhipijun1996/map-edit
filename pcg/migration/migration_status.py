"""Reconcile finite source dispositions from actual candidate/evidence versions.

Preparation is not migration. Only the existing current/alias ledger dispositions
count as complete. Shared original resources remain immutable dependencies.
"""
from __future__ import annotations
import argparse, collections, copy, datetime, hashlib, json, re, shutil, subprocess
from pathlib import Path
from . import core, game_adapter

PROTECTED={'active','exact_duplicate','recycled'}
HOLD_STATUSES={'human_design_hold','withdrawn_review','withdrawn','pacing_held'}
HOLD_REVIEWS={'design_hold','human_design_hold','rejected','pacing_held','withdrawn_review'}
REPORT=core.STATE/'source-disposition-v2.json'
SNAPSHOTS=core.REPO/'pcg/results/foundation-migration-final-status-v2/evidence_snapshot'


def _artifact(path):return dict(path=core.relative(path),sha256=core.sha(path))
def _optional(path):
    try:return core.read(path)
    except (OSError,ValueError):return None


def registry():
    rows=[]
    for old in core.read(core.STATE/'inventory-generated-v1.json')['versions']:
        source='pcg/map_directed/library/candidates/'+old['contentVersion'].split(':',1)[1]
        rows.append(dict(sourceKey=source,sourceVersion=old['contentVersion'],sourceType='repository_generated',referenceId=old['source_id'],title=old['title']))
    originals=game_adapter.source_entries()
    for old in originals:
        name='game-'+re.sub(r'[^a-z0-9_-]+','-',old['id'].lower()).replace('__','-').replace('_','-')
        source='pcg/migration/game-sources/'+name
        document=core.resolve_artifact(source+'/module.mapnote.json')
        doc=core.read(document)
        rows.append(dict(sourceKey=source,sourceVersion=doc['generationContract']['contentVersion'],sourceType='original_game',referenceId=old['id'],sourceKind=old['kind'],title=old['title'],stableId=name))
    if len(rows)!=311 or len({r['sourceKey']for r in rows})!=311:raise ValueError('fixed_migration_inventory_must_cover_all_311_sources')
    return rows,originals


def _candidates(fixed):
    known={r['sourceKey']:r for r in fixed};by_source=collections.defaultdict(list);by_version=collections.defaultdict(set);folders={}
    paths=list((core.REPO/'.cache/migration').rglob('migration.json'))
    paths+=list(core.ACTIVE.glob('*/migration.json'))
    # Source records are not prepared candidates. Compiled superseded packages
    # are historical evidence, not newer preparation attempts.
    for path in paths:
        meta=_optional(path)
        if not meta or meta.get('sourcePath')not in known:continue
        source=meta['sourcePath']
        if meta.get('sourceVersion')!=known[source]['sourceVersion']:continue
        document=path.parent/'module.mapnote.json';cases=path.parent/'cases.json'
        doc=_optional(document)
        if not doc or not cases.exists():continue
        gc=doc.get('generationContract',{})
        if gc.get('version')!=2:continue
        b=gc.get('space',{}).get('bounds',{});f=gc.get('foundation',{})
        structural=(f.get('blockSize')==128 and isinstance(f.get('widthBlocks'),int)and isinstance(f.get('heightBlocks'),int)
                    and b.get('w')==f.get('widthBlocks',0)*128 and b.get('h')==f.get('heightBlocks',0)*128)
        candidate=dict(sourceKey=source,sourceVersion=meta['sourceVersion'],contentVersion=gc['contentVersion'],folder=core.relative(path.parent),
            document=_artifact(document),cases=_artifact(cases),physicsInput=_artifact(path.parent/'physics-input-cases.json'if(path.parent/'physics-input-cases.json').exists()else cases),metadata=_artifact(path),status=meta.get('status'),physicsReport=meta.get('physicsReport'),humanReview=meta.get('humanReview','UNKNOWN'),
            structuralFormat='block_rectangle_and_explicit_port_contract'if structural else'static_contract_incomplete',staticFormatPassed=structural,
            mtime=max(document.stat().st_mtime_ns,cases.stat().st_mtime_ns),snapshotRequired=not path.parent.is_relative_to(core.ACTIVE))
        by_source[source].append(candidate);by_version[gc['contentVersion']].add(source);folders[core.relative(path.parent)]=source
    return by_source,by_version,folders


def _ref(value):
    if isinstance(value,dict)and value.get('path'):
        path=core.resolve_artifact(value['path'])
        if not path.is_file():return None,'missing_evidence:'+value['path']
        if value.get('sha256')and core.sha(path)!=value['sha256']:return None,'changed_evidence:'+value['path']
        return _optional(path),None
    return None,None


def _quality(value):
    doc,error=_ref(value)
    if not doc:return dict(status='NOT_RUN'if value=='NOT_RUN'or not value else'UNAVAILABLE',error=error)
    failed=[]
    for row in doc.get('rows',[]):
        p=row.get('purpose',{})
        if p.get('ok')is False or row.get('safe_stable')is False:
            failed.append(dict(level=row.get('level'),trial=row.get('trial'),reasons=p.get('reasons',[]),evidence=row.get('evidence')))
    gate=doc.get('quality_gate',{})
    return dict(status=gate.get('status','UNKNOWN'),reasons=gate.get('reasons',[]),observedFailureReasons=sorted({reason for r in failed for reason in r['reasons']}),stats=doc.get('stats',{}),failedTrials=failed,artifact=value)


def summarize_physics(path,report):
    routes=[];cal_failed=hold_failed=False;reasons=[]
    for r in report.get('routes',[]):
        cal=_quality(r.get('calibration'));hold=_quality(r.get('holdout'))
        cal_failed|=cal['status']not in ('awaiting_human_review','UNKNOWN')
        hold_failed|=hold['status']not in ('awaiting_human_review','NOT_RUN','UNKNOWN')
        reasons.extend(cal.get('reasons',[])+cal.get('observedFailureReasons',[]));reasons.extend(hold.get('reasons',[])+hold.get('observedFailureReasons',[]))
        routes.append(dict(routeId=r.get('routeId'),passed=r.get('passed'),calibration=cal,holdout=hold))
    probes,probe_error=_ref(report.get('probes'));bad_probes=[p for p in probes or[]if not p.get('check',{}).get('passed')]
    counters,counter_error=_ref(report.get('counterexamples'));bad_counters=[c for c in counters or[]if c.get('adjudication',{}).get('invalidates_design')]
    if cal_failed:stage='calibration_failed'
    elif hold_failed:stage='independent_holdout_failed'
    elif bad_probes:stage='boundary_or_continuous_route_failed'
    elif bad_counters:stage='cheap_counterexample_invalidates_design'
    elif report.get('passed'):stage='full_physics_passed_awaiting_native_package_or_enrollment'
    else:stage='full_physics_failed_unclassified'
    conflicts=sorted(set(reasons+[p.get('id','boundary_probe_failed')for p in bad_probes]+[c.get('id','counterexample_invalidates_design')for c in bad_counters]+[e for e in (probe_error,counter_error)if e]))
    return dict(kind='full_physics',stage=stage,passed=report.get('passed',False),actualAttempts=report.get('actualAttempts',0),routes=routes,
        failedBoundaryProbes=bad_probes,invalidatingCounters=bad_counters,conflicts=conflicts,artifact=_artifact(path),
        searchedScope=['frozen_calibration_and_independent_holdout_when_eligible','declared_Port_body_crossings','continuous_declared_routes','finite_cheap_counterexamples'],
        unverifiedScope=report.get('unknown',[]))


def summarize_clean(path,report):
    bad_routes=[r for r in report.get('routes',[])if not r.get('check',{}).get('ok')]
    bad_probes=[p for p in report.get('probes',[])if not p.get('check',{}).get('passed')]
    bad_counters=[c for c in report.get('counters',[])if c.get('adjudication',{}).get('invalidates_design')]
    error=report.get('preparationError')
    stage='clean_preflight_passed_pending_full_quality'if report.get('passed')else'clean_route_failed'if bad_routes else'boundary_or_continuous_route_failed'if bad_probes else'cheap_counterexample_invalidates_design'if bad_counters else'declaration_or_fixture_preparation_failed'
    reasons=[reason for r in bad_routes for reason in r.get('check',{}).get('reasons',[])]
    reasons += [r.get('id','boundary_probe_failed')for r in bad_probes]
    if error:reasons.append(error)
    return dict(kind='clean_preflight',stage=stage,passed=report.get('passed',False),actualAttempts=report.get('actualAttempts',0),routeFailures=bad_routes,
        failedBoundaryProbes=bad_probes,invalidatingCounters=bad_counters,preparationError=error,conflicts=sorted(set(reasons)),artifact=_artifact(path),
        searchedScope=['actual_clean_program','declared_Port_body_crossings','continuous_declared_routes','finite_cheap_counterexamples'],unverifiedScope=['full_calibration','independent_holdout'])


def _events(fixed,by_version,folders,candidates):
    known={r['sourceKey']for r in fixed};events=collections.defaultdict(list)
    by_folder={c['folder']:c for group in candidates.values()for c in group}
    for filename in ('migration-physics.json','clean-preflight.json'):
        for path in (core.REPO/'pcg/results').rglob(filename):
            report=_optional(path)
            if not report or not report.get('contentVersion'):continue
            version=report['contentVersion'];sources=by_version.get(version,set())
            binding=_optional(path.parent/'input-binding.json')
            if binding and isinstance(binding.get('module'),dict):
                folder=str(Path(binding['module']['path']).parent)
                if folder in folders:sources={folders[folder]}
            if len(sources)!=1:continue
            source=next(iter(sources))
            summary=summarize_physics(path,report)if filename=='migration-physics.json'else summarize_clean(path,report)
            summary.update(sourceKey=source,contentVersion=version,mtime=path.stat().st_mtime_ns,physicsInput=copy.deepcopy(binding.get('cases'))if binding else None,
                experimentDocument=copy.deepcopy(binding.get('module'))if binding else None,
                inputBinding=_artifact(path.parent/'input-binding.json')if binding else None)
            events[source].append(summary)
    # Errors before a report could be completed must remain visible too.
    version_index={r['sourceVersion']:r['sourceKey']for r in fixed}
    stable={name:r['sourceKey']for r in fixed for name in (r.get('stableId'),r['referenceId'])if name}
    campaign_paths=set((core.STATE/'campaigns').glob('*.json'))
    for pattern in ('*quality*.json','*promotion*.json','*discovery*.json','*clean*.json'):campaign_paths.update(core.STATE.glob(pattern))
    for path in campaign_paths:
        campaign=_optional(path)
        if not campaign:continue
        for row in campaign.get('rows',[]):
            if not row.get('conflict'):continue
            source=row.get('sourceKey')or row.get('source')or row.get('sourcePath')
            if source not in known:
                source=version_index.get('sha256:'+str(source))or stable.get(row.get('moduleId'))or stable.get(row.get('id'))
            if source not in known and row.get('prepared'):source=folders.get(row['prepared'])
            if source not in known:continue
            version=row.get('contentVersion');candidate=by_folder.get(row.get('prepared'))
            if version is None and candidate:
                bound,_=_ref(candidate.get('physicsReport'))
                if bound:version=bound.get('contentVersion')
                elif path.stat().st_mtime_ns>=candidate['mtime']:version=candidate['contentVersion']
            conflict=row['conflict'];stage='declaration_or_experiment_execution_error'
            if any(k in conflict for k in ('stationary_saw_missing_period','geometry_mismatch','unsupported_reward','unbound_content','native_profile_document_binding')):stage='native_package_projection_failed'
            elif any(k in conflict for k in ('load_execution_failed','load_terminal','invalid_native_load','missing_real_load')):stage='native_package_load_failed'
            elif 'Module contract:'in conflict:stage='static_contract_validation_failed'
            elif any(k in conflict for k in ('source_changed','input_binding','evidence_binding')):stage='evidence_binding_conflict'
            events[source].append(dict(kind='campaign_error',stage=stage,passed=False,contentVersion=version,
                conflicts=[row['conflict']],artifact=_artifact(path),mtime=path.stat().st_mtime_ns,
                searchedScope=['recorded_campaign_stage:'+str(row.get('stage',campaign.get('schema')))],unverifiedScope=['stage_not_completed']))
    return events


def _latest_candidate(candidates):
    if not candidates:return None
    groups=collections.defaultdict(list)
    for c in candidates:groups[c['contentVersion']].append(c)
    # Copies/native receipt attachment must not make an older semantic version
    # newer than an explicitly revised program. The earliest observed prepared
    # file timestamp per semantic version establishes this bounded ordering.
    selected=max(groups,key=lambda v:min(c['mtime']for c in groups[v]))
    return max(groups[selected],key=lambda c:(c['status']=='passed_scoped',c['mtime']))


def _validate_candidates(candidates):
    selected=[_latest_candidate(group)for group in candidates.values()if group]
    files=[str(core.REPO/c['document']['path'])for c in selected]
    process=subprocess.run(['node',str(core.REPO/'pcg/migration/status_contract_check.mjs')],input=json.dumps(files),cwd=core.REPO,capture_output=True,text=True)
    if process.returncode:raise ValueError('existing_contract_validator_batch_failed:'+process.stderr)
    checks=json.loads(process.stdout);lookup={c['document']['path']:c for c in selected}
    receipt=dict(schema='pcg/source-disposition-existing-contract-check/v1',validator='module-contract.js/validateGenerationContract',
        validatorSource=_artifact(core.REPO/'module-contract.js'),batchWrapper=_artifact(core.REPO/'pcg/migration/status_contract_check.mjs'),rows=checks)
    key=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
    path=core.REPO/'pcg/results/foundation-migration-final-status-v2/contract_checks'/(key+'.json')
    if not path.exists():core.write(path,receipt)
    for checked in checks:
        candidate=lookup[core.relative(Path(checked['path']))]
        candidate['staticFormatPassed']=checked['valid'] and checked.get('documentSha256')==candidate['document']['sha256']
        candidate['staticContractCheck']=dict(report=_artifact(path),valid=checked['valid'],documentSha256=checked.get('documentSha256'),error=checked.get('error'))
    return checks


def _snapshot(candidate,root):
    source=core.REPO/candidate['folder'];version=candidate['sourceVersion'].split(':',1)[1]
    dest=Path(root)/version/candidate['contentVersion'].split(':',1)[1]/(candidate['document']['sha256'][:12]+'-'+candidate['cases']['sha256'][:12])
    names=['module.mapnote.json','cases.json','migration.json','physics-input-cases.json','adaptation.json','repair-receipt.json','reference-revision.json','component-receipts.json','thumbnail.svg']
    files={name:source/name for name in names if(source/name).is_file()}
    if(source/'components').exists():files.update({p.relative_to(source).as_posix():p for p in(source/'components').rglob('*')if p.is_file()})
    artifacts=[]
    for name,path in files.items():
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        before=core.sha(path)
        if target.exists()and core.sha(target)!=before:raise ValueError('immutable_pending_snapshot_conflict:'+str(target))
        if not target.exists():shutil.copy2(path,target)
        if core.sha(target)!=before:raise ValueError('pending_snapshot_copy_changed:'+name)
        artifacts.append(_artifact(target))
    if core.sha(dest/'module.mapnote.json')!=candidate['document']['sha256']or core.sha(dest/'cases.json')!=candidate['cases']['sha256']:raise ValueError('pending_candidate_changed_while_snapshotting')
    return dict(path=core.relative(dest),contentVersion=candidate['contentVersion'],document=_artifact(dest/'module.mapnote.json'),cases=_artifact(dest/'cases.json'),artifacts=artifacts,
        phaseTag='latest_pending_candidate_current_bytes',includesAllHistoricalExperimentInputs=False,includesFrozenHelperCode=False,
        archivePlan='Include with global historical cache/raw/source archive. This latest pending image does not replace original experiment input bindings or earlier phase byte images; it is evidence, not another Module library.')


def _disposition(source,entry,candidates,events,snapshot_root=None):
    row=copy.deepcopy(source);row['sourceRole']='module_reference'
    row['initialGaps']=entry.get('initialGaps',entry.get('gaps',[]))
    row['humanReview']=entry.get('humanReview','UNKNOWN')
    row['humanHoldPreserved']=entry.get('migrationStatus')in HOLD_STATUSES or row['humanReview']in HOLD_REVIEWS
    row['structuralAdaptation']=_latest_candidate(candidates)
    if row['structuralAdaptation'] and row['structuralAdaptation'].get('humanReview')in HOLD_REVIEWS:
        row['humanReview']=row['structuralAdaptation']['humanReview'];row['humanHoldPreserved']=True
    status=entry.get('migrationStatus')
    if status in PROTECTED:
        row.update(disposition=status,stage='current_certified_scoped_template'if status=='active'else'exact_duplicate_with_persistent_alias'if status=='exact_duplicate'else'explicitly_recycled',destination=entry.get('destination'),moduleId=entry.get('moduleId'),replacementModuleId=entry.get('replacementModuleId'),latestEvidence=None)
        return row
    candidate=row['structuralAdaptation'];all_events=sorted(events,key=lambda e:e['mtime']);latest=all_events[-1]if all_events else None
    matching=[e for e in all_events if candidate and e.get('contentVersion')==candidate['contentVersion']]
    full=[e for e in matching if e['kind']=='full_physics']
    actual=full[-1]if full else matching[-1]if matching else None
    completion_errors=[e for e in matching if e['kind']=='campaign_error'and e['stage']in ('native_package_projection_failed','native_package_load_failed','evidence_binding_conflict')and(not actual or e['mtime']>=actual['mtime'])]
    if completion_errors:actual=completion_errors[-1]
    if actual and actual.get('physicsInput')and candidate and actual['physicsInput'].get('sha256')!=candidate['physicsInput']['sha256']:
        actual=dict(kind='binding_error',stage='evidence_binding_conflict',passed=False,conflicts=['same_content_version_has_different_actual_physics_input_bytes'],artifact=actual['artifact'],actualAttempts=0,searchedScope=['existing_version_bound_input_comparison'],unverifiedScope=['modified_physics_input_requires_new_binding'])
    row['latestPreviousExperiment']=latest
    if actual:
        row['latestEvidence']=actual;row['stage']=actual['stage'];row['disposition']='not_yet_fulltested'if actual['passed']else'pending_actual_failure'
        expected=actual.get('experimentDocument')
        if expected:
            image=core.resolve_artifact(expected['path'])
            row['experimentDocumentByteImage']=dict(expected=expected,availableAtBoundPath=image.is_file()and core.sha(image)==expected.get('sha256'),
                sameAsCurrentPreparedDocument=bool(candidate and candidate['document']['sha256']==expected.get('sha256')),
                recovery='See historical global cache snapshot or explicitly record missing original byte image; current post-certification metadata is not the original experiment document.')
    elif candidate:
        row.update(disposition='not_yet_fulltested',stage='new_standard_version_prepared_pending_actual_validation',latestEvidence=None)
    elif latest:
        row.update(disposition='pending_actual_failure',stage=latest['stage'],latestEvidence=latest)
    else:row.update(disposition='not_yet_fulltested',stage='new_standard_candidate_not_yet_found',latestEvidence=None)
    row['currentConflicts']=row['latestEvidence'].get('conflicts',[])if row['latestEvidence']else[]
    if candidate and not candidate['staticFormatPassed']:
        row.update(disposition='pending_actual_failure',stage='new_standard_structural_contract_incomplete')
        row['currentConflicts'].append('actual_candidate_failed_existing_generation_contract_validator')
    if candidate and snapshot_root:
        try:row['evidence_snapshot']=_snapshot(candidate,snapshot_root)
        except Exception as error:row['snapshotConflict']=str(error)
    return row


def dependency_rows(originals):
    imported=core.read(core.STATE/'game-source-import.json');rows=[]
    for artifact in imported['files']:
        if not artifact['originalPath'].startswith('resources/generation/modules/')or not artifact['originalPath'].endswith('.tres'):continue
        ident=Path(artifact['originalPath']).stem;owners=[]
        for source in originals:
            if source['sourcePath']==artifact['originalPath']:owners.append(dict(referenceId=source['id'],role='direct_resource_definition'))
            elif source['kind']=='foundry'and any(n.get('module_id')==ident for n in source['data'].get('nodes',[])):owners.append(dict(referenceId=source['id'],role='Foundry_node_definition'))
        actual=core.REPO/artifact['path']
        rows.append(dict(sourceKey=artifact['path'],sourceRole='shared_reference_artifact',migrationStatus='preserved_shared_dependency',moduleReferenceOwners=owners,
            originalPath=artifact['originalPath'],expectedSha256=artifact['sha256'],actualSha256=core.sha(actual),sourceCommit=artifact['sourceCommit'],moved=False,countedAsPendingModule=False))
    if len(rows)!=72:raise ValueError('expected_all_72_shared_original_resource_definitions')
    return rows


def source_clean_observations(fixed):
    """Retain interior-only observations without promoting interface evidence."""
    path=core.STATE/'foundry-canonical-clean-observations-v5.json'
    receipt=_optional(path)
    if not receipt:return {}
    sources={r['referenceId']:r['sourceKey']for r in fixed};verified={};result={}
    for old in receipt.get('rows',[]):
        source=sources.get(old.get('sourceKey'))
        if not source:continue
        row=copy.deepcopy(old);errors=[]
        for name in ('frozenInput','rawEvidence'):
            ref=row.get(name,{})
            if ref.get('path')not in verified:
                actual=core.resolve_artifact(ref.get('path','missing'))
                verified[ref.get('path')]=core.sha(actual)if actual.is_file()else None
            if verified.get(ref.get('path'))!=ref.get('sha256'):errors.append(name+'_missing_or_changed')
        row.update(receipt=_artifact(path),artifactBindingErrors=errors,
            observationAvailable=not errors and row.get('exactCaseEquality')is True and row.get('canonicalCaseDigest')==row.get('frozenCaseDigest'),
            usedForAdmission=False,usedForInterfaceCertification=False)
        result[source]=row
    return result


def reconcile(*,update=True,snapshot_root=None):
    fixed,originals=registry();candidates,versions,folders=_candidates(fixed);_validate_candidates(candidates);events=_events(fixed,versions,folders,candidates)
    journal=core.ledger();rows=[_disposition(source,journal['entries'].get(source['sourceKey'],{}),candidates[source['sourceKey']],events[source['sourceKey']],snapshot_root if update else None)for source in fixed]
    observations=source_clean_observations(fixed)
    for row in rows:
        if row['sourceKey']in observations:
            row['originalSourceCleanObservation']=observations[row['sourceKey']]
            candidate=row['structuralAdaptation']
            row['originalSourceCleanObservation']['sameCasesAsLatestPrepared']=bool(candidate and candidate['physicsInput']['sha256']==observations[row['sourceKey']]['canonicalCasesSHA'])
    dependencies=dependency_rows(originals)
    if update:
        # Re-check live dispositions under the same lock as promotion/dedup. A
        # module admitted while diagnostics were being scanned is never reset.
        with core._migration_lock():
            live=core.ledger()
            for row in rows:
                old=live['entries'].get(row['sourceKey'],{})
                if old.get('migrationStatus')in PROTECTED:
                    row.update(disposition=old['migrationStatus'],stage='current_certified_scoped_template'if old['migrationStatus']=='active'else'exact_duplicate_with_persistent_alias'if old['migrationStatus']=='exact_duplicate'else'explicitly_recycled',moduleId=old.get('moduleId'),destination=old.get('destination'),replacementModuleId=old.get('replacementModuleId'))
                    continue
                held=old.get('migrationStatus')in HOLD_STATUSES
                saved={**old,'source':row['sourceKey'],'sourceType':row['sourceType'],'sourceRole':'module_reference','sourceVersion':row['sourceVersion'],'referenceId':row['referenceId'],
                    'initialGaps':old.get('initialGaps',old.get('gaps',[])),'gaps':row.get('currentConflicts',[]),'migrationDisposition':row['disposition'],
                    'migrationStatus':old['migrationStatus']if held else row['disposition'],'pendingStage':row['stage'],'structuralAdaptation':row['structuralAdaptation'],
                    'actualEvidence':row.get('latestEvidence'),'previousExperiment':row.get('latestPreviousExperiment'),'evidence_snapshot':row.get('evidence_snapshot'),
                    'experimentDocumentByteImage':row.get('experimentDocumentByteImage'),'snapshotConflict':row.get('snapshotConflict'),
                    'originalSourceCleanObservation':row.get('originalSourceCleanObservation'),
                    'humanReview':row['humanReview'],'destination':'original','productionAdmitted':False}
                live['entries'][row['sourceKey']]=saved
            for dep in dependencies:
                old=live['entries'].get(dep['sourceKey'],{})
                live['entries'][dep['sourceKey']]={**old,**dep,'initialMigrationStatus':old.get('initialMigrationStatus',old.get('migrationStatus')),'initialGaps':old.get('initialGaps',old.get('gaps',[])),'gaps':[]if dep['actualSha256']==dep['expectedSha256']else['shared_dependency_source_bytes_changed']}
            core.write(core.JOURNAL,live)
    counts=collections.Counter(r['disposition']for r in rows)
    groups={kind:dict(collections.Counter(r['disposition']for r in rows if r['sourceType']==kind))for kind in ('repository_generated','original_game')}
    report=dict(schema='pcg/source-disposition/v2',createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ledgerUpdated=update,
        inventory=dict(total=311,repositoryGenerated=134,originalGameReferences=177,covered=len(rows),allCovered=len(rows)==311),counts=dict(counts),countsBySource=groups,
        stageCounts=dict(collections.Counter(r['stage']for r in rows)),humanHoldsPreserved=sum(r['humanHoldPreserved']for r in rows),
        pendingHumanHoldsPreserved=sum(r['humanHoldPreserved']and r['disposition']not in PROTECTED for r in rows),
        activeSourceHumanHolds=sum(r['humanHoldPreserved']and r['disposition']=='active'for r in rows),
        sharedDependencies=dict(count=len(dependencies),preserved=True,countedAsPendingModules=False,rows=dependencies),
        formatAdaptedSources=sum(bool(r['structuralAdaptation']and r['structuralAdaptation']['staticFormatPassed'])or r['disposition']in PROTECTED for r in rows),
        actualMigratedSources=counts['active'],exactDuplicateReferences=counts['exact_duplicate'],preparedDoesNotCountAsMigrated=True,
        rows=rows,sourceCode=_artifact(Path(__file__)),snapshotRoot=core.relative(snapshot_root)if snapshot_root else None,
        policy='Latest content-version-bound actual evidence, retained failures and human holds. Shared dependencies are not Module migration backlog; no source files moved by reconciliation.')
    core.write(core.STATE/('source-disposition-v2.json'if update else'source-disposition-v2-preview.json'),report)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dry-run',action='store_true');parser.add_argument('--snapshot-root',default=str(SNAPSHOTS));args=parser.parse_args()
    report=reconcile(update=not args.dry_run,snapshot_root=Path(args.snapshot_root))
    print(json.dumps({k:report[k]for k in ('inventory','counts','countsBySource','stageCounts','formatAdaptedSources','ledgerUpdated')},ensure_ascii=False))
