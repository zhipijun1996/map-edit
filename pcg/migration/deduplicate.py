"""Prove exact current static resources or narrowly scoped original forests.

Uses the existing certificates, relocation lock, ledger, file hashing and WAL
writer. No source-original relocation is rewritten and no physics is replaced.
"""
from __future__ import annotations
import argparse, ast, copy, json, os, re, tempfile
from pathlib import Path
from . import core
from . import godot_package
from pcg.prototype.factory.core.quality import digest

SCHEMA='pcg/current-module-equivalence/v1'
ALIASES_SCHEMA='pcg/module-aliases/v1'
WAL_SCHEMA='pcg/current-deduplication-transaction/v1'
CASE_ANNOTATIONS={'id','family','module_sha256','factory_id','factory_evidence','recorded_frames','generation_rule','source_identity'}
FORBIDDEN=('hazards','thorns','saws','moving_platforms','hooks','latches','enemies','reward_sites','shop_sites','original_pickups')


def _alias_path():return core.ACTIVE/'aliases.json'
def _aliases():
    path=_alias_path()
    result=core.read(path)if path.exists()else dict(schema=ALIASES_SCHEMA,aliases={})
    if result.get('schema')!=ALIASES_SCHEMA or not isinstance(result.get('aliases'),dict):raise ValueError('unknown_alias_registry_schema')
    return result


def _checkpoint(_label):
    """Filesystem fault-injection seam for isolated transaction tests only."""
    return None


REFERENCE_FIELDS={'id','objectId','supportObjectId','pathObjectId','from','to','from_port','to_port','port_id','portId','routeId','objectIds','routeIds','seamIds'}
def _canonical(value,mapping,field=''):
    if isinstance(value,str):return mapping.get(value,value)if field in REFERENCE_FIELDS else value
    if isinstance(value,list):return [_canonical(v,mapping,field)for v in value]
    if isinstance(value,dict):return {(mapping.get(k,k)if field=='block_ports'else k):_canonical(v,mapping,k)for k,v in value.items()if k not in ('label','note','title','description','prompt')}
    if isinstance(value,float)and value.is_integer():return int(value)
    return value


def _semantics(folder):
    doc=core.read(folder/'module.mapnote.json');gc=doc['generationContract'];meta=core.read(folder/'migration.json')
    compiled=core.read(folder/'compiled-content.json');canonical=core.read(folder/'physics-input-cases.json')['cases']
    if gc['kind']!='module' or doc.get('source',{}).get('kind')!='resource':raise ValueError('equivalence_scope_requires_original_static_resource')
    if any(compiled.get(k)for k in FORBIDDEN):raise ValueError('stateful_or_progression_cells_require_separate_equivalence_proof')
    if any(o['type']not in ('terrain','platform','entry','exit','route','anchor','note')or(o['type']=='note'and o.get('mechanics'))for o in doc['objects']):raise ValueError('unsupported_static_equivalence_cell')
    if gc.get('portConfigurations'):raise ValueError('alternative_configurations_require_separate_equivalence_proof')
    if any(c.get('original_tuning_profile')for c in canonical):raise ValueError('native_profile_requires_separate_equivalence_proof')
    for case in canonical:
        if not case.get('family','').startswith('original-game-'):raise ValueError('unknown_causal_family_identity_semantics')
    mapping={doc['id']:'MODULE'}
    for i,o in enumerate(doc['objects']):mapping[o['id']]='OBJECT'+str(i)
    ports=sorted(gc['ports'],key=lambda p:(p['position'],p['normal']))
    for i,p in enumerate(ports):
        mapping[p['id']]='PORT'+str(i)
        for j,seam in enumerate(p['seamIds']):mapping[seam]='SEAM'+str(i)+'-'+str(j)
    for i,r in enumerate(gc['routes']):mapping[r['id']]='ROUTE'+str(i)
    physical={k:v for k,v in compiled.items()if k not in ('schema','stable_id','source_sha256')}
    space={k:v for k,v in gc['space'].items()if k not in ('boundsCoverage',)}
    routes=[{k:v for k,v in r.items()if k!='validationIds'}for r in gc['routes']]
    original={k:v for k,v in doc['source']['original'].items()if k!='module_id'}
    payload=dict(compiled=physical,space=space,foundation=gc['foundation'],ports=gc['ports'],relations=gc['relations'],routes=routes,
        closures=[{k:v for k,v in c.items()if k!='validationIds'}for c in gc.get('closures',[])],mirror={k:v for k,v in gc.get('mirror',{}).items()if k!='validationIds'},
        capabilityRequirements=doc['capabilityRequirements'],difficulty=doc['difficulty'],
        programs=[{k:v for k,v in c.items()if k not in CASE_ANNOTATIONS}for c in canonical],originalResource=original,
        actorReview=dict(humanReview=meta['humanReview'],productionAdmitted=meta['productionAdmitted']))
    return _canonical(payload,mapping),ports,mapping


