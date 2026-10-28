"""One explicit open-and-select intent; original modal and grant remain real.

World-time jitter applies to the interaction. A specified selection while the
world is paused is submitted in the same capture, as two original UI inputs.
No movement, menu guard, grant, physics or source quality threshold is changed.
"""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,boundary_runtime,forest_region_drop_v15 as previous,godot_package_v5 as native
RUNNER_SCRIPT=core.REPO/'pcg/migration/forest_region_ui_runner_v16.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*previous.SOURCE_DEPENDENCIES]
purpose=previous.purpose


def bind_ui(case):
    result=copy.deepcopy(case);plan=result['control_plan'];revised=[];i=0;pairs=0
    while i<len(plan):
        command=plan[i]
        if command['op']=='native_region_interact':
            if i+1>=len(plan)or plan[i+1]['op']!='native_region_choose'or plan[i+1].get('kind')not in('coin','note'):raise ValueError('explicit_adjacent_original_UI_choice_required')
            revised.append(dict(op='native_region_select',trigger=copy.deepcopy(command['trigger']),kind=plan[i+1]['kind']));pairs+=1;i+=2
        else:revised.append(copy.deepcopy(command));i+=1
    if pairs!=len(result.get('required_region_chest_choices',[])):raise ValueError('explicit_region_UI_intent_count_mismatch')
    result['control_plan']=revised;result['max_frames']=3420;result['id']+='-modal-intent-v16';result['generation_rule']['registration_source']='pcg/migration/forest_region_ui_v16.py';result.pop('module_sha256',None)
    result['native_region_UI_intent']=dict(policy='Explicit open then specified selection inside paused modal',originalEvents=['native_region_interact','native_region_choose'],movementTimingPerturbed=True,pausedMenuHasNoPhysicsFrames=True,autoRewardGrant=False,selectionGuardByOriginalConsumer=True)
    return result


def prepare(base,out):
    base=Path(base);out=Path(out);shutil.copytree(base,out);doc=core.read(base/'module.mapnote.json');cases=[bind_ui(c)for c in core.read(base/'cases.json')['cases']];doc['generationContract']['generation']['parameters']['nativeRegionUIIntent']=cases[0]['native_region_UI_intent'];doc['generationContract']['generation']['parameters']['physicalMeasurementBudget']=dict(maxFrames=3420,continuousExitReserve=180,harnessHardLimit=3600)
    doc,cases,bindings=boundary_runtime.bind(doc,cases);doc=native.bind_case_behavior(doc,cases)
    for key in('replay-cases.json','physics-input-cases.json'):(out/key).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'boundary-bindings.json',bindings);core.contract(out/'module.mapnote.json',refresh=True);native.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args();prepare(a.source,a.out)
