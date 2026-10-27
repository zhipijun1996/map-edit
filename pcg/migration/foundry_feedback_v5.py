"""Translate original Foundry driver routines into the existing action DSL.

Driver source: tests/branch_module_driver.gd, plains_exploration_motion.gd and
plains_interactive_motion.gd. These are input policies, not another simulator.
Only the native Godot Harness decides geometry, resources and actual success.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import shutil
from pathlib import Path
from . import core,game_adapter,game_world_v4,foundry_replay_v4,core_preserving
from .corners import annotate
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate

RUNNER_SCRIPT=core.REPO/'pcg/migration/foundry_feedback_runner_v5.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*game_world_v4.SOURCE_DEPENDENCIES,
    core.STATE/'original-foundry-driver-v5.json',
    *[core.REPO/'pcg/migration/source-driver-v5'/name for name in ('branch_module_driver.gd','plains_exploration_motion.gd','plains_interactive_motion.gd')]]
REPRESENTATIVES=['height_then_precision','read_ride_release','short_long_rise',
                 'climb_change_height','resource_then_rhythm','precision_to_transfer']


def purpose(case,raw):return game_world_v4.purpose(case,raw)


def cmd(op,after=0,**kwargs):return dict(op=op,trigger=dict(after=after),**kwargs)


def wait_at(point,tolerance=5,timeout=480,after=0):
    return dict(op='wait',trigger=dict(after=after,state='grounded',migration_goal=[point[0]-tolerance,point[1]-4,tolerance*2,8],timeout=timeout))


def move(point, gain=5.5):
    return [cmd('settle',target_x=point[0],deadband=.6,source_native_gain=gain),wait_at(point)]


def jump_to(point,gain=5.5,release=None):
    plan=[cmd('settle',target_x=point[0],deadband=.6,source_native_gain=gain),cmd('jump')]
    if release is not None:plan.append(cmd('jump_release',release))
    plan += [wait_at(point,after=6),cmd('jump_release')]
    return plan


def _floor_y(raw,x,near=None):
    ys=[r[1]-18 for r in raw['platforms']if r[0]-1e-5<=x<=r[0]+r[2]+1e-5]
    if not ys:raise ValueError('original_driver_target_has_no_static_floor:'+str(x))
    return min(ys,key=lambda y:abs(y-near))if near is not None else min(ys)


def _floor_contains(raw,a,b):
    if abs(a[1]-b[1])>.1:return False
    covered=min(a[0],b[0]);end=max(a[0],b[0])
    for floor in sorted(raw['platforms']):
        if abs(floor[1]-a[1]-18)<.1 and floor[0]<=covered<floor[0]+floor[2]:covered=floor[0]+floor[2]
    return covered>=end


def component_plan(row,offset,part,variant):
    raw=row['data'];identifier=row['id'];dx,dy=offset;gain=5.5 if variant==0 else 8.0
    at=lambda x,y:[x+dx,y+dy]
    entry=raw['entry_port']['position'];exit=raw['exit_port']['position'];plan=[]
    if identifier in ('plains_recoil_step','plains_recoil_double'):
        pairs=[(170,400)]+([(430,640)]if identifier=='plains_recoil_double'else[])
        for takeoff,receiver in pairs:
            before=_floor_y(raw,takeoff,entry[1]);after=_floor_y(raw,receiver)
            plan+=move(at(takeoff,before),gain)
            plan += [cmd('settle',target_x=dx+receiver,deadband=.6,source_native_gain=gain),cmd('jump'),
                cmd('shoot',18,direction=[0,1]),cmd('jump_release',9),wait_at(at(receiver,after),after=6)]
    elif identifier=='plains_recoil_span':
        plan+=move(at(275,entry[1]),gain)
        plan += [cmd('settle',target_x=dx+700,deadband=.6,source_native_gain=gain),cmd('jump'),
                 cmd('shoot',18,direction=[-2**-.5,2**-.5]),wait_at(at(700,exit[1]),after=6),cmd('jump_release')]
    elif identifier=='plains_low_arch':
        plan+=move(at(275,entry[1]),gain)
        plan += [cmd('axis',value=1),cmd('jump'),cmd('jump_release',7 if variant==0 else 5),
                 dict(op='wait',trigger=dict(after=2,state='grounded',timeout=240)),cmd('jump_release')]
    elif identifier=='plains_thorn_cells':
        plan+=move(at(170,282),gain)+jump_to(at(420,282),gain)
    elif identifier=='plains_thorn_wall':
        plan+=move(at(225,282),gain)+jump_to(at(352,152),gain)+jump_to(at(490,282),gain)
    elif identifier=='plains_twin_gears':
        for i,x in enumerate((220,510)):
            saw=raw['saws'][i];travel=saw['travel'][0]
            if not travel:raise ValueError('original_twin_gear_has_no_horizontal_phase')
            phase_low=math.asin(min(.99,25/abs(travel)))/(2*math.pi)
            window=[phase_low+.01,.24]if travel>0 else [.5+phase_low+.01,.74]
            plan+=move(at(x-90,282),gain)
            plan.append(dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=f'part{part}/'+saw['source_id'],window=window),timeout=360)))
            plan+=jump_to(at(x+90,282),gain)
    elif identifier=='plains_ferry_channel':
        ferry=raw['ferries'][0];identity=f'part{part}/'+ferry['platform_id'];period=2*(ferry['travel_duration']+ferry['dwell_duration'])
        plan+=move(at(130,282),gain)
        plan.append(dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=identity,window=[0,.25/period]),timeout=900)))
        plan += [cmd('settle',target_x=dx+ferry['start'][0],deadband=.6,source_native_gain=gain,source_carrier_id=identity),cmd('jump'),
            dict(op='wait',trigger=dict(after=6,state='grounded',dynamic=dict(kind='on_platform',id=identity),timeout=180)),cmd('jump_release'),
            dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=identity,window=[.5,.5+.25/period]),timeout=900)),
            cmd('axis',value=0),cmd('wait',6)]
        plan+=jump_to(at(640,282),gain)
    elif raw.get('main_route'):
        anchors=raw['anchors'];path=raw['main_route']
        for a_index,b_index in zip(path,path[1:]):
            a,b=anchors[a_index],anchors[b_index]
            if _floor_contains(raw,a,b):plan+=move(at(*b),gain);continue
            direction=1 if b[0]>a[0]else -1;takeoff=a[0]
            for floor in raw['platforms']:
                if abs(floor[1]-a[1]-18)<.1 and floor[0]<=a[0]<floor[0]+floor[2]:
                    takeoff=floor[0]+floor[2]-40 if direction>0 else floor[0]+40
                    if floor[2]>400:takeoff=a[0]+direction*20
                    break
            plan+=move(at(takeoff,a[1]),gain)+jump_to(at(*b),gain)
    else:raise ValueError('original_driver_routine_not_translated:'+identifier)
    plan+=move(at(*exit),gain)
    return plan


def prepare_one(prepared,source,variant,out):
    prepared=Path(prepared).resolve();out=Path(out).resolve()
    original=core.REPO/'pcg/migration/game-sources'/prepared.name
    if not original.exists():raise ValueError('foundry_original_source_already_archived')
    doc=core.read(prepared/'module.mapnote.json');case=core.read(prepared/'cases.json')['cases'][0]
    source_doc=core.read(original/'module.mapnote.json');source_cases=core.read(original/'cases.json')['cases']
    source_cases[0]['id']=case['id']
    doc,cases,receipt=core_preserving.restore_core_shores(doc,[case],source_doc,source_cases)
    value=game_world_v4.native_fields(cases[0],source)
    resources={r['id']:r for r in game_adapter.source_entries()if r['kind']=='resource'}
    # Exact authored per-instance hazard names survive atomic flattening.
    cursor=0;scopes=[]
    for part,node in enumerate(source['data']['nodes']):
        count=len(resources[node['module_id']]['data']['platforms'])
        for thorn in value['thorns']:
            if cursor<=thorn['platform_index']<cursor+count:
                before=thorn['surface_id'];thorn['surface_id']=f'part{part}/'+before.removeprefix(f'part{part}/')
                scopes.append(dict(index=thorn['platform_index'],before=before,after=thorn['surface_id']))
        cursor+=count
    objects={o['id']:o for o in doc['objects']}
    for obj in doc['objects']:
        if obj['type']in('spike','wallSpike'):
            ix=objects.get(obj.get('hostId'),{}).get('sourceIndex')
            matches=[s for s in scopes if s['index']==ix and obj.get('sourceId')in(s['before'],s['after'])]
            if len(matches)==1:obj['sourceId']=matches[0]['after']
    plan=[]
    for part,node in enumerate(source['data']['nodes']):plan+=component_plan(resources[node['module_id']],node['offset'],part,variant)
    exit_id=value['route_spec']['to_port'];exit_port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id)
    tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress'])
    # Canonical interior ends on the real inner dock. The continuous-exit
    # fixture separately supplies an exterior neighbor and crosses outside.
    tail[-1]['target_x']=exit_port['stagingPosition'][0]
    value['control_plan']=plan+tail;value['goal']=[exit_port['stagingPosition'][0]-8,exit_port['stagingPosition'][1]-5,16,10]
    value['exit_port']=exit_port['stagingPosition'][:]
    value['max_frames']=min(3600,max(1600,600*len(source['data']['nodes'])))
    value['id']+=f'-original-feedback-v5-{variant}'
    value['generation_rule']['registration_source']='pcg/migration/foundry_feedback_v5.py'
    value['original_feedback_routines']=dict(version=5,variant=variant,source='Original BranchModuleDriver + PlainsExplorationMotion + PlainsInteractiveMotion routines',usesRecordedPoseAssignment=False)
    value.pop('axes',None);value.pop('actions',None);value.pop('recorded_frames',None);value.pop('module_sha256',None)
    doc['generationContract']['generation']['parameters'].update(controlPlan=value['control_plan'],original_tuning_profile=value['original_tuning_profile'],sourceFeedbackRoutines=value['original_feedback_routines'])
    for route in doc['generationContract']['routes']:
        route['requiredAbilities']=value['capabilities'];route['capabilityRequirements']['allOf']=[v for v in value['capabilities']if v!='move']
    annotate(doc)
    if out.exists():raise ValueError('feedback_prepared_destination_exists')
    shutil.copytree(prepared,out)
    for cache in ('physics-input-cases.json','replay-cases.json'):
        if(out/cache).exists():(out/cache).unlink()
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=[value]));core.write(out/'core-restoration.json',receipt)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',internalGeometryChanged=True);meta['adaptation']['coreRestoration']=receipt
    core.write(out/'migration.json',meta);core.contract(out/'module.mapnote.json',refresh=True)
    return out


def calibrate_representatives(prepared,out,name):
    prepared=Path(prepared).resolve();out=Path(out).resolve();out.mkdir(exist_ok=False,parents=True)
    sources={r['id']:r for r in game_adapter.source_entries()};rows=[];cases=[];labels={}
    entries=core.read(prepared/'manifest.json')['rows'];by_id={r['id']:r for r in entries}
    for template in REPRESENTATIVES:
        identifier='foundry__'+template+'-base-v0-p0';entry=by_id[identifier]
        for variant in(0,1):
            target=out/(Path(entry['prepared']).name+f'-policy{variant}')
            prepare_one(core.REPO/entry['prepared'],sources[identifier],variant,target)
            value=core.read(target/'cases.json')['cases'][0];cases.append(value);labels[value['id']]=dict(template=template,variant=variant,prepared=core.relative(target))
    run=core.REPO/'pcg/results'/core.safe_id(name)
    engine=WorkshopEngine(run,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT)
    core.write(run/'protocol.json',dict(schema='pcg/original-foundry-feedback-calibration/v5',representatives=REPRESENTATIVES,variants=[dict(gain=5.5,archHold=7),dict(gain=8.0,archHold=5)],
        maximumAttempts=864,selection='first variant satisfying existing regular calibration gate; no holdout in this calibration experiment',calibrationSeed=2710277401,
        reuse='Original action drivers translated to existing DSL; no new physical model or source geometry redesign'))
    # One clean diagnostic first; no holdout conditions are touched here.
    for case,raw,evidence in engine.run(cases,'source-feedback-clean'):
        checked=purpose(case,raw);row=dict(**labels[case['id']],case=case,clean=checked,evidence=evidence,actualGoal=raw.get('ok'),reason=raw.get('reason'))
        if checked['ok']:
            result=evaluate(engine,[case],2710277401,12,'source-feedback-calibration',purpose_fn=purpose)[0]
            row['calibration']=result['quality_gate'];row['rates']={k:v['rate']for k,v in result['stats'].items()}
        rows.append(row);core.write(run/'calibration-results.json',dict(rows=rows,actualAttempts=engine.sim.cases))
        print(json.dumps({k:v for k,v in row.items()if k not in('case','evidence')}),flush=True)
    return dict(rows=rows,actualAttempts=engine.sim.cases)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args()
    r=calibrate_representatives(a.prepared,a.out,a.name);print('feedback calibration attempts',r['actualAttempts'])