def _source_binding(folder):
    meta=core.read(folder/'migration.json');report_path=core.resolve_artifact(meta['physicsReport']['path']);report=core.read(report_path)
    core.verify_artifacts([meta['physicsReport'],report['sourceBinding'],report['protocol']])
    return report_path,report,core.read(core.resolve_artifact(report['sourceBinding']['path']))


def _core_ast_delta(left,right):
    trees=[ast.parse(p.read_text())for p in (left,right)]
    removed=[];fingerprints=[]
    allowed={'prepare','package'}
    for tree in trees:
        changed={node.name:ast.dump(node,include_attributes=False)for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))and node.name in allowed}
        removed.append(changed)
        tree.body=[node for node in tree.body if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))or node.name not in allowed]
        fingerprints.append(digest(ast.dump(tree,include_attributes=False)))
    if fingerprints[0]!=fingerprints[1]:raise ValueError('nonphysics_tooling_delta_exceeds_reviewed_prepare_and_package_functions')
    return dict(path='migration/core.py',primarySha256=core.sha(left),duplicateSha256=core.sha(right),unchangedRemainingAstSha256=fingerprints[0],
        changedFunctions=sorted(k for k in allowed if removed[0].get(k)!=removed[1].get(k)),
        reason='Only offline prepare/package implementations differ. Both compiled payloads and every actual physics/causal source are separately identical; these functions do not execute inside the frozen Godot experiment.')


