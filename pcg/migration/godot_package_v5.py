"""Isolated native exact-fixture and region-choice extension; old backends frozen."""
from __future__ import annotations
import copy,types
from pathlib import Path
from . import godot_package as base,godot_package_v4 as v4
VERSION='foundation-data-runtime/v5'
SCENES=[('module','module_loader_v5.gd'),('demo','package_demo_v5.gd')]
ASSETS=base.ROOT/'pcg/migration/foundation-v1/original-region-v5-assets.json'
SOURCES=base.ROOT/'pcg/migration/foundation-v1/original-resource-driver-v9.json'
SERVICE='DemoApp._region_interact/_claim_region_chest'

def required(doc,cases):return any(c.get('original_fixture_profile')or c.get('original_region_chests')for c in cases)or any(o.get('mechanics',{}).get('service')==SERVICE for o in doc.get('objects',[]))

def exact_profile(profile,fixture):
    if fixture is None:return v4.profile_definition(profile),None
    if not isinstance(fixture,dict)or set(fixture)!={'provider','id','source','initializer','max_jumps','max_air_shots'}:base._fail('invalid_original_fixture_profile')
    jumps,shots=fixture['max_jumps'],fixture['max_air_shots']
    if type(jumps)is not int or type(shots)is not int or (jumps,shots)not in ((1,2),(2,2)):base._fail('unsupported_exact_fixture_capacity')
    filename='challenge_recoil_tests.gd'if jumps==1 else'branch_library_runner.gd'
    source=next(r for r in base._json(SOURCES)['files']if Path(r['localPath']).name==filename)
    expected=dict(path=source['localPath'],sha256=source['sha256'])
    base._equal(fixture['source'],expected,'exact_fixture_source')
    if base.sha(base.ROOT/expected['path'])!=expected['sha256']:base._fail('exact_fixture_source_changed')
    identifier=f'original-fixture-{jumps}j{shots}s'
    base._equal(fixture['provider'],'original_fixture/v1','fixture_provider');base._equal(fixture['id'],identifier,'fixture_id')
    base._equal(fixture['initializer'],'ChallengeRecoilTests._fixture'if jumps==1 else'BranchLibraryRunner.fixture','fixture_initializer')
    wanted=dict(id=identifier,overrides=dict(max_jumps=jumps,max_air_shots=shots),abilities=['move','jump','shot_recoil']+(['double_jump']if jumps==2 else[]),effectiveTuning=dict(max_jumps=jumps,max_air_shots=shots))
    base._equal(profile,wanted,'exact_fixture_profile')
    return wanted,copy.deepcopy(fixture)


def chest_definition(chest):
    if not isinstance(chest,dict)or set(chest)!={'id','position','tier','items','coins','reward_mode','resources'}:base._fail('invalid_original_region_chest')
    if not isinstance(chest['id'],str)or not chest['id']or not isinstance(chest['position'],list)or len(chest['position'])!=2:base._fail('invalid_region_chest_identity')
    if chest['items']!=[]or chest['reward_mode']!='resources':base._fail('unsupported_region_item_chest')
    if chest['tier']not in ('medium','high','hard_optional'):base._fail('unknown_original_region_tier')
    resources=chest['resources']
    if not isinstance(resources,list)or len(resources)!=2 or [r.get('kind')for r in resources]!=['coin','note']:base._fail('region_chest_requires_original_coin_note_OR')
    if any(set(r)!={'kind','amount'}or type(r['amount'])is not int or r['amount']<0 for r in resources)or not any(r['amount']>0 for r in resources):base._fail('invalid_original_region_resource_amount')
    base._equal(chest['coins'],resources[0]['amount'],'original_region_coin_field')
    return copy.deepcopy(chest)


def _filtered(doc,cases):
    d=copy.deepcopy(doc);c=copy.deepcopy(cases)
    d['objects']=[o for o in d.get('objects',[])if o.get('mechanics',{}).get('service')!=SERVICE]
    if cases and cases[0].get('original_fixture_profile'):
        d['generationContract']['generation'].setdefault('parameters',{})['original_tuning_profile']=None
        for case in c:case.pop('original_tuning_profile',None)
    return d,c


def bind_case_behavior(doc,cases):
    d,c=_filtered(doc,cases);result=v4.bind_case_behavior(d,c)
    result['objects']+=copy.deepcopy([o for o in doc.get('objects',[])if o.get('mechanics',{}).get('service')==SERVICE])
    if cases:
        profile,fixture=exact_profile(cases[0].get('original_tuning_profile'),cases[0].get('original_fixture_profile'))
        parameters=result['generationContract']['generation'].setdefault('parameters',{})
        parameters['original_tuning_profile']=profile;parameters['original_fixture_profile']=fixture
    return result


