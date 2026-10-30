"""Existing native compiler plus an explicitly owned adjacent-Port fixture host."""
import copy,sys,types
from . import godot_package as base,ideas_runtime_v2 as previous
from pcg.manual_review.prepare_revision053_v1 import decode
from pcg.manual_review.lift_idea_v1 import consumer_document as lift_consumer
VERSION='foundation-data-runtime/user-revision053-v1'
SCENES=[('module','module_loader_ideas_v2.gd'),('demo','package_demo_revision053_v1.gd')]
def audit_cases(doc,cases,*,require_replay=True):
    owned=lift_consumer(doc) if doc['id'].startswith('idea-') else copy.deepcopy(doc)
    normalized=copy.deepcopy(cases)
    content=decode(doc)
    for case in normalized:
        fixture=case.get('explicit_exit_neighbor')
        if not fixture:continue
        top=next(p for p in doc['generationContract']['ports']if p['id']==fixture['portId'])
        assert top['face']=='TOP' and top['permission']=='OUTPUT' and top['surface']=='ONE_WAY_PLATFORM'
        assert fixture['floor']==[top['position'][0]-48,top['position'][1]-32,96,12] and fixture['copiedIntoModule'] is False
        index=fixture['index'];assert index==len(content['platforms']) and case['platforms'][index]==fixture['floor'] and len(case['platforms'])==index+1
        case['platforms'].pop(index);case['one_way_platform_indices'].remove(index)
    _,audit=base.audit_cases(owned,normalized,require_replay=require_replay,_extension=True)
    audit.update(explicitAdjacentFixtureNotModuleGeometry=True,ownedContentExact=True,originalPhysics=True)
    return content,audit
def dependencies(project):
    result={r['path']:r for r in previous.dependencies(project)}
    path='pcg/migration/runtime/package_demo_revision053_v1.gd';result[path]=dict(path=path,sha256=base.sha(base.ROOT/path))
    return [result[k]for k in sorted(result)]
def decorate_manifest(manifest,stage):
    previous.decorate_manifest(manifest,stage)
    manifest['userRevision053']=dict(compiler=dict(path='pcg/migration/revision053_runtime_v1.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/prepare_revision053_v1.py',sha256=base.sha(base.ROOT/'pcg/manual_review/prepare_revision053_v1.py')),neighbor='Explicit compatible adjacent one-way fixture in demo host; excluded from Module compiled geometry.',smoke='Check only declared jump/shoot abilities plus actual movement; never grant an undeclared ability.')
def compile_package(*args,**kwargs):return base.compile_package(*args,**kwargs,_extension=sys.modules[__name__])
def verify_package(folder,require_loaded=True):return base.verify_package(folder,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*args,**kwargs):
    fn=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);fn.__kwdefaults__=base.run_package_validation.__kwdefaults__;return fn(*args,**kwargs)
