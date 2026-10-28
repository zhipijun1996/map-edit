"""Source-authored forest routes with explicit approach, departure and suffix.

Only Router input policies and native observations are added. The original
platforms, grapple/recoil mechanics, purpose checks and quality gates remain.
"""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,godot_package,core_preserving,boundary_runtime,forest_feedback_v8 as previous,foundry_feedback_v5 as feedback
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_feedback_runner_v9.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*previous.SOURCE_DEPENDENCIES]
VARIANTS=[dict(firstHookDelay=1),dict(firstHookDelay=8)]


def purpose(case,raw):
    # Preserve every previous original route, damage, native pickup and exact
    # hook-target assertion. New directional drivers declare their true Hs.
    return previous.purpose(case,raw)


def steps_program(steps,gain=5.5):
    plan=[]
    for step in steps:
        kind=step.get('kind')
        if kind=='walk':plan+=feedback.move(step['landing'],gain)
        elif kind in('jump_gap','jump_rise'):
            plan+=feedback.move(step['takeoff'],gain)+feedback.jump_to(step['landing'],gain)
        elif kind=='drop_through':
            path=step.get('path',[step.get('takeoff'),step['landing']]);start=step.get('takeoff',path[0]);mouth=path[1]if len(path)>2 else start
            plan+=feedback.move(start,gain)
            # A horizontal mouth is reached by walking off the actual edge;
            # a two-point vertical OWP departure uses a genuine Down request.
            plan += [feedback.cmd('jump_release'),feedback.cmd('settle',target_x=mouth[0],deadband=.6,source_native_gain=gain)]
            if abs(mouth[0]-start[0])<.1:plan.append(feedback.cmd('drop_through',1))
            plan += [feedback.cmd('settle',target_x=step['landing'][0],deadband=.6,source_native_gain=gain),feedback.wait_at(step['landing'],after=6)]
        else:raise ValueError('unbound_original_step_kind:'+str(kind))
    return plan


def hr_program(actions,hooks,variant,*,jump=True):
    plan=[feedback.cmd('jump')]if jump else[]
    for index,row in enumerate(actions):
        if row['action']=='H':
            hook=hooks.get(row['anchor'])
            if hook is None:raise ValueError('original_hook_id_unresolved:'+row['anchor'])
            if hook.get('hang_enabled'):raise ValueError('original_hang_release_program_required')
            delay=VARIANTS[variant]['firstHookDelay']if index==0 and jump else 0
            if index==0 and jump and delay>=6:plan.append(feedback.cmd('jump_release',6));delay-=6
            plan.append(feedback.cmd('grapple',delay,aim_target=hook['position']))
            if index==0 and jump and variant==0:plan.append(feedback.cmd('jump_release',5))
            plan.append(dict(op='wait',trigger=dict(after=20,state='free',timeout=220)))
        elif row['action']=='R':
            if index==0 and jump:plan.append(feedback.cmd('jump_release',6))
            plan += [feedback.cmd('shoot',1 if index==0 and jump else 0,direction=row['direction']),dict(op='wait',trigger=dict(after=9,state='free',timeout=180))]
        else:raise ValueError('unsupported_original_action:'+str(row['action']))
    return plan


def _suffix(raw,point):
    steps=raw.get('steps',[]);support=raw.get('reward_support_id')
    # Hard source post_landing_steps explicitly start at the airborne receiver.
    if steps and steps[0].get('from_support_id')==support:return steps
    hit=next((i for i,s in enumerate(steps)if s.get('support_id')==support),None)
    if hit is not None:return steps[hit+1:]
    for name,value in raw.get('routes',{}).items():
        route=value.get('steps',[])if isinstance(value,dict)else value
        hit=next((i for i,s in enumerate(route)if s.get('support_id')==support),None)
        if hit is None:continue
        suffix=route[hit+1:]
        last=suffix[-1].get('support_id')if suffix else support
        if last==raw.get('exit_support_id'):return suffix
        # Authored side reward descends to an existing main-route support.
        j=next((i for i,s in enumerate(steps)if s.get('support_id')==last),None)
        if j is not None:return suffix+steps[j+1:]
    if raw['goal']==point or not steps:return []
    raise ValueError('original_reward_support_has_no_declared_route_suffix')