def _compare(source,primary):
    # Reuses the established deep certificate re-derivation, including raw
    # calibration/holdout, actual body crossings and native replay receipts.
    source_checked=core.validate(source,require_certified=True);primary_checked=core.validate(primary,require_certified=True)
    source_manifest=core.read(source/'godot-package.json');primary_manifest=core.read(primary/'godot-package.json')
    if source_manifest['compiler_version']!=primary_manifest['compiler_version']or source_manifest['runtimeDependencies']!=primary_manifest['runtimeDependencies']:raise ValueError('native_runtime_sources_differ')
    source_doc=core.read(source/'module.mapnote.json');primary_doc=core.read(primary/'module.mapnote.json')
    forest=source_doc.get('source',{}).get('kind')=='forest'or primary_doc.get('source',{}).get('kind')=='forest'
    forest_evidence={};extra_artifacts=[]
    if forest:
        from .forest_equivalence import semantics
        if source_doc.get('source',{}).get('kind')!='forest'or primary_doc.get('source',{}).get('kind')!='forest':raise ValueError('mixed_original_source_kinds_not_equivalent')
        if source_doc['source']['original']!=primary_doc['source']['original']:raise ValueError('whole_original_forest_data_differ')
        source_payload,source_ports,source_ids,soriginal=semantics(source)
        primary_payload,primary_ports,primary_ids,poriginal=semantics(primary)
        forest_evidence=dict(wholeOriginalDataEqual=True,originalDataSha256=soriginal['originalDataSha256'],
            originalSourceIds=[soriginal['originalId'],poriginal['originalId']],
            persistentProgressionExcluded=True,localBehaviorScope=soriginal['localHookAndFruitBehavior'])
        extra_artifacts=soriginal['sourceArtifacts']+poriginal['sourceArtifacts']
    else:
        source_payload,source_ports,source_ids=_semantics(source);primary_payload,primary_ports,primary_ids=_semantics(primary)
    if source_payload!=primary_payload:raise ValueError('actual_semantics_differ_do_not_archive')
    spath,sreport,sbinding=_source_binding(source);ppath,preport,pbinding=_source_binding(primary)
    if sbinding['engine_sha256']!=pbinding['engine_sha256']or sbinding['runner']!=pbinding['runner']:raise ValueError('actual_engine_or_runner_differ')
    if core.read(core.resolve_artifact(sreport['protocol']['path']))!=core.read(core.resolve_artifact(preport['protocol']['path'])):raise ValueError('fixed_quality_protocol_differs')
    a,b=pbinding['source_files'],sbinding['source_files']
    if a.keys()!=b.keys():raise ValueError('frozen_source_file_sets_differ')
    deltas=[]
    for name in a:
        if a[name]==b[name]:continue
        if name!='migration/core.py':raise ValueError('actual_physics_or_causal_source_differs:'+name)
        deltas.append(_core_ast_delta(ppath.parent/'source_snapshot'/name,spath.parent/'source_snapshot'/name))
    port_map={s['id']:p['id']for s,p in zip(source_ports,primary_ports)}
    source_routes=source_doc['generationContract']['routes'];primary_routes=primary_doc['generationContract']['routes']
    route_map={s['id']:p['id']for s,p in zip(source_routes,primary_routes)}
    artifact_names=('module.mapnote.json','compiled-content.json','physics-input-cases.json','godot-package.json','migration.json','load-evidence/index.json')
    def bindings(folder):return [dict(path=core.relative(folder/name),sha256=core.sha(folder/name))for name in artifact_names]
    return dict(semanticFingerprint=digest(source_payload),sourceValidation=source_checked,primaryValidation=primary_checked,portMapping=port_map,routeMapping=route_map,
        runtimeDependencyFingerprint=digest(source_manifest['runtimeDependencies']),actualPhysicsSourceFingerprint=digest({k:v for k,v in a.items()if k!='migration/core.py'}),
        physicsSourceFiles=len(a),identicalPhysicsAndCausalFiles=sum(a[k]==b[k]for k in a),nonPhysicsToolingDeltas=deltas,
        artifacts=bindings(source)+bindings(primary)+[dict(path=core.relative(spath),sha256=core.sha(spath)),dict(path=core.relative(ppath),sha256=core.sha(ppath))]+extra_artifacts,
        unknownRelationsPreserved=True,persistentProgressionCells=0,newPhysicsCases=0,**(dict(originalForest=forest_evidence)if forest else{}))


def prove(duplicate_id,primary_id,output):
    duplicate_id=core.safe_id(duplicate_id);primary_id=core.safe_id(primary_id)
    if duplicate_id==primary_id:raise ValueError('duplicate_and_primary_must_differ')
    source=core.ACTIVE/duplicate_id;primary=core.ACTIVE/primary_id
    comparison=_compare(source,primary)
    from .forest_equivalence import SCHEMA as FOREST_SCHEMA
    forest='originalForest'in comparison
    value=dict(schema=FOREST_SCHEMA if forest else SCHEMA,exact=True,duplicateId=duplicate_id,primaryId=primary_id,
        duplicateContentVersion=comparison['sourceValidation']['contentVersion'],primaryContentVersion=comparison['primaryValidation']['contentVersion'],
        scope=('Exact original forest dictionary and complete current geometry, Port/Route, control and capability semantics; identical native and physics sources. Only original local hook/fruit behavior; no persistent progression or other dynamic mechanisms.'if forest else'Exact currently certified original static-resource Module under a bijective logical Port/Cell/Route renaming. No reward, enemy, pickup, mechanism, mutable resource profile or runtime persistent namespace.'),**comparison)
    core.write(output,value)
    return value


