"""Actual original resource input routines, expressed in the existing action DSL.

No physics model or map generation. Source fixtures and original action methods
are pinned in source-resource-v9; all geometry is restored before local docks.
"""
from __future__ import annotations
import argparse,copy,json,math,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,core_preserving,boundary_runtime,godot_package,foundry_feedback_v5 as feedback
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=feedback.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*feedback.SOURCE_DEPENDENCIES,core.STATE/'original-resource-driver-v9.json',core.STATE/'original-resource-extra-driver-v9.json',
 *list((core.REPO/'pcg/migration/source-resource-v9').glob('*.gd'))]
FIXTURE_IDS={'challenge_long_gap':(1,2),'plains_recoil_chasm':(2,2),'plains_recoil_chasm_wide':(2,2)}


def purpose(case,raw):
    result=game_world_v4.purpose(case,raw)
    expected=case.get('original_action_contract',{})
    if raw.get('shots',0)<expected.get('minimumShots',0):result['reasons'].append('original_required_native_shots_not_executed')
    if raw.get('jumps',0)<expected.get('minimumJumps',0):result['reasons'].append('original_required_native_jumps_not_executed')
    result['ok']=not result['reasons'];return result


def wait_phase(kind,identity,window,timeout=900):return dict(op='wait',trigger=dict(dynamic=dict(kind=kind,id=identity,window=window),timeout=timeout))

def program(source,case,variant):
    raw=source['data'];name=source['id'];gain=5.5 if variant==0 else 8.;entry=raw['entry_port']['position'];exit=raw['exit_port']['position']
    def move(x,y=None):return feedback.move([x,feedback._floor_y(raw,x,entry[1])if y is None else y],gain)
    def jump(x,y):return feedback.jump_to([x,y],gain)
    def shoot(after=0,second=False):
        latch=case['latches'][0];query=dict(kind='bell',id=latch['id'])
        if second:query['receiver']='second'
        return feedback.cmd('shoot',after,aim_cell=query)
    plan=[];shots=0;jumps=0
    if name=='challenge_recoil_climb':
        for takeoff,target in((175,400),(435,640),(715,940)):
            y=feedback._floor_y(raw,target)
            plan+=move(takeoff)+[feedback.cmd('axis',value=1),feedback.cmd('jump'),feedback.cmd('shoot',18,direction=[0,1]),feedback.cmd('jump_release',10),feedback.cmd('settle',target_x=target,source_native_gain=gain,deadband=.6),feedback.wait_at([target,y])]
        shots=3;jumps=3
    elif name in('challenge_long_gap','plains_recoil_chasm','plains_recoil_chasm_wide'):
        plan+=move(240)+[feedback.cmd('axis',value=1),feedback.cmd('jump'),feedback.cmd('shoot',18,direction=[-1,0]),feedback.cmd('shoot',17,direction=[-1,0]),feedback.cmd('jump_release',10)]
        if name!='challenge_long_gap':plan.append(feedback.cmd('jump'));jumps=2
        else:jumps=1
        target=820 if name=='challenge_long_gap'else 990 if name.endswith('_wide')else 930
        plan +=[feedback.cmd('settle',target_x=target,source_native_gain=gain,deadband=.6),feedback.wait_at([target,exit[1]]),feedback.cmd('jump_release')];shots=2
    elif name=='recoil_shaft':
        plan+=move(590)+[feedback.cmd('axis',value=1),feedback.cmd('jump'),feedback.cmd('shoot',18,direction=[0,1]),feedback.cmd('jump_release',1),feedback.cmd('settle',target_x=exit[0],source_native_gain=gain,deadband=.6),feedback.wait_at(exit)];shots=1;jumps=1
    elif name=='descending_switchback':
        plan+=move(760,372)+move(380,502)+move(exit[0],exit[1])
    elif name=='spike_gap':
        plan+=move(165)+jump(380,entry[1])+move(395)+jump(560,entry[1]);jumps=2
    elif name in('plains_gear_brook','plains_gear_glade'):
        x=raw['saws'][0]['origin'][0];plan+=move(x-90)+jump(x+90,entry[1]);jumps=1
    elif name in('plains_switchback','plains_wind_spire'):
        plan=feedback.component_plan(source,[0,0],0,variant);jumps=sum(c['op']=='jump'for c in plan)
    elif name=='plains_thorn_slalom':
        plan+=move(145)
        for index,x in enumerate((350,520,540,735),1):plan+=(move(x)if index==3 else jump(x,282))
        jumps=3
    elif name=='macro_chain':
        for a,b in((185,385),(465,655),(735,890)):plan+=move(a)+jump(b,feedback._floor_y(raw,b))
        vertical,horizontal=raw['saws'];limit=(410-vertical['origin'][1])/vertical['travel'][1]
        plan +=[wait_phase('saw_phase',vertical['source_id'],[.5-math.asin(min(.99,limit))/(2*math.pi)+.01,.74])]
        plan+=move(1045)+jump(1180,feedback._floor_y(raw,1180))
        plan +=[wait_phase('saw_phase',horizontal['source_id'],[.01,.24])]
        plan+=move(1220)+jump(1410,feedback._floor_y(raw,1410));jumps=5
    elif name in('challenge_ferry_ascent','plains_ferry_one','plains_ferry_two','plains_ferry_gears','plains_windchime_ferry','moving_transfer','plains_bell_ferry_control'):
        horizontal=name in('moving_transfer','plains_bell_ferry_control')
        if name=='plains_bell_ferry_control':plan+=move(130)+[shoot(),feedback.cmd('wait',32)];shots+=1
        for i,ferry in enumerate(case['moving_platforms']):
            identity=ferry['platform_id'];period=2*(ferry['travel_duration']+ferry['dwell_duration'])
            station=[280,entry[1]]if name=='moving_transfer'else[130,282]if name=='plains_bell_ferry_control'else[[150,932],[710,682],[360,380]][i]
            plan+=move(*station)+[wait_phase('platform_phase',identity,[0,min(.1,ferry['dwell_duration']/period-.005)]),feedback.cmd('settle',target_x=ferry['start'][0],source_native_gain=gain,source_carrier_id=identity,deadband=.6),feedback.cmd('jump'),dict(op='wait',trigger=dict(after=6,state='grounded',dynamic=dict(kind='on_platform',id=identity),timeout=180)),feedback.cmd('jump_release'),feedback.cmd('axis',value=0),wait_phase('platform_phase',identity,[.5,.5+min(.1,ferry['dwell_duration']/period-.005)]),feedback.cmd('wait',3)];jumps+=1
            if name=='plains_windchime_ferry':plan +=[shoot(),feedback.cmd('wait',15)];shots+=1
            if name=='moving_transfer':plan+=move(exit[0],exit[1])
            else:
                receiver=[640,282]if horizontal else[[680,682],[390,380],[840,78]][i]
                plan+=jump(*receiver);jumps+=1
    elif name in('plains_remote_bell','plains_remote_sequence','plains_windchime_lesson','plains_windchime_sequence','plains_windchime_timed','plains_windchime_rush','plains_windchime_well'):
        if name=='plains_windchime_well':
            plan+=move(265)+[feedback.cmd('axis',value=1),feedback.cmd('jump'),shoot(14),feedback.cmd('wait',10),feedback.cmd('jump_release'),feedback.cmd('settle',target_x=430,source_native_gain=gain,deadband=.6),feedback.wait_at([430,feedback._floor_y(raw,430)])];shots=1;jumps=1
        elif name=='plains_remote_sequence':
            plan+=move(100)+[shoot(),feedback.cmd('wait',30)]+move(420)+jump(520,192)+[shoot(second=True),feedback.cmd('wait',30),feedback.cmd('drop_through'),feedback.cmd('wait',50)];shots=2;jumps=1
        elif name=='plains_remote_bell':plan+=move(130)+[shoot(),feedback.cmd('wait',32)];shots=1
        else:
            plan+=move(140)+[shoot(),feedback.cmd('wait',30)];shots=1
            if name=='plains_windchime_sequence':plan+=move(210)+[shoot(second=True),feedback.cmd('wait',30)];shots=2
            if name=='plains_windchime_rush':plan+=move(255)+jump(435,282);jumps=1
    else:raise ValueError('original_resource_driver_not_mapped:'+name)
    plan+=move(exit[0],exit[1])
    return plan,dict(minimumShots=shots,minimumJumps=jumps,sourceRoutines='Pinned actual original input methods; sourcegeometryunchanged',variant=variant,gain=gain)