def program(source,case,variant):
    raw=source['data'];hooks={h['id']:h for h in raw.get('hook_anchors',[])};actions=raw.get('action_program',[]);plan=[]
    if source['id'].startswith('forest_directional_geometry__'):
        actions=[dict(action='H',anchor='side_ring'),dict(action='R',direction=[-1,0])]
        if not source['id'].endswith('build_narrow'):actions += [dict(action='H',anchor='arch_exit_ring'),dict(action='H',anchor='crown_ring')]
        case['source_action_program']=actions
        return feedback.move(raw['spawn'])+hr_program(actions,hooks,variant)+feedback.move(raw['goal'])
    if not actions:raise ValueError('original_named_geometry_driver_not_bound')
    approach=raw.get('approach_steps',[])
    outside=raw.get('departure',{}).get('ground_required')is False and not approach
    if approach:
        plan += steps_program(approach)+feedback.move(raw['action_start'])
    elif outside:
        departure=raw['departure'];target=hooks[actions[0]['anchor']]
        plan += feedback.move(raw['spawn'])+[feedback.cmd('jump_release'),feedback.cmd('settle',target_x=departure['path'][-1][0],deadband=.6,source_native_gain=12),dict(op='wait',trigger=dict(source_min_y=target['position'][1]+20,timeout=300)),feedback.cmd('axis',value=0)]
    elif raw.get('difficulty')=='normal' and raw.get('steps'):
        # Preserve the source's main/side branch approach before invoking H,
        # rather than firing from the unrelated global spawn or first gap.
        route=raw.get('routes',{}).get('upper_reward',raw['steps'])
        first=hooks[actions[0]['anchor']]['position'];options=[]
        for i,step in enumerate(route):
            point=step.get('takeoff',step.get('landing'))
            if point is not None:options.append((abs(first[0]-point[0])+abs(first[1]-point[1]),i,point))
        _,index,launch=min(options)
        plan += steps_program(route[:index])+feedback.move(launch)
    else:plan+=feedback.move(raw['spawn'])
    plan += hr_program(actions,hooks,variant,jump=not outside)
    pickups=case['original_pickups']
    if pickups:
        point=pickups[0]['position'];plan+=feedback.move(point)
        for p in pickups:plan += [feedback.cmd('native_pickup_interact',4)]
        plan+=steps_program(_suffix(raw,point))
    elif raw.get('reward_position'):raise ValueError('original_reward_consumer_not_bound')
    return plan+feedback.move(raw['goal'])


def prepare_one(entry,source,variant,out):
    out=Path(out);base=core.REPO/entry['prepared'];meta=core.read(base/'migration.json');original=core.REPO/meta['sourcePath']
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0]
    original_doc=core.read(original/'module.mapnote.json');original_cases=core.read(original/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,restoration=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases)
    value=game_world_v4.native_fields(cases[0],source)
    if value['decoder_pending_behavior']:raise ValueError('unbound_native_behavior:'+str(value['decoder_pending_behavior']))
    value.pop('recorded_frames',None);prefix=program(source,value,variant)
    exit_id=value['route_spec']['to_port'];port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id)
    tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-forest-source-v9-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=3000)
    value['generation_rule']['registration_source']='pcg/migration/forest_feedback_v9.py'
    value['original_feedback_routines']=dict(source='Pinned original H/R rhythm and explicit source approach/departure/routes',variant=variant,sourcePosesAssigned=False)
    entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    intermediate=out.with_name(out.name+'-core');shutil.copytree(base,intermediate)
    core.write(intermediate/'module.mapnote.json',doc);core.write(intermediate/'cases.json',dict(cases=[value]))
    game_world_v4.prepare_one(intermediate,source,out,value)
    # Native field binding preserves exact original H/R. The directional source
    # encodes the same sequence through its pinned named input driver instead.
    candidate=core.read(out/'cases.json')['cases'][0]
    candidate['source_action_program']=value['source_action_program'];candidate['generation_rule']['registration_source']='pcg/migration/forest_feedback_v9.py'
    doc=core.read(out/'module.mapnote.json');doc,cases,bindings=boundary_runtime.bind(doc,[candidate]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    for key in('replay-cases.json','physics-input-cases.json','physics.json','package.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};cases=[];labels={};rows=[]
    entries=[r for r in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']if r['sourceKind']=='forest']
    core.write(out/'protocol.json',dict(schema='pcg/original-forest-binding/v9',variants=VARIANTS,maximumSources=35,maximumAttempts=70,selection='First source-exact input variant passing original purpose before calibration and holdout',forbidden=['geometry optimization from holdout','reward substitution','actor pose assignment','original assertion removal']))
    for entry in entries:
        source=sources[entry['referenceId']]
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(id=source['id'],moduleId=entry['stableId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:
                case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as error:row.update(status='behavior_binding_gap',conflict=str(error))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0,maximumAttempts=70))
    if not cases:return
    # One frozen controller for this preregistered discovery, no new holdout.
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-policy-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,actualGoal=raw.get('ok'),reason=raw.get('reason'),actualHookContacts=raw.get('original_hook_contacts',[]))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,maximumAttempts=70));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],check=check,reason=row['reason'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.out,a.name)
