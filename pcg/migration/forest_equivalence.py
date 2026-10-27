"""Exact original forest dictionaries, not general dynamic-game equivalence.

Only already independently certified templates can reach the common dedup WAL.
Local hook/fruit reset behavior is retained byte-for-byte in actual inputs and
shares actual runtime sources; persistent pickups/progression are excluded.
"""
from __future__ import annotations
import copy
from pathlib import Path
from . import core
from pcg.prototype.factory.core.quality import digest

SCHEMA='pcg/current-original-forest-equivalence/v1'
FORBIDDEN=('saws','moving_platforms','latches','enemies','reward_sites','shop_sites',
 'original_pickups','original_region_chests','required_original_pickups','required_region_chest_choices')
ALLOWED_TYPES={'terrain','platform','hazard','hookBounce','hookHang','entry','exit','route','anchor','note'}


def source_record(doc):
    from .game_adapter import source_entries
    source=doc.get('source',{})
    if source.get('kind')!='forest':raise ValueError('forest_equivalence_requires_original_forest_dictionary')
    rows=[row for row in source_entries()if row['id']==source.get('moduleId')and row['kind']=='forest']
    if len(rows)!=1:raise ValueError('forest_original_source_identity_not_unique')
    row=rows[0]
    if not row.get('sourceArtifact')or row['data']!=source.get('original'):
        raise ValueError('forest_current_document_does_not_preserve_exact_original_data')
    if row['sourceCommit']!=source.get('commit')or row['sourcePath']!=source.get('path'):
        raise ValueError('forest_original_source_provenance_mismatch')
    artifact=row['sourceArtifact'];core.verify_artifacts([artifact])
    return row


def _no_persistent(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if item and any(word in key.lower()for word in ('persistent','save_key','save_namespace','global_pickup','global_chest')):
                raise ValueError('persistent_progression_not_supported_by_exact_forest_proof')
            _no_persistent(item)
    elif isinstance(value,list):
        for item in value:_no_persistent(item)


def semantics(folder):
    from .deduplicate import _canonical,CASE_ANNOTATIONS
    folder=Path(folder);doc=core.read(folder/'module.mapnote.json');gc=doc['generationContract']
    meta=core.read(folder/'migration.json');compiled=core.read(folder/'compiled-content.json')
    cases=core.read(folder/'physics-input-cases.json')['cases'];row=source_record(doc)
    if gc['kind']!='module'or gc.get('portConfigurations'):
        raise ValueError('forest_equivalence_requires_single_certified_base_configuration')
    for value in (compiled,row['data'],*cases):
        if any(value.get(k)for k in FORBIDDEN):raise ValueError('forest_progression_or_other_dynamic_mechanisms_require_separate_proof')
        _no_persistent(value)
    if any(o['type']not in ALLOWED_TYPES or(o['type']=='note'and o.get('mechanics'))for o in doc['objects']):
        raise ValueError('unsupported_exact_forest_cell')
    if any(c.get('original_tuning_profile')for c in cases):raise ValueError('forest_native_profile_requires_separate_equivalence_proof')
    mapping={doc['id']:'MODULE'}
    for i,obj in enumerate(doc['objects']):mapping[obj['id']]='OBJECT'+str(i)
    ports=sorted(gc['ports'],key=lambda p:(p['position'],p['normal']))
    for i,port in enumerate(ports):
        mapping[port['id']]='PORT'+str(i)
        for j,seam in enumerate(port['seamIds']):mapping[seam]='SEAM'+str(i)+'-'+str(j)
    for i,route in enumerate(gc['routes']):mapping[route['id']]='ROUTE'+str(i)
    programs=[]
    for i,case in enumerate(cases):
        identity=case.get('source_identity',{})
        if identity.get('originalDictionarySha256')!=digest(row['data'])or identity.get('sourceCommit')!=row['sourceCommit']:
            raise ValueError('forest_actual_case_not_bound_to_whole_original_dictionary')
        if not case.get('family','').startswith('original-game-'):raise ValueError('forest_causal_family_identity_unknown')
        program={k:copy.deepcopy(v)for k,v in case.items()if k not in CASE_ANNOTATIONS}
        binding=program.get('migration_boundary_control_binding')
        if binding:
            if binding.get('caseId')!=case['id']:raise ValueError('forest_boundary_binding_wrong_case')
            binding['caseId']='CASE'+str(i)
        programs.append(program)
    contract={k:copy.deepcopy(v)for k,v in gc.items()if k not in
        ('contentVersion','generation','validations','visualization','staticChecks')}
    for route in contract['routes']:route.pop('validationIds',None)
    for closure in contract.get('closures',[]):closure.pop('validationIds',None)
    contract.get('mirror',{}).pop('validationIds',None)
    for cell in contract.get('composition',{}).get('cells',[]):cell.pop('contentVersion',None)
    physical={k:v for k,v in compiled.items()if k not in ('schema','stable_id','source_sha256')}
    parameters=copy.deepcopy(gc['generation']['parameters']);parameters.pop('family',None)
    payload=dict(document={k:v for k,v in doc.items()if k not in
        ('id','title','description','updatedAt','source','generationContract')},contract=contract,compiled=physical,
        parameters=parameters,programs=programs,originalForestData=row['data'],
        sourceRuntimeIdentity={k:doc['source'].get(k)for k in('repository','commit','kind','method','arguments','integration')},
        actorReview=dict(humanReview=meta['humanReview'],productionAdmitted=meta['productionAdmitted']))
    artifacts=[dict(path=row['sourceDocument'],sha256=row['sourceDocumentSha256']),
        {k:row['sourceArtifact'][k]for k in('path','sha256')},
        dict(path=core.relative(__file__),sha256=core.sha(__file__))]
    return _canonical(payload,mapping),ports,mapping,dict(originalId=row['id'],
        originalDataSha256=digest(row['data']),sourceArtifacts=artifacts,
        localHookAndFruitBehavior='Exact original data, complete input fields and identical runtime; no persistent progression cells.')