def verify_proof(artifact):
    core.verify_artifacts([artifact]);proof=core.read(core.resolve_artifact(artifact['path']))
    from .forest_equivalence import SCHEMA as FOREST_SCHEMA
    if proof.get('schema')not in(SCHEMA,FOREST_SCHEMA)or proof.get('exact')is not True:raise ValueError('complete_current_equivalence_proof_required')
    core.verify_artifacts(proof['artifacts'])
    source=core.resolve_artifact('modules/'+core.safe_id(proof['duplicateId'])+'/module.mapnote.json').parent
    primary=core.resolve_artifact('modules/'+core.safe_id(proof['primaryId'])+'/module.mapnote.json').parent
    actual=_compare(source,primary)
    if (proof['schema']==FOREST_SCHEMA)!=('originalForest'in actual):raise ValueError('equivalence_proof_scope_changed')
    if 'originalForest'in actual and proof.get('originalForest')!=actual['originalForest']:raise ValueError('original_forest_data_proof_changed')
    if actual['sourceValidation']['contentVersion']!=proof['duplicateContentVersion']or actual['primaryValidation']['contentVersion']!=proof['primaryContentVersion']:raise ValueError('proof_content_version_not_bound_to_actual_certificates')
    if actual['sourceValidation']['moduleId']!=proof['duplicateId']or actual['primaryValidation']['moduleId']!=proof['primaryId']:raise ValueError('proof_template_identity_not_bound_to_actual_certificates')
    observed={str(core.resolve_artifact(a['path'])):a['sha256']for a in actual['artifacts']}
    frozen={str(core.resolve_artifact(a['path'])):a['sha256']for a in proof['artifacts']}
    if observed!=frozen:raise ValueError('incomplete_or_extra_equivalence_artifact_bindings')
    for name in ('semanticFingerprint','portMapping','routeMapping','runtimeDependencyFingerprint','actualPhysicsSourceFingerprint','nonPhysicsToolingDeltas','physicsSourceFiles','identicalPhysicsAndCausalFiles'):
        if actual[name]!=proof[name]:raise ValueError('current_equivalence_proof_no_longer_matches:'+name)
    return proof


def _paths(t):
    if t.get('schema')!=WAL_SCHEMA or t.get('operation')!='deduplicate_current':raise ValueError('unknown_deduplication_transaction')
    source=core.REPO/t['source'];archive=core.REPO/t['archive'];primary=core.ACTIVE/core.safe_id(t['primaryId'])
    if not re.fullmatch(r'sha256:[0-9a-f]{64}',t.get('sourceContentVersion','')):raise ValueError('unsafe_duplicate_content_version')
    if source.is_symlink()or primary.is_symlink():raise ValueError('symlink_current_package_not_allowed')
    if source.parent.resolve()!=core.ACTIVE.resolve()or source.name!=core.safe_id(t['duplicateId']):raise ValueError('unsafe_duplicate_source_path')
    if archive.resolve()!=(core.RECYCLE/source.name/('duplicate-'+t['sourceContentVersion'].removeprefix('sha256:'))).resolve():raise ValueError('unsafe_duplicate_archive_path')
    if primary==source or Path(t['receiptName']).name!=t['receiptName']:raise ValueError('unsafe_duplicate_transaction_identity')
    return source,archive,primary


def _restore_aliases(t):
    path=_alias_path();prior=bytes.fromhex(t['previousAliasesHex'])if t.get('previousAliasesHex')is not None else None
    before=json.loads(prior)if prior is not None else dict(schema=ALIASES_SCHEMA,aliases={})
    now=_aliases();key=t['duplicateId'];entry=now['aliases'].get(key)
    if entry not in (before['aliases'].get(key),t['aliasEntry']):raise ValueError('unrelated_alias_edit_during_pending_transaction')
    expected=copy.deepcopy(before);expected['aliases'][key]=t['aliasEntry']
    if now in (before,expected):
        if prior is None:path.unlink(missing_ok=True)
        else:
            with tempfile.NamedTemporaryFile(mode='wb',dir=path.parent,delete=False)as stream:
                stream.write(prior);stream.flush();os.fsync(stream.fileno());temporary=Path(stream.name)
            temporary.replace(path)
    else:
        if key in before['aliases']:now['aliases'][key]=before['aliases'][key]
        else:now['aliases'].pop(key,None)
        core.write(path,now)


