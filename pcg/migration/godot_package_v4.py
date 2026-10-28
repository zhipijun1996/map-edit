"""Native pickup/profile extension of the existing data compiler and verifier.

No second compiler, physics simulator, or reward implementation: delegate
packaging and every execution binding to v1-v3, add exact native data semantics.
"""
from __future__ import annotations
import copy
from pathlib import Path
from . import godot_package as base

VERSION='foundation-data-runtime/v4'
SCENES=[('module','module_loader_v4.gd'),('demo','package_demo_v4.gd')]
ASSETS=base.ROOT/'pcg/migration/foundation-v1/original-pickup-v4-assets.json'
PROFILE_PATH=base.PROJECT/'config/foundry_capabilities.json'
DEFAULTS_PATH=base.PROJECT/'config/player_tuning.json'


def required(doc,cases):
    return any(c.get('original_pickups')or c.get('original_tuning_profile')for c in cases)or any(o.get('mechanics',{}).get('service')=='DemoApp._commit_pickup'for o in doc.get('objects',[]))


def profile_definition(profile):
    if profile is None:return None
    if not isinstance(profile,dict):base._fail('invalid_original_profile')
    records=base._json(PROFILE_PATH)['profiles']
    original=next((r for r in records if r['id']==profile.get('id')and r.get('implemented')),None)
    if original is None:base._fail('unknown_original_profile',profile=profile.get('id'))
    if set(profile)-{'id','overrides','abilities','effectiveTuning'}:base._fail('unknown_original_profile_fields')
    for key in ('overrides','abilities'):base._equal(profile.get(key),original[key],'native_profile/'+key)
    tuning=base._json(DEFAULTS_PATH);tuning.update(original['overrides'])
    effective={key:tuning[key]for key in ('max_jumps','max_air_shots')}
    if 'effectiveTuning'in profile:base._equal(profile['effectiveTuning'],effective,'native_profile/effectiveTuning')
    return dict(id=original['id'],overrides=copy.deepcopy(original['overrides']),abilities=copy.deepcopy(original['abilities']),effectiveTuning=effective)


def bind_case_behavior(doc,cases):
    result=base.bind_case_behavior(doc,cases,_extension=True)
    if cases:
        profile=profile_definition(cases[0].get('original_tuning_profile'))
        result['generationContract']['generation'].setdefault('parameters',{})['original_tuning_profile']=profile
    return result


def audit_cases(doc,cases,*,require_replay=True):
    filtered=copy.deepcopy(doc);native=[];reward_ids=[]
    for obj in doc.get('objects',[]):
        m=obj.get('mechanics',{})
        if m.get('service')!='DemoApp._commit_pickup':continue
        if obj.get('type')!='reward'or m.get('kind')not in ('coin','note'):base._fail('unsupported_original_pickup',object_id=obj.get('id'))
        expected_size=[14,14]if m['kind']=='coin'else[14,24]
        base._equal([obj['w'],obj['h']],expected_size,obj['id']+'/native_pickup_size')
        base._equal(m.get('interactionRadius'),46,obj['id']+'/native_interaction_radius')
        source=m.get('source')
        if not isinstance(source,dict)or set(source)!= {'id','kind','amount','position'}:base._fail('invalid_original_pickup_source',object_id=obj['id'])
        base._equal(base._center(obj),source['position'],obj['id']+'/native_pickup_position')
        base._equal(m['kind'],source['kind'],obj['id']+'/native_pickup_kind');base._equal(m.get('amount'),source['amount'],obj['id']+'/native_pickup_amount')
        if not isinstance(source['amount'],int)or isinstance(source['amount'],bool)or source['amount']<=0:base._fail('invalid_original_pickup_amount',object_id=obj['id'])
        native.append(copy.deepcopy(source));reward_ids.append(obj['id'])
    if len({r['id']for r in native})!=len(native):base._fail('duplicate_original_pickup_id')
    filtered['objects']=[o for o in filtered['objects']if o['id']not in reward_ids]
    content,audit=base.audit_cases(filtered,cases,require_replay=require_replay,_extension=True)
    profile=profile_definition(cases[0].get('original_tuning_profile'))if cases else None
    stored=doc.get('generationContract',{}).get('generation',{}).get('parameters',{}).get('original_tuning_profile')
    base._equal(stored,profile,'native_profile_document_binding')
    for case in cases:
        base._equal(native,case.get('original_pickups',[]),'native_original_pickups',case.get('id'))
        base._equal(profile_definition(case.get('original_tuning_profile')),profile,'shared_native_profile',case.get('id'))
        known={r['id']for r in native}
        if not set(case.get('required_original_pickups',[]))<=known:base._fail('unknown_required_original_pickup',case_id=case.get('id'))
    content['original_pickups']=native;content['original_tuning_profile']=profile
    audit['nativeConsumer']='DemoApp._commit_pickup';audit['originalProfile']=profile
    return content,audit


