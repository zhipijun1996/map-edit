"""Preserve the original well's jump or walk-off same-shot recoil alternatives.

The pinned ShotLatchModuleDriver has an explicit combo=False path. Jumping is
demonstrated by the nominal combo program, not a requirement on every solution.
"""
from __future__ import annotations
import copy,shutil
from pathlib import Path
from . import core,physics,boundary_runtime,godot_package,resource_original_v9 as original
RUNNER_SCRIPT=original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*original.SOURCE_DEPENDENCIES]


def purpose(case,raw):
    result=original.purpose(case,raw)
    shots=[c for c in raw.get('fired_commands',[])if c.get('op')=='shoot']
    events=raw.get('plains',{}).get('events',[])
    witnessed=[]
    for shot in shots:
        frame=shot.get('frame',-100);position=shot.get('position',[])
        if len(position)!=2 or shot.get('direction',[0,0])[1]<=0:continue
        opened=any(e.get('type')=='bell_open'and frame<=e.get('frame',-1)<=frame+10 for e in events)
        # fired_commands is before that frame's native physics tick; captured
        # frame+9 is the tenth actual tick, matching the pinned await tick(10).
        tenth=next((f for f in raw.get('frames',[])if f.get('frame')==frame+9),None)
        ascent=position[1]-tenth['y']if tenth else 0
        if opened and ascent>100:witnessed.append(dict(frame=frame,ascentWithin10Frames=ascent))
    if not witnessed:result['reasons'].append('original_well_same_shot_gate_and_upward_recoil_missing')
    result['ok']=not result['reasons'];result['originalWellRecoilWitness']=witnessed
    return result


def prepare(source_folder,out):
    source_folder=Path(source_folder);out=Path(out)
    doc=core.read(source_folder/'module.mapnote.json');cases=core.read(source_folder/'cases.json')['cases']
    assert len(cases)==1 and cases[0]['family']=='original-game-plains_windchime_well'
    value=copy.deepcopy(cases[0]);value['id']+='-legal-alternative-v11'
    value['generation_rule']['registration_source']='pcg/migration/resource_well_v11.py'
    contract=value['original_action_contract'];contract['minimumJumps']=0
    contract['demonstratedNominalJumps']=1;contract['sameShotUpwardAscentWithin10FramesGreaterThan']=100
    source=core.REPO/'pcg/migration/source-resource-v9/shot_latch_module_driver.gd'
    contract['legalAlternativesSource']=dict(path=core.relative(source),sha256=core.sha(source),lines='52-80',sameShotAssertion='await tick.call(10); motor.global_position.y < height - 100',noJumpAlternative='combo=false')
    for key in('module_sha256','recorded_frames'):value.pop(key,None)
    doc['generationContract']['generation']['parameters']['originalActionContract']=copy.deepcopy(contract)
    doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=godot_package.bind_case_behavior(doc,cases)
    shutil.copytree(source_folder,out)
    for name in('physics-input-cases.json','replay-cases.json'):(out/name).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'boundary-bindings.json',bindings)
    meta=core.read(out/'migration.json');meta['status']='prepared_unverified';meta['adaptation']['wellPurposeCorrection']=dict(previousMinimumJumps=1,correctedMinimumJumps=0,reason='Original source explicitly allows the non-combo alternative. The observed zero-jump path walks off before shooting in air; same-shot bell opening and >100px recoil retained.')
    core.write(out/'migration.json',meta);core.contract(out/'module.mapnote.json',refresh=True)
    godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();prepare(args.source,args.out)
