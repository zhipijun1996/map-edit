"""Correct custom source observation triggers without editing frozen drivers."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,godot_package,core_preserving,boundary_runtime,forest_feedback_v9 as forest,forest_hollow_v10 as hollow,foundry_feedback_v5 as feedback
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=hollow.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*hollow.SOURCE_DEPENDENCIES]

def program(source,case,variant):
    p=(hollow if 'cavity_elbow'in source['id']else forest).program(source,case,variant)
    for c in p:
        trigger=c.get('trigger',{})
        if 'source_min_y'in trigger or 'source_right_of'in trigger:trigger['state']='free'
    case['source_departure_observation']=dict(kind='elbow_full_body_walkoff'if'cavity_elbow'in source['id']else'outside_descending_cast',physicsChanged=False,triggerDispatchFixed=True)
    return p

def purpose(case,raw):
    result=forest.purpose(case,raw)
    guard=case.get('source_departure_observation',{}).get('kind');casts=[f for f in raw.get('frames',[])if any(r.get('type')=='grapple'for r in f.get('requested',[]))]
    if guard=='elbow_full_body_walkoff' and len(casts)>=2:
        bay=next(p['rect']for p in case['source_behavior']['platforms']if p['id']=='cavity_bay')if'platforms'in case['source_behavior']else None
        # source_behavior intentionally excludes platform geometry; source rect
        # is bound separately by the source entry below during preparation.
        limit=case.get('source_departure_body_edge')
        if limit is None or casts[1]['grounded']or casts[1]['x']<limit-.1:result['reasons'].append('original_elbow_full_body_departure_not_observed')
    elif guard=='outside_descending_cast' and casts:
        target=case['hooks'][0];limit=target['y']+20
        if casts[0]['grounded']or casts[0]['y']<limit-.1:result['reasons'].append('original_descending_cast_not_observed')
    result['ok']=not result['reasons'];return result

def prepare_one(entry,source,variant,out):
    out=Path(out);base=core.REPO/entry['prepared'];meta=core.read(base/'migration.json');original=core.REPO/meta['sourcePath']
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0]
    original_doc=core.read(original/'module.mapnote.json');original_cases=core.read(original/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,restoration=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases)
    value=game_world_v4.native_fields(cases[0],source)
    if value['decoder_pending_behavior']:raise ValueError('unbound_native_behavior:'+str(value['decoder_pending_behavior']))
    value.pop('recorded_frames',None);prefix=program(source,value,variant)
    if 'cavity_elbow'in source['id']:
        bay=next(p['rect']for p in source['data']['platforms']if p['id']=='cavity_bay');value['source_departure_body_edge']=bay[0]+bay[2]+12
    exit_id=value['route_spec']['to_port'];port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id)
    tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-forest-departure-v11-{variant}',control_plan=prefix+tail,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],max_frames=3000)
    value['generation_rule']['registration_source']='pcg/migration/forest_departure_v11.py'
    value['original_feedback_routines']=dict(source='Pinned original H/R rhythm and explicit source approach/departure/routes',variant=variant,sourcePosesAssigned=False)
    entry_id=value['route_spec']['from_port'];value['migration_boundary_plans']={entry_id:dict(ingress=copy.deepcopy(value['migration_boundary_continuations'][entry_id]['ingress']))}
    intermediate=out.with_name(out.name+'-core');shutil.copytree(base,intermediate)
    core.write(intermediate/'module.mapnote.json',doc);core.write(intermediate/'cases.json',dict(cases=[value]))
    game_world_v4.prepare_one(intermediate,source,out,value)
    # Native field binding preserves exact original H/R. The directional source
    # encodes the same sequence through its pinned named input driver instead.
    candidate=core.read(out/'cases.json')['cases'][0]
    candidate['source_action_program']=value['source_action_program'];candidate['generation_rule']['registration_source']='pcg/migration/forest_departure_v11.py'
    doc=core.read(out/'module.mapnote.json');doc,cases,bindings=boundary_runtime.bind(doc,[candidate]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    for key in('replay-cases.json','physics-input-cases.json','physics.json','package.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',restoration);core.write(out/'boundary-bindings.json',bindings)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]

def discover(out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={s['id']:s for s in game_adapter.source_entries()};cases=[];rows=[];labels={}
    ids={'forest_exploration_modules__backbranch_turn','forest_bible_backbranch_geometry__default','forest_hollow_trunk_geometry__cavity_elbow'}
    entries=[r for r in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']if r['referenceId']in ids]
    core.write(out/'protocol.json',dict(schema='pcg/original-departure-observer-repair/v11',maximumSources=3,maximumAttempts=6,repair='Custom observer predicates now have state=free so original DSL dispatch invokes condition_met; raw must show real airborne/body departure before cast.',revision=1,maximumRevisions=2,selection='First original policy passing exact purpose before any holdout',geometryChanged=False,oldFailuresPreserved=True))
    for entry in entries:
        source=sources[entry['referenceId']]
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(id=source['id'],moduleId=entry['stableId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,source,variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as e:row.update(status='behavior_binding_gap',conflict=str(e))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0))
    if not cases:return
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-departure-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,reason=raw.get('reason'),actualHookContacts=raw.get('original_hook_contacts',[]))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],check=check,reason=row['reason'])),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.out,a.name)
