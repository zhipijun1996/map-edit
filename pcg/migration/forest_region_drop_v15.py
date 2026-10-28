"""Bind original periodic Down to remaining source-authored reward returns."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,boundary_runtime,forest_region_v12 as original,godot_package_v5 as native
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_region_drop_runner_v15.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*original.SOURCE_DEPENDENCIES,core.STATE/'original-forest-drop-driver-v13.json',core.REPO/'pcg/migration/source-forest-v13/forest_depth_region_trace.gd']
purpose=original.purpose


def prepare(source_folder,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);before=core.read(Path(source_folder)/'manifest.json');rows=[];cases=[]
    for prior in before['rows']:
        if prior['status']!='actual_clean_failure':continue
        base=core.REPO/prior['prepared'];folder=out/base.name;shutil.copytree(base,folder);doc=core.read(folder/'module.mapnote.json');values=core.read(folder/'cases.json')['cases']
        for case in values:
            case['max_frames']=3420;case['id']+='-source-drop-v15';case['generation_rule']['registration_source']='pcg/migration/forest_region_drop_v15.py';case.pop('module_sha256',None)
            itinerary=case['source_ordinary_reward_itinerary'];steps=itinerary['before']+itinerary['after'];drops=[s for s in steps if s['kind']=='drop_through']
            for c in case['control_plan']:
                trigger=c.get('trigger',{});goal=trigger.get('migration_goal')
                if not goal:continue
                step=next((s for s in drops if abs(goal[0]+goal[2]/2-s['landing'][0])<.1 and abs(goal[1]+goal[3]/2-s['landing'][1])<.1),None)
                if step:
                    path=step.get('path',[step['takeoff'],step['landing']]);trigger.update(source_drop_until_y=step['landing'][1],source_drop_mouth_x=(path[1]if len(path)>2 else path[0])[0])
            case['original_drop_driver']=dict(source='Pinned original forest_depth_region_trace.drive_drop',minimumIntervalFrames=20,requiresRealGroundSupport=True,requiresActualMouth=True,geometryChanged=False,resourcesReset=False)
        doc['generationContract']['generation']['parameters']['physicalMeasurementBudget']=dict(maxFrames=3420,continuousExitReserve=180,harnessHardLimit=3600)
        doc['generationContract']['generation']['parameters']['originalDropDriver']=values[0]['original_drop_driver']
        doc,values,bindings=boundary_runtime.bind(doc,values);doc=native.bind_case_behavior(doc,values);core.write(folder/'module.mapnote.json',doc);core.write(folder/'cases.json',dict(cases=values));core.write(folder/'boundary-bindings.json',bindings);core.contract(folder/'module.mapnote.json',refresh=True);native.audit_cases(core.read(folder/'module.mapnote.json'),values,require_replay=False)
        for name in('replay-cases.json','physics-input-cases.json'):(folder/name).unlink(missing_ok=True)
        meta=core.read(folder/'migration.json');meta.update(status='prepared_unverified',originalDropBinding=values[0]['original_drop_driver']);core.write(folder/'migration.json',meta)
        row={k:copy.deepcopy(prior[k])for k in('id','moduleId','variant')};row.update(prepared=core.relative(folder),status='prepared_unverified');rows.append(row);cases+=values
    protocol=dict(schema='pcg/original-region-drop-input-binding/v15',maximumSources=7,maximumAttempts=14,revision=1,maximumRevisions=2,maximumCanonicalFrames=3420,maximumContinuousExitFrames=3600,geometryChanged=False,selection='First fixed original input variant passing full source purpose before calibration/holdout',sourceItineraryUnchanged=True,repair='Original Down through OWP at actual horizontal mouth and every20frames until authored lower receiver')
    core.write(out/'protocol.json',protocol);core.write(core.STATE/'original-forest-region-v15-protocol-v1.json',protocol);core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0));return rows,cases


def run(source_folder,out,name):
    out=Path(out);rows,cases=prepare(source_folder,out);labels={c['id']:r for c,r in zip(cases,rows)};engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=[*SOURCE_DEPENDENCIES,core.STATE/'original-forest-region-v15-protocol-v1.json'],runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-region-original-drop-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,reason=raw.get('reason'),originalRegion=raw.get('original_region_chests'))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],reason=row['reason'],check=check)),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();run(a.source,a.out,a.name)