def _rollback(path,t):
    source,archive,_=_paths(t)
    if source.exists()and archive.exists():raise ValueError('duplicate_current_and_archive_both_exist')
    original=source if source.exists()else archive
    if not original.exists():raise ValueError('duplicate_original_package_missing')
    core._check_tree(original,t['sourceFiles'],()if original==source else(t['receiptName'],))
    if archive.exists():
        (archive/t['receiptName']).unlink(missing_ok=True);archive.rename(source)
    journal=core.ledger();key=t['journalKey'];journal['entries'][key]=t['previousEntry']
    rkey=t['source'];before=t.get('previousCompiledRelocation')
    if before is None:journal['relocations'].pop(rkey,None)
    else:journal['relocations'][rkey]=before
    core.write(core.JOURNAL,journal);_restore_aliases(t);core._restore_catalog(t['previousCatalogHex'])
    current=sorted(p.name for p in core.ACTIVE.iterdir()if p.is_dir())
    if current!=t['previousCurrentDirectories']:core.build_catalog()
    t['status']='rolled_back';core._save_transaction(path,t)


def recover(path):
    with core._migration_lock():
        t=core.read(path);_paths(t)
        if t['status']not in ('complete','rolled_back'):_rollback(Path(path),t)
        return dict(status=t['status'],transaction=core.relative(path))


def merge(artifact):
    # Recovery is deliberately before certificate lookup: a killed transaction
    # can have moved the very package referenced by the proof's artifact paths.
    raw=core.read(core.resolve_artifact(artifact['path']));duplicate_id=core.safe_id(raw['duplicateId']);primary_id=core.safe_id(raw['primaryId'])
    path=core.STATE/'transactions'/('deduplicate-'+duplicate_id+'.json')
    with core._migration_lock():
        if path.exists():
            previous=core.read(path);_paths(previous)
            if previous['primaryId']!=primary_id:raise ValueError('deduplication_transaction_target_changed')
            if previous['status']not in ('complete','rolled_back'):_rollback(path,previous)
            if previous['status']=='complete':
                resolved=resolve(duplicate_id)
                if resolved['primaryId']!=primary_id:raise ValueError('completed_alias_changed')
                return dict(status='already_merged',**resolved)
        proof=verify_proof(artifact);source=core.ACTIVE/duplicate_id;primary=core.ACTIVE/primary_id
        version=proof['duplicateContentVersion'];archive=core.RECYCLE/duplicate_id/('duplicate-'+version.removeprefix('sha256:'))
        aliases=_aliases()
        if duplicate_id in aliases['aliases']:raise ValueError('existing_alias_cannot_be_silently_retargeted')
        if archive.exists()or not source.exists()or not primary.exists():raise ValueError('duplicate_archive_or_current_state_conflict')
        meta=core.read(source/'migration.json');key=meta['sourcePath'];journal=core.ledger();entry=journal['entries'].get(key)
        if not entry or entry.get('migrationStatus')!='active'or entry.get('moduleId')!=duplicate_id:raise ValueError('duplicate_not_current_in_source_ledger')
        alias=dict(primaryId=primary_id,sourceContentVersion=version,targetContentVersion=proof['primaryContentVersion'],portMapping=proof['portMapping'],routeMapping=proof['routeMapping'],proof=artifact,archivedPackage=core.relative(archive))
        transaction=core._new_transaction('deduplicate_current',source,archive,journal,journal_key=key,
            duplicateId=duplicate_id,primaryId=primary_id,sourceContentVersion=version,proof=artifact)
        transaction.update(schema=WAL_SCHEMA,previousAliasesHex=_alias_path().read_bytes().hex()if _alias_path().exists()else None,
            previousCurrentDirectories=sorted(p.name for p in core.ACTIVE.iterdir()if p.is_dir()),previousCompiledRelocation=journal['relocations'].get(core.relative(source)),aliasEntry=alias)
        _paths(transaction);core._save_transaction(path,transaction)
        try:
            core._check_tree(source,transaction['sourceFiles']);archive.parent.mkdir(parents=True,exist_ok=True);source.rename(archive);_checkpoint('after_archive')
            core._check_tree(archive,transaction['sourceFiles'])
            core.write(archive/transaction['receiptName'],dict(reason='exact_duplicate_current_template',replacement=core.relative(primary),proof=artifact,portMapping=proof['portMapping'],originalFiles=transaction['sourceFiles']))
            aliases['aliases'][duplicate_id]=alias;core.write(_alias_path(),aliases);_checkpoint('after_aliases')
            updated=copy.deepcopy(entry);updated.update(migrationStatus='exact_duplicate',replacementModuleId=primary_id,destination=core.relative(primary),
                deduplication=dict(reason='exact_duplicate_current_template',proof=artifact,compiledArchive=core.relative(archive),sourceContentVersion=version,targetContentVersion=proof['primaryContentVersion']))
            journal['entries'][key]=updated
            # Preserve every original-source prefix relocation and archive.
            journal['relocations'][core.relative(source)]=core.relative(archive)
            core.write(core.JOURNAL,journal);_checkpoint('after_ledger')
            core.build_catalog();_checkpoint('after_catalog')
            resolved=resolve(duplicate_id)
            transaction['status']='complete';core._save_transaction(path,transaction)
        except BaseException:
            _rollback(path,transaction);raise
        return dict(status='merged',**resolved,archive=core.relative(archive),transaction=core.relative(path))


