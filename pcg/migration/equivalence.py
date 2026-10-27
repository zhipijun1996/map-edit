"""Conservative exact equivalence. Similarity never authorizes disposal."""
import copy
from pathlib import Path
from . import core
from .inspection import normalized_objects
from pcg.prototype.factory.core.quality import digest


def fingerprint(folder):
    folder=Path(folder);doc=core.read(folder/'module.mapnote.json')
    gc=doc['generationContract'];source=gc['generation']['source']
    if gc['kind']!='module' or source.get('sourceManifestSha256','UNKNOWN')=='UNKNOWN':
        raise ValueError('equivalence_requires_known_module_physics_source')
    prefix=doc['id']+'/'
    def normalize(value):
        if isinstance(value,str):return value.replace(prefix,'module/')
        if isinstance(value,list):return [normalize(v)for v in value]
        if isinstance(value,dict):return {k:normalize(v)for k,v in value.items()}
        return value
    ignored={'id','factory_id','factory_evidence','module_sha256','layout_title','play_hint',
             'review_alias','idea_ids','source_map_request','map_request_response','map_specification'}
    cases=[{k:v for k,v in case.items()if k not in ignored}for case in core.legacy_cases(folder)]
    routes=[{k:v for k,v in route.items()if k!='validationIds'}for route in gc['routes']]
    return digest(normalize(dict(objects=normalized_objects(doc),cases=cases,ports=gc['ports'],
        relations=gc['relations'],routes=routes,capabilities=doc['capabilityRequirements'],
        actorBody=gc['space']['actorBody'],bounds=gc['space']['bounds'],
        physicsCommit=source['physicsSourceCommit'],physicsSourceManifest=source['sourceManifestSha256'])))


def decision(source,primary_id,out):
    source=Path(source).resolve();primary_id=core.safe_id(primary_id)
    primary=core.ACTIVE/primary_id;core.validate(primary,require_certified=True)
    meta=core.read(primary/'migration.json')
    if meta.get('internalGeometryChanged')is not False:
        raise ValueError('primary_adaptation_requires_separate_equivalence_review')
    original=core.resolve_artifact(meta['sourcePath']+'/module.mapnote.json').parent
    secondary_fingerprint=fingerprint(source);primary_fingerprint=fingerprint(original)
    value=dict(schema='pcg/exact-module-equivalence/v1',source=core.relative(source),
        sourceDocumentSha256=core.sha(source/'module.mapnote.json'),
        primaryId=primary_id,primaryContentVersion=core.read(primary/'module.mapnote.json')['generationContract']['contentVersion'],
        sourceFingerprint=secondary_fingerprint,primaryFingerprint=primary_fingerprint,
        exact=secondary_fingerprint==primary_fingerprint,
        humanApproval='UNKNOWN',method='exact canonical inputs, interfaces, geometry and frozen physics source; no mirror/translation normalization')
    core.write(out,value)
    return value


def verify(source,record):
    if record.get('schema')!='pcg/exact-module-equivalence/v1':
        raise ValueError('deduplication_requires_reviewed_equivalence_record')
    original_key=core.relative(source)
    actual=core.resolve_artifact(original_key+'/module.mapnote.json').parent
    primary=core.ACTIVE/core.safe_id(record['primaryId'])
    core.validate(primary,require_certified=True)
    meta=core.read(primary/'migration.json')
    parent=core.resolve_artifact(meta['sourcePath']+'/module.mapnote.json').parent
    if meta.get('internalGeometryChanged')is not False or record['source']!=original_key:
        raise ValueError('equivalence_original_identity_changed')
    if record['primaryContentVersion']!=core.read(primary/'module.mapnote.json')['generationContract']['contentVersion'] or record['sourceDocumentSha256']!=core.sha(actual/'module.mapnote.json'):
        raise ValueError('equivalence_document_version_changed')
    actual_fingerprint=fingerprint(actual);expected=fingerprint(parent)
    if actual_fingerprint!=expected or record['sourceFingerprint']!=actual_fingerprint or record['primaryFingerprint']!=expected:
        raise ValueError('not_exactly_equivalent_keep_original_for_review')
    return dict(duplicateOf=record['primaryId'],equivalenceFingerprint=expected)