def prepare_one(entry,source,variant,out):
    source_folder=core.REPO/entry['sourceKey'];base=core.REPO/entry['prepared'];out=Path(out)
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0];original_doc=core.read(source_folder/'module.mapnote.json');original_cases=core.read(source_folder/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,receipt=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases);value=game_world_v4.native_fields(cases[0],source)
    if source['id']in FIXTURE_IDS:raise ValueError('awaiting_exact_original_fixture_nativev5:'+str(FIXTURE_IDS[source['id']]))
    plan,contract=program(source,value,variant);port=next(p for p in doc['generationContract']['ports']if p['id']==value['route_spec']['to_port'])
    tail=copy.deepcopy(value['migration_boundary_continuations'][port['id']]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-original-source-v9-{variant}',control_plan=plan+tail,max_frames=3420,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],original_action_contract=contract)
    value['generation_rule']['registration_source']='pcg/migration/resource_original_v9.py'
    value['migration_boundary_plans']={value['route_spec']['from_port']:dict(ingress=value['migration_boundary_continuations'][value['route_spec']['from_port']]['ingress'])}
    for key in('module_sha256','recorded_frames','axes','actions'):value.pop(key,None)
    doc['generationContract']['generation']['parameters'].update(controlPlan=value['control_plan'],originalActionContract=contract)
    doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=godot_package.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=cases[0]['capabilities'][:]
    annotate(doc);shutil.copytree(base,out)
    for file in('replay-cases.json','physics-input-cases.json'):(out/file).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',receipt);core.write(out/'boundary-bindings.json',bindings)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',internalGeometryChanged=True);meta['adaptation']['originalInputRoutines']=contract;core.write(out/'migration.json',meta)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(out,name):
    out=Path(out);out.mkdir(exist_ok=False,parents=True);entries=[r for r in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']if r['sourceKind']=='resource'];sources={r['id']:r for r in game_adapter.source_entries()};rows=[];cases=[];labels={}
    core.write(out/'protocol.json',dict(schema='pcg/original-resource-inputs/v9',maximumSources=27,maximumVariants=2,maximumAttempts=54,variants=[dict(originalNativeGain=5.5),dict(originalNativeGain=8)],selection='First actualnativeintent+goal success, before anyheldout; no sourcegeometry orqualitythresholdchanges'))
    for entry in entries:
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(sourceKey=entry['sourceKey'],moduleId=entry['stableId'],referenceId=entry['referenceId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,sources[entry['referenceId']],variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as error:row.update(status='binding_gap',conflict=str(error))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows))
    # Actualrunner is per-author boundary wrapper; rawcleans do not need that
    # fixture override, inherited nativeinputphysics andpurpose are identical.
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'original-resource-methods-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,actualGoal=raw.get('ok'),reason=raw.get('reason'),evidence=evidence,status='clean_only'if check['ok']else'current_program_failed')
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(row),flush=True)
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.out,a.name)
