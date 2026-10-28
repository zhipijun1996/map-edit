"""Reuse original authored driver policies for remaining resource modules."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,game_adapter,game_world_v4,core_preserving,foundry_feedback_v5 as feedback
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=feedback.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*feedback.SOURCE_DEPENDENCIES]
SUPPORTED={'plains_recoil_step','plains_recoil_double','plains_recoil_span','plains_low_arch','plains_thorn_cells','plains_thorn_wall','plains_twin_gears','plains_ferry_channel'}


def purpose(case,raw):return game_world_v4.purpose(case,raw)


def prepare_one(entry,source,out):
    prepared=core.REPO/entry['prepared'];original=core.REPO/entry['sourcePackage'];out=Path(out)
    doc=core.read(prepared/'module.mapnote.json');case=core.read(prepared/'cases.json')['cases'][0]
    original_doc=core.read(original/'module.mapnote.json');original_cases=core.read(original/'cases.json')['cases'];original_cases[0]['id']=case['id']
    doc,cases,receipt=core_preserving.restore_core_shores(doc,[case],original_doc,original_cases)
    value=game_world_v4.native_fields(cases[0],source)
    plan=feedback.component_plan(source,[0,0],0,0)
    # A standalone resource retains its exact original IDs (composites namespace).
    for command in plan:
        dynamic=command.get('trigger',{}).get('dynamic',{})
        if dynamic.get('id','').startswith('part0/'):dynamic['id']=dynamic['id'].removeprefix('part0/')
        if command.get('source_carrier_id','').startswith('part0/'):command['source_carrier_id']=command['source_carrier_id'].removeprefix('part0/')
    exit_id=value['route_spec']['to_port'];port=next(p for p in doc['generationContract']['ports']if p['id']==exit_id)
    tail=copy.deepcopy(value['migration_boundary_continuations'][exit_id]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(control_plan=plan+tail,max_frames=max(1600,50*len(plan)),goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:])
    value['id']+='-original-feedback-v6';value['generation_rule']['registration_source']='pcg/migration/resource_feedback_v6.py'
    value['original_feedback_routines']=dict(version=6,variant=0,source='Pinned original BranchModuleDriver routines',usesRecordedPoseAssignment=False)
    for key in('axes','actions','recorded_frames','module_sha256'):value.pop(key,None)
    doc['generationContract']['generation']['parameters'].update(controlPlan=value['control_plan'],sourceFeedbackRoutines=value['original_feedback_routines'])
    annotate(doc);shutil.copytree(prepared,out)
    for name in('replay-cases.json','physics-input-cases.json'):
        if(out/name).exists():(out/name).unlink()
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=[value]));core.write(out/'core-restoration.json',receipt)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',internalGeometryChanged=True);meta['adaptation']['coreRestoration']=receipt;core.write(out/'migration.json',meta)
    core.contract(out/'module.mapnote.json',refresh=True)
    return value


def stage(prepared,out,name):
    prepared=Path(prepared);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    sources={r['id']:r for r in game_adapter.source_entries()};rows=[];cases=[];labels={}
    core.write(out/'protocol.json',dict(schema='pcg/original-resource-feedback-campaign/v6',maximumSources=72,maximumCleanAttempts=72,variants=1,selection='Original authored action driver; no policy search or holdout selection',humanReview='UNKNOWN'))
    for entry in core.read(prepared/'manifest.json')['rows']:
        source=sources[entry['id']];identifier=Path(entry['prepared']).name
        if source['kind']!='resource'or(core.REPO/'modules'/identifier).exists():continue
        if not(core.REPO/entry['sourcePackage']).exists():continue
        if source['id']not in SUPPORTED and not source['data'].get('main_route'):continue
        row=dict(id=source['id'],moduleId=identifier,prepared=core.relative(out/identifier),status='prepared_unverified')
        try:
            case=prepare_one(entry,source,out/identifier);cases.append(case);labels[case['id']]=row
        except Exception as error:row.update(status='needs_repair',conflict=str(error))
        rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows,totalSources=len(rows)))
    from . import physics
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=18,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-resource-feedback-clean'):
        row=labels[case['id']];checked=purpose(case,raw);row.update(clean=checked,status='clean_only'if checked['ok']else'needs_repair',actualGoal=raw.get('ok'),reason=raw.get('reason'),evidence=evidence)
        core.write(out/'manifest.json',dict(rows=rows,totalSources=len(rows),actualCleanAttempts=engine.sim.cases))
        print(json.dumps(row),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();stage(a.prepared,a.out,a.name)
