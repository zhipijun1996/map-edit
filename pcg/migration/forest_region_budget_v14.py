"""Correct a zero-step rejected measurement budget; preserve source policies."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,boundary_runtime,forest_region_v12 as original,godot_package_v5 as native
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*original.SOURCE_DEPENDENCIES]
purpose=original.purpose


def prepare(source_folder,out):
    source_folder=Path(source_folder);out=Path(out);out.mkdir(parents=True,exist_ok=False);before=core.read(source_folder/'manifest.json');rows=[];cases=[]
    for prior in before['rows']:
        if prior.get('reason')!='rejected_frame_budget':raise ValueError('budget_repair_only_zero_step_rejected_sources')
        base=core.REPO/prior['prepared'];folder=out/base.name;shutil.copytree(base,folder)
        doc=core.read(folder/'module.mapnote.json');values=core.read(folder/'cases.json')['cases']
        for case in values:
            if case['max_frames']!=6000:raise ValueError('unexpected_original_budget')
            case['max_frames']=3600;case['id']+='-bounded-v14';case['generation_rule']['registration_source']='pcg/migration/forest_region_budget_v14.py';case.pop('module_sha256',None)
        doc['generationContract']['generation']['parameters']['physicalMeasurementBudget']=dict(maxFrames=3600,harnessHardLimit=3600,correctedRejected6000=True,zeroStepPrevious=True)
        doc,values,bindings=boundary_runtime.bind(doc,values);doc=native.bind_case_behavior(doc,values)
        core.write(folder/'module.mapnote.json',doc);core.write(folder/'cases.json',dict(cases=values));core.write(folder/'boundary-bindings.json',bindings);core.contract(folder/'module.mapnote.json',refresh=True);native.audit_cases(core.read(folder/'module.mapnote.json'),values,require_replay=False)
        meta=core.read(folder/'migration.json');meta.update(status='prepared_unverified',measurementBudgetRepair=dict(previous=6000,current=3600,previousSteppedFrames=0,gameplayChanged=False));core.write(folder/'migration.json',meta)
        row={k:copy.deepcopy(prior[k])for k in('id','moduleId','variant')};row.update(prepared=core.relative(folder),status='prepared_unverified');rows.append(row);cases+=values
    protocol=dict(schema='pcg/original-region-measurement-budget-repair/v14',maximumSources=9,maximumAttempts=18,variants=['Unchanged v12 full-held source itinerary','Unchanged v12 release16 source itinerary'],previousRejectedRequests=18,previousSteppedFrames=0,maxFrames=3600,geometryChanged=False,sourcePoliciesChanged=False,selection='First unchanged source policy passing actual purpose before calibration and holdout')
    core.write(out/'protocol.json',protocol);core.write(core.STATE/'original-forest-region-v14-protocol-v1.json',protocol);core.write(out/'manifest.json',dict(rows=rows,actualAttempts=0,previousZeroStepRejectedRequests=18));return rows,cases


def run(source_folder,out,name):
    out=Path(out);rows,cases=prepare(source_folder,out);labels={c['id']:r for c,r in zip(cases,rows)}
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=12,extra_sources=[*SOURCE_DEPENDENCIES,core.STATE/'original-forest-region-v14-protocol-v1.json'],runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'source-region-bounded-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,status='clean_only'if check['ok']else'actual_clean_failure',evidence=evidence,reason=raw.get('reason'),originalRegion=raw.get('original_region_chests'))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,previousZeroStepRejectedRequests=18));print(json.dumps(dict(id=row['id'],variant=row['variant'],status=row['status'],reason=row['reason'],check=check)),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();run(a.source,a.out,a.name)