def resolve(module_id,port_ids=None,expected_version=None):
    """Reload a durable ID/Port alias, fail closed on any changed proof/version."""
    requested=core.safe_id(module_id);module_id=requested;ports=list(port_ids or[]);chain=[];registry=_aliases()['aliases'];seen=set()
    while module_id in registry:
        if module_id in seen:raise ValueError('module_alias_cycle')
        seen.add(module_id);alias=registry[module_id];proof=verify_proof(alias['proof'])
        original=core.resolve_artifact('modules/'+module_id+'/module.mapnote.json').parent
        if alias.get('archivedPackage')!=core.relative(original):raise ValueError('alias_archive_not_bound_to_relocation_ledger')
        if proof['duplicateId']!=module_id or alias['primaryId']!=proof['primaryId']or alias['portMapping']!=proof['portMapping']or alias['routeMapping']!=proof['routeMapping']:raise ValueError('alias_not_bound_to_actual_equivalence_proof')
        if expected_version is not None and expected_version!=alias['sourceContentVersion']:raise ValueError('requested_alias_content_version_mismatch')
        if alias['sourceContentVersion']!=proof['duplicateContentVersion']or alias['targetContentVersion']!=proof['primaryContentVersion']:raise ValueError('alias_versions_not_bound_to_proof')
        if any(p not in alias['portMapping']for p in ports):raise ValueError('unknown_aliased_port')
        ports=[alias['portMapping'][p]for p in ports];chain.append(dict(id=module_id,primaryId=alias['primaryId'],portMapping=alias['portMapping'],proof=alias['proof']))
        expected_version=alias['targetContentVersion'];module_id=core.safe_id(alias['primaryId'])
    folder=core.ACTIVE/module_id;checked=core.validate(folder,require_certified=True)
    if expected_version is not None and expected_version!=checked['contentVersion']:raise ValueError('alias_target_content_version_changed')
    doc=core.read(folder/'module.mapnote.json');known={p['id']for p in doc['generationContract']['ports']}
    if not set(ports)<=known:raise ValueError('requested_port_unknown_in_current_module')
    return dict(requestedId=requested,primaryId=module_id,contentVersion=checked['contentVersion'],mappedPorts=ports,file=core.relative(folder/'module.mapnote.json'),scene=core.relative(folder/'module.tscn'),aliasChain=chain,reloadedFrom='persistent modules/aliases.json and actual current certified package',mapReady=checked['mapReady'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prove');p.add_argument('duplicate');p.add_argument('primary');p.add_argument('--out',required=True)
    p=sub.add_parser('merge');p.add_argument('proof')
    p=sub.add_parser('resolve');p.add_argument('module_id');p.add_argument('--ports',nargs='*',default=[]);p.add_argument('--version')
    p=sub.add_parser('recover');p.add_argument('transaction')
    args=parser.parse_args()
    if args.command=='prove':result=prove(args.duplicate,args.primary,Path(args.out))
    elif args.command=='merge':result=merge(dict(path=core.relative(Path(args.proof)),sha256=core.sha(args.proof)))
    elif args.command=='recover':result=recover(Path(args.transaction))
    else:result=resolve(args.module_id,args.ports,args.version)
    print(json.dumps(result,ensure_ascii=False,indent=2))