def dependencies(project):
    rows=base._dependencies(project,base.EXTENDED_VERSION);by={r['path']:r for r in rows}
    for name in ('module_loader_v4.gd','package_demo_v4.gd','original_pickups_v4.gd'):
        p=base.RUNTIME/name;by[p.relative_to(base.ROOT).as_posix()]=dict(path=p.relative_to(base.ROOT).as_posix(),sha256=base.sha(p))
    for asset in base._json(ASSETS)['files']:
        p=base.ROOT/asset['runtimePath']
        if base.sha(p)!=asset['sha256']:base._fail('changed_original_pickup_asset',path=asset['runtimePath'])
        by[asset['runtimePath']]=dict(path=asset['runtimePath'],sha256=asset['sha256'],resourcePath='res://'+p.relative_to(project).as_posix())
    return [by[k]for k in sorted(by)]


def decorate_manifest(manifest,stage):
    manifest['extensionSource']=dict(path='pcg/migration/godot_package_v4.py',sha256=base.sha(__file__))
    manifest['nativeBindings']=dict(pickupConsumer='DemoApp._commit_pickup',pickupKinds=['coin','note'],profileInitializer='FoundryCatalog.apply_profile before frame0 only',seamProfileApplication=False,seamResourceReset=False,explicitMetaForNotes=True,sourceAssets=dict(path=ASSETS.relative_to(base.ROOT).as_posix(),sha256=base.sha(ASSETS)))
    manifest['gameAdapter']['api']='bind_player(controller, policy, lifetime, wallet, existing_scope=null, instance_id="", native_meta=null)'
    manifest['resourceInstallation']='Install the pinned original res:// runtime and seven verified native consumer assets once. Package-local adapters are byte-identical copies; the Module never applies a profile or grants resources at a seam.'


def compile_package(*args,**kwargs):
    kwargs['_extension']=__import__(__name__,fromlist=['unused'])
    return base.compile_package(*args,**kwargs)


def verify_package(output_dir,require_loaded=True):
    module=__import__(__name__,fromlist=['unused'])
    result=base.verify_package(output_dir,require_loaded=require_loaded,_extension=module)
    package=Path(output_dir);manifest=base._json(package/'godot-package.json')
    expected={};decorate_manifest(expected_manifest:={'gameAdapter':{}},package)
    base._equal(manifest.get('nativeBindings'),expected_manifest['nativeBindings'],'nativeBindings')
    if not require_loaded:return result
    cases=base._json(package/'cases.json');cases=cases['cases']if isinstance(cases,dict)else cases
    index=base._json(package/'load-evidence/index.json')
    for case,execution in zip(cases,index['executions']):
        receipt=base._json(package/execution['artifacts']['receipt']['path'])
        native=receipt.get('package',{}).get('original_pickups',{})
        if native.get('consumer')!='DemoApp._commit_pickup'or native.get('resources_reset')is not False:base._fail('missing_original_pickup_consumer_receipt',case_id=case['id'])
        claimed={p['id']for p in native.get('pickups',[])if p.get('claimed')}
        if not set(case.get('required_original_pickups',[]))<=claimed:base._fail('original_pickup_not_claimed',case_id=case['id'])
        profile=profile_definition(case.get('original_tuning_profile'))
        if profile:
            base._equal(receipt.get('initial_native_profile'),profile,'observed_native_initial_profile',case['id'])
            base._equal(receipt.get('initial_tuning'),profile['effectiveTuning'],'observed_native_initial_tuning',case['id'])
    result['originalPickupConsumer']=True;result['nativeProfileInitialization']=True
    return result
