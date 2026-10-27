"""Original forest reward routes with the actual region chest OR consumer."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,core_preserving,boundary_runtime,forest_feedback_v9 as forest,foundry_feedback_v5 as feedback,godot_package_v5 as native
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_region_runner_v12.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*forest.SOURCE_DEPENDENCIES,Path(native.__file__),*[core.REPO/'pcg/migration/runtime'/name for name in ('module_loader_v5.gd','package_demo_v5.gd','native_profile_v5.gd','original_region_chests_v5.gd')],core.STATE/'original-region-v5-assets.json',core.STATE/'original-forest-reward-sources-v5.json',*list((core.REPO/'pcg/migration/source-forest-reward-v5').glob('*.gd'))]
IDS={'forest_exploration_modules__backlook_fruit_cache','forest_exploration_modules__thorn_7_root_fold','forest_exploration_modules__thorn_z_root_switchback','forest_playful_module_variants__l_hollow_reward_loop','forest_playful_module_variants__z_hollow_inner_cache','forest_exploration_places__z_descending_return_v0','forest_exploration_places__z_descending_return_v1','forest_exploration_fallen_trunk__v0','forest_exploration_fallen_trunk__v1'}


def chest_for(source):
    raw=source['data'];identifier=source['id'];risk=raw.get('risk_reward',{})
    if 'z_descending_return'in identifier:coins,notes,tier,origin=6,2,'hard_optional','forest_exploration_network._install_onward_places + _install_stage_routes_and_rewards'
    elif 'fallen_trunk'in identifier:coins,notes,tier,origin=4,1,'hard_optional','forest_exploration_network._install_onward_places + _install_stage_routes_and_rewards'
    elif 'backlook_fruit_cache'in identifier:coins,notes,tier,origin=4,1,'medium','forest_exploration_world shared_choice _reward(raw.coins,max(1,raw.notes))'
    elif 'thorn_7_root_fold'in identifier or'thorn_z_root_switchback'in identifier:coins,notes,tier,origin=4,1,'medium','forest_exploration_world installed branch cache overrides'
    elif identifier.startswith('forest_playful_module_variants__'):
        if type(risk.get('coins'))is not int or type(risk.get('notes'))is not int:raise ValueError('original_reward_amount_missing')
        coins,notes,tier,origin=risk['coins'],risk['notes'],risk['tier'],'Source module risk_reward declaration; new offline binding to original OR consumer, not original-world admission'
    else:raise ValueError('original_region_reward_payload_not_bound')
    chest=dict(id='source_cache',position=raw['reward_position'][:],tier=tier,items=[],coins=coins,reward_mode='resources',resources=[dict(kind='coin',amount=coins),dict(kind='note',amount=notes)])
    native.chest_definition(chest)
    return chest,dict(sourceCommit=source['sourceCommit'],origin=origin,rawRewardPositionExact=True,consumer=native.SERVICE)


def route_steps(raw,name):
    value=raw.get('routes',{}).get(name)
    if value is None:raise ValueError('original_route_missing:'+name)
    if isinstance(value,dict):
        if value.get('kind')!='ordinary_sequence':raise ValueError('original_nonordinary_route_not_bound:'+name)
        value=value['steps']
    return value


def itinerary(source):
    raw=source['data'];identifier=source['id']
    if identifier.endswith('backlook_fruit_cache'):return route_steps(raw,'backlook_cache'),route_steps(raw,'cache_return')+route_steps(raw,'main')
    if identifier.endswith('thorn_7_root_fold')or identifier.endswith('thorn_z_root_switchback'):return route_steps(raw,'reward'),route_steps(raw,'returning')+route_steps(raw,'main')
    if identifier.endswith('l_hollow_reward_loop'):return route_steps(raw,'reward'),route_steps(raw,'reward_onward')
    if identifier.endswith('z_hollow_inner_cache'):
        prefix=route_steps(raw,'reward_other_exit');main=route_steps(raw,'main');last=prefix[-1]['support_id'];hit=next((i for i,s in enumerate(main)if s.get('support_id')==last),None)
        if hit is None:raise ValueError('original_reward_exit_has_no_main_route_suffix')
        return route_steps(raw,'reward'),prefix+main[hit+1:]
    if 'z_descending_return'in identifier:return route_steps(raw,'reward'),route_steps(raw,'returning')
    if 'fallen_trunk'in identifier:return route_steps(raw,'inner_reward'),route_steps(raw,'cache_return')
    raise ValueError('original_reward_route_not_bound')


def program(source,case,variant):
    before,after=itinerary(source);point=source['data']['reward_position'];plan=forest.steps_program(before)+feedback.move(point)
    plan += [feedback.cmd('native_region_interact',4),feedback.cmd('native_region_choose',kind='coin')]
    plan+=forest.steps_program(after)+feedback.move(source['data']['goal'])
    if variant==1:
        # Authored ordinary jumps remain ordinary. This second preregistered
        # control releases a held jump after16frames instead of at reception.
        revised=[]
        for command in plan:
            revised.append(command)
            if command['op']=='jump':revised.append(feedback.cmd('jump_release',16))
        plan=revised
    case['source_action_program']=[]
    case['source_optional_action_program']=copy.deepcopy(source['data'].get('action_program',[]))
    case['source_ordinary_reward_itinerary']=dict(before=copy.deepcopy(before),after=copy.deepcopy(after),optionalHNotRequired=True)
    return plan


def purpose(case,raw):
    result=game_adapter.purpose(case,raw);snapshot=raw.get('original_region_chests',{})
    if snapshot.get('consumer')!=native.SERVICE or snapshot.get('interaction_radius')!=80 or snapshot.get('resources_reset')is not False or snapshot.get('modal_open')is not False:
        result['reasons'].append('original_region_consumer_not_bound_or_modal_unfinished')
    for wanted in case.get('required_region_chest_choices',[]):
        chest=next((c for c in snapshot.get('chests',[])if c.get('id')==wanted['id']),None)
        event=next((e for e in snapshot.get('events',[])if e.get('type')=='native_region_choose'and e.get('kind')==wanted['kind']and e.get('id')==wanted['id']and e.get('accepted')),None)
        spec=next(c for c in case['original_region_chests']if c['id']==wanted['id']);amount=next(r['amount']for r in spec['resources']if r['kind']==wanted['kind'])
        if chest is None or not chest.get('claimed')or event is None:result['reasons'].append('original_region_choice_not_actually_claimed');continue
        if snapshot.get('coins')!=(amount if wanted['kind']=='coin'else 0)or snapshot.get('notes')!=(amount if wanted['kind']=='note'else 0):result['reasons'].append('original_region_OR_amount_not_exact')
    result['ok']=not result['reasons'];return result


def prepare_one(entry,source,variant,out):
    out=Path(out);base=core.REPO/entry['prepared'];original=core.REPO/core.read(base/'migration.json')['sourcePath']
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0];original_doc=core.read(original/'module.mapnote.json');original_cases=core.read(original/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,restoration=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases);value=copy.deepcopy(cases[0]);chest,provenance=chest_for(source)
    pending=[k for k in value.get('decoder_pending_behavior',[])if k not in('action_program','original_branch_chest_consumer','original_coin_note_pickup_consumer')]
    if pending:raise ValueError('unbound_original_behavior:'+str(pending))
    value.update(decoder_pending_behavior=[],original_pickups=[],required_original_pickups=[],original_region_chests=[chest],required_region_chest_choices=[dict(id=chest['id'],kind='coin')],source_reward_consumer_provenance=provenance)
    for key in('recorded_frames','module_sha256','factory_evidence'):value.pop(key,None)
    prefix=program(source,value,variant);exit_id=value['route_spec']['to_port'];port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id);tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-forest-region-v12-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=6000)
    value['generation_rule']['registration_source']='pcg/migration/forest_region_v12.py';entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    gc=doc['generationContract'];identifier=doc['id']+'/original-region-chest-'+chest['id'];x,y=chest['position'];doc['objects'].append(dict(id=identifier,type='reward',x=x-12,y=y-12,w=24,h=24,rotation=0,label='原区域二选一奖励',note=provenance['origin'],mechanics=dict(service=native.SERVICE,interactionRadius=80,selection='OR',source=copy.deepcopy(chest))))
    gc['space']['occupancy']['objectIds'].append(identifier);gc['composition']['cells'].append(dict(id=identifier,contentVersion='sha256:'+'0'*64,objectIds=[identifier]));gc['requiredServices']=['run_wallet','meta_progression','region_state'];gc['generation']['parameters'].update(controlPlan=value['control_plan'],nativeOriginalRegionConsumer=provenance)
    for route in gc['routes']:route['resourceProfile']=dict(requiredRegionChestChoices=value['required_region_chest_choices'],sourceReward=copy.deepcopy(chest),optionalHNotRequired=True)
    annotate(doc);doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=native.bind_case_behavior(doc,cases)
    out.mkdir(parents=True,exist_ok=False)
    for name in('migration.json','duplicates.json'):
        if(base/name).exists():shutil.copy2(base/name,out/name)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',nativeRegionReward=provenance);core.write(out/'migration.json',meta)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings);core.contract(out/'module.mapnote.json',refresh=True);native.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(out,name,prepare_only=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};cases=[];rows=[];labels={}
    core.write(out/'protocol.json',dict(schema='pcg/original-forest-region-reward-binding/v12',maximumSources=9,maximumAttempts=18,variants=['Authored full-held ordinary steps','Same source itinerary; release jump at16frames'],selection='First original complete reward/return itinerary passing actual original consumer before calibration/holdout',geometryChanged=False,noCoinSubstitution=True,originalWorldAdmission='Not claimed for uninstalled playful variants',sourceKeysRemainOriginal=True))
    for entry in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']:
        if entry['referenceId']not in IDS:continue
        source=sources[entry['referenceId']]
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(id=source['id'],moduleId=entry['stableId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as e:row.update(status='behavior_binding_gap',conflict=str(e))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0))
    if not cases or prepare_only:return
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-region-reward-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,reason=raw.get('reason'),originalRegion=raw.get('original_region_chests'))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],check=check,reason=row['reason'])),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);p.add_argument('--prepare-only',action='store_true');a=p.parse_args();discover(a.out,a.name,a.prepare_only)
