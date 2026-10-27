"""Original source approach corrections; no core/ability/resource changes."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,godot_package,core_preserving,boundary_runtime,forest_feedback_v9 as forest,foundry_feedback_v5 as feedback
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_source_approach_runner_v13.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*forest.SOURCE_DEPENDENCIES,core.STATE/'original-forest-drop-driver-v13.json',core.REPO/'pcg/migration/source-forest-v13/forest_depth_region_trace.gd']
def purpose(case,raw):
    result=forest.purpose(case,raw)
    expected=sum(a.get('action')=='R'for a in case.get('source_action_program',[]))
    if raw.get('shots',0)<expected:result['reasons'].append('original_recoil_actions_not_actually_accepted')
    result['ok']=not result['reasons'];return result

def program(source,case,variant):
    policy=copy.deepcopy(source);raw=source['data'];identifier=source['id']
    if identifier.endswith('double_fruit_s'):
        policy['data']['difficulty']='hard';policy['data']['spawn']=raw['steps'][0]['takeoff'][:]
    elif identifier.endswith('thorn_side_passage')or identifier.endswith('crown_hook_relay'):
        shore=next(p['rect']for p in raw['platforms']if p['id']==raw['entry_support_id']);policy['data']['spawn']=[shore[0]+shore[2]-32,raw['spawn'][1]]
    plan=forest.program(policy,case,variant)
    drops=[s['landing']for s in raw.get('approach_steps',[])if s.get('kind')=='drop_through']
    for c in plan:
        trigger=c.get('trigger',{});goal=trigger.get('migration_goal')
        if goal and any(abs(goal[0]+goal[2]/2-p[0])<.1 and abs(goal[1]+goal[3]/2-p[1])<.1 for p in drops):trigger['source_drop_until_y']=goal[1]+goal[3]/2
    case['original_source_approach_repair']=dict(revision=1,maximumRevisions=2,sourceSpawnUnchanged=True,actualWalkLaunch=policy['data']['spawn'],sourceDropPolicy='Pinned original drive_drop periodic native Down on intervening supports; no collision edits',sourceProgram=copy.deepcopy(raw.get('action_program',[])))
    return plan

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
    value.update(id=value['id']+f'-forest-approach-v13-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=3000)
    value['generation_rule']['registration_source']='pcg/migration/forest_source_approach_v13.py'
    value['original_feedback_routines']=dict(source='Pinned original H/R rhythm and explicit source approach/departure/routes',variant=variant,sourcePosesAssigned=False)
    entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    intermediate=out.with_name(out.name+'-core');shutil.copytree(base,intermediate)
    core.write(intermediate/'module.mapnote.json',doc);core.write(intermediate/'cases.json',dict(cases=[value]))
    game_world_v4.prepare_one(intermediate,source,out,value)
    # Native field binding preserves exact original H/R. The directional source
    # encodes the same sequence through its pinned named input driver instead.
    candidate=core.read(out/'cases.json')['cases'][0]
    candidate['source_action_program']=value['source_action_program'];candidate['generation_rule']['registration_source']='pcg/migration/forest_source_approach_v13.py'
    doc=core.read(out/'module.mapnote.json');doc,cases,bindings=boundary_runtime.bind(doc,[candidate]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    for key in('replay-cases.json','physics-input-cases.json','physics.json','package.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]

def discover(out,name,prepare_only=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};ids={'forest_exploration_modules__double_fruit_s','forest_exploration_modules__thorn_side_passage','forest_exploration_modules__crown_hook_relay','forest_exploration_modules__deep_root_switchback'};cases=[];rows=[];labels={}
    core.write(out/'protocol.json',dict(schema='pcg/original-source-approach-repair/v13',maximumSources=4,maximumAttempts=8,revision=1,maximumRevisions=2,selection='First fixed source-approach variant passing original full purpose before calibration/holdout',geometryChanged=False,sourceSpawnAssigned=False,details='Real walk from unchanged spawn to original first takeoff or32px inside actual entry edge; original drop driver repeats genuine Down on intervening OWP'))
    for entry in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']:
        if entry['referenceId']not in ids:continue
        source=sources[entry['referenceId']]
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(id=source['id'],moduleId=entry['stableId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as e:row.update(status='behavior_binding_gap',conflict=str(e))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0))
    if not cases or prepare_only:return
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-approach-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,reason=raw.get('reason'),actualHookContacts=raw.get('original_hook_contacts',[]))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],check=check,reason=row['reason'])),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);p.add_argument('--prepare-only',action='store_true');a=p.parse_args();discover(a.out,a.name,a.prepare_only)
