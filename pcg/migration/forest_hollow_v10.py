"""Bind seven original hollow input drivers; preserve core and native checks."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,godot_package,core_preserving,boundary_runtime,forest_feedback_v9 as previous,foundry_feedback_v5 as feedback
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_hollow_runner_v10.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*previous.SOURCE_DEPENDENCIES,core.STATE/'original-forest-drivers-v10.json',*list((core.REPO/'pcg/migration/source-forest-v10').glob('*.gd'))]
purpose=previous.purpose
VARIANTS=[dict(sourceJumpHookDelay=7,standingCavityHook=False),dict(sourceJumpHookDelay=1,standingCavityHook=True)]


def hop(anchor,hooks,variant,*,jump=True,recoil=True):
    plan=[]
    if jump:
        plan.append(feedback.cmd('jump'))
        if variant==0:plan += [feedback.cmd('jump_release',6),feedback.cmd('grapple',1,aim_target=hooks[anchor]['position'])]
        else:plan += [feedback.cmd('grapple',1,aim_target=hooks[anchor]['position']),feedback.cmd('jump_release',5)]
    else:plan.append(feedback.cmd('grapple',aim_target=hooks[anchor]['position']))
    plan.append(dict(op='wait',trigger=dict(after=21,state='free',timeout=240)))
    if recoil:plan += [feedback.cmd('shoot',direction=[-1,0]),dict(op='wait',trigger=dict(after=9,state='free',timeout=180))]
    return plan


def program(source,case,variant):
    raw=source['data'];hooks={h['id']:h for h in raw['hook_anchors']};cavity='cavity_ring_a'in hooks;elbow=source['id'].endswith('cavity_elbow')
    if cavity:
        actions=[dict(action='H',anchor='cavity_ring_a'),dict(action='R',direction=[-1,0]),dict(action='H',anchor='cavity_ring_b'),dict(action='R',direction=[-1,0])]
        plan=feedback.move(raw['spawn'],12)+hop('cavity_ring_a',hooks,variant,jump=variant==0)+feedback.move(raw['nodes']['B']['position'],12)
        if elbow:
            bay=next(p['rect']for p in raw['platforms']if p['id']=='cavity_bay');limit=bay[0]+bay[2]+12
            plan += [feedback.cmd('axis',value=1),dict(op='wait',trigger=dict(source_right_of=limit,timeout=180)),feedback.cmd('axis',value=0)]
        plan+=hop('cavity_ring_b',hooks,variant,jump=(variant==0 and not elbow))
    else:
        upper=source['id']=='forest_hollow_upper_candidate__build';actions=[dict(action='H',anchor='upper_window_ring')]
        if not upper:actions.append(dict(action='R',direction=[-1,0]))
        launch=[108,raw['spawn'][1]]if upper else raw['spawn'];plan=feedback.move(launch,12)+hop('upper_window_ring',hooks,variant,recoil=not upper)
    case['source_action_program']=actions
    case['original_named_driver']=dict(sourceCommit='879b39eaa869be70cb799dedd1bb6ffc35e0b92f',driver='tests/forest_hollow_upper_runner.gd'if cavity or source['id'].startswith('forest_hollow_upper')else'tests/forest_hollow_trunk_runner.gd',case='cavity/elbow'if cavity else'H0R'if source['id'].startswith('forest_hollow_upper')else'upper_HR',onlyInputTranslation=True)
    return plan+feedback.move(raw['goal'],12)


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
    value.update(id=value['id']+f'-forest-hollow-v10-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=3000)
    value['generation_rule']['registration_source']='pcg/migration/forest_hollow_v10.py'
    value['original_feedback_routines']=dict(source='Pinned original H/R rhythm and explicit source approach/departure/routes',variant=variant,sourcePosesAssigned=False)
    entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    intermediate=out.with_name(out.name+'-core');shutil.copytree(base,intermediate)
    core.write(intermediate/'module.mapnote.json',doc);core.write(intermediate/'cases.json',dict(cases=[value]))
    game_world_v4.prepare_one(intermediate,source,out,value)
    # Native field binding preserves exact original H/R. The directional source
    # encodes the same sequence through its pinned named input driver instead.
    candidate=core.read(out/'cases.json')['cases'][0]
    candidate['source_action_program']=value['source_action_program'];candidate['generation_rule']['registration_source']='pcg/migration/forest_hollow_v10.py'
    doc=core.read(out/'module.mapnote.json');doc,cases,bindings=boundary_runtime.bind(doc,[candidate]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    for key in('replay-cases.json','physics-input-cases.json','physics.json','package.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};cases=[];labels={};rows=[]
    entries=[r for r in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']if r['sourceKind']=='forest'and ('forest_hollow_trunk_geometry__'in r['referenceId']or'forest_hollow_upper_candidate__'in r['referenceId'])]
    core.write(out/'protocol.json',dict(schema='pcg/original-hollow-binding/v10',variants=VARIANTS,maximumSources=7,maximumAttempts=14,selection='First source-exact driver policy passing original purpose before calibration/holdout',sourceKeysRemainOriginal=True,scope='Previously unbound named driver only; no rerun of exposed v9 holdout'))
    for entry in entries:
        source=sources[entry['referenceId']]
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(id=source['id'],moduleId=entry['stableId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as error:row.update(status='behavior_binding_gap',conflict=str(error))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0,maximumAttempts=14))
    if not cases:return
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-hollow-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,actualGoal=raw.get('ok'),reason=raw.get('reason'),actualHookContacts=raw.get('original_hook_contacts',[]))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,maximumAttempts=14));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],check=check,reason=row['reason'])),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.out,a.name)