def audit_cases(doc,cases,*,require_replay=True):
    d,c=_filtered(doc,cases);content,audit=v4.audit_cases(d,c,require_replay=require_replay)
    chests=[]
    for obj in doc.get('objects',[]):
        m=obj.get('mechanics',{})
        if m.get('service')!=SERVICE:continue
        if obj.get('type')!='reward':base._fail('region_chest_must_be_reward_object')
        base._equal([obj['w'],obj['h']],[24,24],obj['id']+'/region_chest_visual_size')
        base._equal(m.get('interactionRadius'),80,obj['id']+'/original_region_radius');base._equal(m.get('selection'),'OR',obj['id']+'/original_region_selection')
        chest=chest_definition(m.get('source'));base._equal(base._center(obj),chest['position'],obj['id']+'/region_chest_position');chests.append(chest)
    if len({x['id']for x in chests})!=len(chests):base._fail('duplicate_region_chest_id')
    profile,fixture=exact_profile(cases[0].get('original_tuning_profile'),cases[0].get('original_fixture_profile'))if cases else(None,None)
    parameters=doc['generationContract']['generation'].get('parameters',{})
    base._equal(parameters.get('original_tuning_profile'),profile,'v5_profile_document_binding');base._equal(parameters.get('original_fixture_profile'),fixture,'v5_fixture_document_binding')
    if doc['generationContract'].get('requiredNativeProfile')is not None:base._equal(doc['generationContract']['requiredNativeProfile'],profile,'v5_required_native_profile_binding')
    for case in cases:
        base._equal([chest_definition(x)for x in case.get('original_region_chests',[])],chests,'native_region_chests',case.get('id'))
        base._equal(exact_profile(case.get('original_tuning_profile'),case.get('original_fixture_profile')),(profile,fixture),'shared_exact_fixture',case.get('id'))
        for choice in case.get('required_region_chest_choices',[]):
            known=next((x for x in chests if x['id']==choice.get('id')),None)
            if known is None or choice.get('kind')not in ('coin','note')or not any(r['kind']==choice['kind']and r['amount']>0 for r in known['resources']):base._fail('unknown_or_unavailable_required_region_choice')
    content.update(original_tuning_profile=profile,original_fixture_profile=fixture,original_region_chests=chests)
    audit.update(exactFixture=fixture,nativeRegionConsumer=SERVICE,regionSelection='OR')
    return content,audit


def dependencies(project):
    by={r['path']:r for r in v4.dependencies(project)}
    paths=[base.RUNTIME/name for name in ('module_loader_v5.gd','package_demo_v5.gd','native_profile_v5.gd','original_region_chests_v5.gd')]
    paths += [base.ROOT/r['localPath']for r in base._json(SOURCES)['files']if Path(r['localPath']).name in ('challenge_recoil_tests.gd','branch_library_runner.gd')]
    paths += [ASSETS,SOURCES]
    for p in paths:by[p.relative_to(base.ROOT).as_posix()]=dict(path=p.relative_to(base.ROOT).as_posix(),sha256=base.sha(p))
    for row in base._json(ASSETS)['files']:
        p=base.ROOT/row['runtimePath']
        if base.sha(p)!=row['sha256']:base._fail('original_region_asset_changed')
        by[row['runtimePath']]=dict(path=row['runtimePath'],sha256=row['sha256'],resourcePath='res://'+p.relative_to(project).as_posix())
    return [by[k]for k in sorted(by)]


def decorate_manifest(manifest,stage):
    manifest['extensionSource']=dict(path='pcg/migration/godot_package_v5.py',sha256=base.sha(__file__))
    manifest['nativeBindings']=dict(pickupConsumer='DemoApp._commit_pickup',regionConsumer=SERVICE,regionRadius=80,selection='OR',profileInitializer='native_profile_v5.initialize_once before frame0',seamProfileApplication=False,seamResourceReset=False,explicitSharedRegionState=True,exactFixtureSources=dict(path=SOURCES.relative_to(base.ROOT).as_posix(),sha256=base.sha(SOURCES)))
    manifest['gameAdapter']['api']='bind_player(controller, policy, lifetime, wallet, existing_scope=null, instance_id="", native_meta=null, native_region_state=null)'


def compile_package(*args,**kwargs):
    kwargs['_extension']=__import__(__name__,fromlist=['unused']);return base.compile_package(*args,**kwargs)


def verify_package(output_dir,require_loaded=True):
    module=__import__(__name__,fromlist=['unused']);result=base.verify_package(output_dir,require_loaded=require_loaded,_extension=module)
    p=Path(output_dir);manifest=base._json(p/'godot-package.json');expected={'gameAdapter':{}};decorate_manifest(expected,p)
    base._equal(manifest.get('nativeBindings'),expected['nativeBindings'],'nativeBindings_v5')
    if not require_loaded:return result
    cases=base._json(p/'cases.json')['cases'];index=base._json(p/'load-evidence/index.json')
    for case,execution in zip(cases,index['executions']):
        receipt=base._json(p/execution['artifacts']['receipt']['path']);snapshot=receipt.get('package',{})
        profile,fixture=exact_profile(case.get('original_tuning_profile'),case.get('original_fixture_profile'))
        if profile:base._equal(receipt.get('initial_native_profile'),profile,'initial_exact_profile')
        if fixture:base._equal(receipt.get('initial_fixture_profile'),fixture,'initial_exact_fixture_source')
        pickups=snapshot.get('original_pickups',{});claimed={x['id']for x in pickups.get('pickups',[])if x.get('claimed')}
        if not set(case.get('required_original_pickups',[]))<=claimed:base._fail('original_pickup_not_claimed')
        region=snapshot.get('original_region_chests',{})
        if case.get('original_region_chests')and(region.get('consumer')!=SERVICE or region.get('resources_reset')is not False or region.get('modal_open')):base._fail('missing_or_unfinished_native_region_consumer')
        for wanted in case.get('required_region_chest_choices',[]):
            chest=next((x for x in region.get('chests',[])if x['id']==wanted['id']),None)
            if chest is None or not chest.get('claimed')or not any(x.get('type')=='native_region_choose'and x.get('id')==wanted['id']and x.get('kind')==wanted['kind']and x.get('accepted')for x in region.get('events',[])):base._fail('required_region_choice_not_claimed')
    result.update(exactFixtureProfile=True,originalRegionChoiceConsumer=True);return result


def run_package_validation(*args,**kwargs):
    # Reuse the existing actual execution implementation, isolated verifier only.
    runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__)
    runner.__kwdefaults__=base.run_package_validation.__kwdefaults__
    return runner(*args,**kwargs)
