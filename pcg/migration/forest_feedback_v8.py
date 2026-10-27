"""Translate original no-reward H/R rooms without inventing a pickup requirement."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,godot_package,core_preserving,boundary_runtime,foundry_feedback_v5 as feedback
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_feedback_runner_v7.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*feedback.SOURCE_DEPENDENCIES,core.STATE/'original-forest-driver-v7.json',
    *list((core.REPO/'pcg/migration/source-forest-v7').glob('*.gd'))]


def purpose(case,raw):
    result=game_world_v4.purpose(case,raw);expected=[a['anchor']for a in case.get('source_action_program',[])if a['action']=='H']
    observed=[c['source_id']for c in raw.get('original_hook_contacts',[])]
    if expected and observed!=expected:result['reasons'].append('original_hook_target_sequence_not_executed')
    result['ok']=not result['reasons'];return result


def program(source,case,variant):
    raw=source['data'];steps=raw.get('steps',[]);gain=5.5;launch=steps[0].get('takeoff',raw['spawn'])if steps else raw['spawn']
    plan=feedback.move(launch,gain)+[feedback.cmd('jump')];age=0;hooks={h['id']:h for h in raw.get('hook_anchors',[])}
    for index,row in enumerate(raw['action_program']):
        if row['action']=='H':
            if row['anchor']not in hooks:raise ValueError('original_hook_id_unresolved:'+row['anchor'])
            if hooks[row['anchor']].get('hang_enabled'):raise ValueError('original_hanging_program_needs_explicit_exit_action')
            delay=(1 if variant==0 else 8)if index==0 else 0
            if index==0 and delay>=6:plan.append(feedback.cmd('jump_release',6));delay-=6
            plan.append(feedback.cmd('grapple',delay,aim_target=hooks[row['anchor']]['position']))
            if index==0 and variant==0:plan.append(feedback.cmd('jump_release',5))
            plan.append(dict(op='wait',trigger=dict(after=20,state='free',timeout=220)))
        elif row['action']=='R':
            if index==0:plan.append(feedback.cmd('jump_release',6))
            plan += [feedback.cmd('shoot',1 if index==0 else 0,direction=row['direction']),dict(op='wait',trigger=dict(after=9,state='free',timeout=180))]
        else:raise ValueError('unsupported_original_action:'+row['action'])
    pickups=case['original_pickups']
    if not pickups:
        if raw.get('reward_position'):raise ValueError('original_reward_consumer_not_bound')
        # Original AirChain runner ends its native program by tracking the
        # authored crown goal. No coin/note exists in these source rooms.
        return plan+feedback.move(raw['goal'],gain)
    point=pickups[0]['position'];reward_support=raw.get('reward_support_id')
    # Reward is reached through the declared source program, then the authored
    # main-route suffix resumes from its original support. No geometry search.
    plan+=feedback.move(point,gain)
    for pickup in pickups:plan += [feedback.cmd('native_pickup_interact',4)]
    landing=next((i for i,s in enumerate(steps)if s.get('support_id')==reward_support),None)
    if landing is None and raw['goal']!=point:
        raise ValueError('original_reward_support_has_no_declared_route_suffix')
    for step in steps[(landing+1)if landing is not None else len(steps):]:
        if step['kind']=='walk':plan+=feedback.move(step['landing'],gain)
        elif step['kind'].startswith('jump'):
            plan+=feedback.move(step['takeoff'],gain)+feedback.jump_to(step['landing'],gain)
        else:raise ValueError('unsupported_original_suffix:'+step['kind'])
    plan+=feedback.move(raw['goal'],gain)
    return plan


def prepare_one(entry,source,variant,out):
    out=Path(out);base=core.REPO/entry['prepared'];original=core.REPO/entry['sourcePackage']
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0]
    original_doc=core.read(original/'module.mapnote.json');original_cases=core.read(original/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,restoration=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases)
    value=game_world_v4.native_fields(cases[0],source)
    if value['decoder_pending_behavior']:raise ValueError('unsupported_native_behavior:'+str(value['decoder_pending_behavior']))
    prefix=program(source,value,variant);exit_id=value['route_spec']['to_port'];port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id)
    tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-forest-native-feedback-v7-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=2200)
    value['generation_rule']['registration_source']='pcg/migration/forest_feedback_v8.py'
    value['original_feedback_routines']=dict(source='Pinned original ForestAirChain input rhythm + exact source steps',variant=variant,sourcePosesAssigned=False)
    entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    intermediate=out.with_name(out.name+'-core');shutil.copytree(base,intermediate)
    core.write(intermediate/'module.mapnote.json',doc);core.write(intermediate/'cases.json',dict(cases=[value]))
    game_world_v4.prepare_one(intermediate,source,out,value)
    value=core.read(out/'cases.json')['cases'][0];value['generation_rule']['registration_source']='pcg/migration/forest_feedback_v8.py'
    doc=core.read(out/'module.mapnote.json');doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    for key in('replay-cases.json','physics-input-cases.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(prepared,out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};cases=[];labels={};rows=[]
    core.write(out/'protocol.json',dict(schema='pcg/original-forest-no-reward-discovery/v8',variants=[dict(firstHookDelay=1),dict(firstHookDelay=8)],maximumSources=14,maximumAttempts=28,selection='First original-program variant with successful native intent, goal and pickups, before calibration or any holdout',scope='No new geometry or resource mechanics; unresolved source behavior explicitly fails'))
    for entry in core.read(Path(prepared)/'manifest.json')['rows']:
        source=sources[entry['id']]
        if source['kind']!='forest'or not source['data'].get('action_program')or source['data'].get('reward_position'):continue
        if not(core.REPO/entry['sourcePackage']).exists():continue
        for variant in(0,1):
            folder=out/(Path(entry['prepared']).name+f'-policy{variant}');row=dict(id=source['id'],moduleId=Path(entry['prepared']).name,variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:
                case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as error:row.update(status='needs_repair',conflict=str(error))
            rows.append(row)
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'original-HR-feedback-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'needs_repair',evidence=evidence,actualGoal=raw.get('ok'),reason=raw.get('reason'),actualHookContacts=raw.get('original_hook_contacts',[]))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,maximumAttempts=28));print(json.dumps(row),flush=True)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,maximumAttempts=28))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.prepared,a.out,a.name)
