"""Bounded input-only repair of the original macro's right-moving gear window.

The original x>1280/right-moving observation permits these late subwindows.
Terrain, all five jumps, actor tuning and native hazards are unchanged.
"""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,boundary_runtime,godot_package,resource_original_v9 as original
from pcg.prototype.workshop.engine import WorkshopEngine
RUNNER_SCRIPT=original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*original.SOURCE_DEPENDENCIES]
WINDOWS=[[.15,.20],[.20,.24]]
purpose=original.purpose


def prepare(source_folder,out,variant):
    source_folder=Path(source_folder);out=Path(out)
    doc=core.read(source_folder/'module.mapnote.json');value=core.read(source_folder/'cases.json')['cases'][0]
    assert value['family']=='original-game-macro_chain'
    window=WINDOWS[variant];changed=[]
    for index,command in enumerate(value['control_plan']):
        query=command.get('trigger',{}).get('dynamic',{})
        if query.get('kind')=='saw_phase'and query.get('id')=='chain_horizontal':
            changed.append(dict(commandIndex=index,old=copy.deepcopy(query['window']),new=window));query['window']=copy.deepcopy(window)
    assert len(changed)==1
    value['id']+=f'-late-source-window-v12-{variant}'
    value['generation_rule']['registration_source']='pcg/migration/resource_macro_v12.py'
    value['original_action_contract']['lateRightMovingGearWindow']=dict(variant=variant,window=window,originalRule='x>1280 and right-moving',source='pcg/migration/source-resource-v9/random_stage_tests.gd:484-500',sourceSha256=core.sha(core.REPO/'pcg/migration/source-resource-v9/random_stage_tests.gd'))
    for key in('module_sha256','recorded_frames'):value.pop(key,None)
    parameters=doc['generationContract']['generation']['parameters'];parameters['controlPlan']=copy.deepcopy(value['control_plan']);parameters['originalActionContract']=copy.deepcopy(value['original_action_contract'])
    doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=godot_package.bind_case_behavior(doc,cases)
    shutil.copytree(source_folder,out)
    for name in('physics-input-cases.json','replay-cases.json'):(out/name).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'boundary-bindings.json',bindings)
    meta=core.read(out/'migration.json');meta['status']='prepared_unverified';meta['adaptation']['macroGearWindowRevision']=changed;core.write(out/'migration.json',meta)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(source_folder,out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[];cases=[]
    core.write(out/'protocol.json',dict(schema='pcg/original-macro-phase-repair/v12',maximumAttempts=2,phaseWindows=WINDOWS,selection='First clean success before any calibration or heldout',unchanged='Native physics, five original jumps, terrain and hazard definitions'))
    for variant in range(2):
        folder=out/f'game-macro-chain-policy{variant}';case=prepare(source_folder,folder,variant);cases.append(case)
        rows.append(dict(moduleId='game-macro-chain',referenceId='macro_chain',sourceKey='pcg/migration/game-sources/game-macro-chain',variant=variant,prepared=core.relative(folder)))
    core.write(out/'manifest.json',dict(rows=rows))
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=2,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'original-macro-late-window-clean'):
        row=next(r for r in rows if case['id'].endswith(str(r['variant'])));check=purpose(case,raw)
        row.update(clean=check,evidence=evidence,reason=raw.get('reason'),actualGoal=raw.get('ok'))
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(row),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',required=True);parser.add_argument('--out',required=True);parser.add_argument('--name',required=True)
    args=parser.parse_args();discover(args.source,args.out,args.name)
