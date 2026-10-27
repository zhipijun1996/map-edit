"""Exact original one/two-jump two-shot fixture; native resource initialization."""
from __future__ import annotations
import argparse,copy,json,shutil
from pathlib import Path
from . import core,physics,game_adapter,game_world_v4,core_preserving,boundary_runtime,resource_original_v9 as original
from .corners import annotate
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/resource_fixture_runner_v10.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*original.SOURCE_DEPENDENCIES,
 core.REPO/'pcg/migration/runtime/native_profile_v5.gd']


def purpose(case,raw):return original.purpose(case,raw)


def fixture_for(source):
    jumps,shots=original.FIXTURE_IDS[source['id']];filename='challenge_recoil_tests.gd'if jumps==1 else'branch_library_runner.gd'
    path='pcg/migration/source-resource-v9/'+filename;identifier=f'original-fixture-{jumps}j{shots}s'
    abilities=['move','jump','shot_recoil']+(['double_jump']if jumps==2 else[])
    profile=dict(id=identifier,overrides=dict(max_jumps=jumps,max_air_shots=shots),abilities=abilities,effectiveTuning=dict(max_jumps=jumps,max_air_shots=shots))
    fixture=dict(provider='original_fixture/v1',id=identifier,source=dict(path=path,sha256=core.sha(core.REPO/path)),
        initializer='ChallengeRecoilTests._fixture'if jumps==1 else'BranchLibraryRunner.fixture',max_jumps=jumps,max_air_shots=shots)
    return profile,fixture


def prepare_one(entry,source,variant,out):
    from . import godot_package_v5
    out=Path(out);base=core.REPO/entry['prepared'];source_folder=core.REPO/entry['sourceKey']
    doc=core.read(base/'module.mapnote.json');case=core.read(base/'cases.json')['cases'][0];original_doc=core.read(source_folder/'module.mapnote.json');source_cases=core.read(source_folder/'cases.json')['cases'];source_cases[0]['id']=case['id']
    doc,cases,receipt=core_preserving.restore_core_shores(doc,[case],original_doc,source_cases)
    value=game_world_v4.native_fields(cases[0],source);profile,fixture=fixture_for(source)
    value['original_tuning_profile']=profile;value['original_fixture_profile']=fixture;value['capabilities']=profile['abilities'][:]
    plan,contract=original.program(source,value,variant);port=next(p for p in doc['generationContract']['ports']if p['id']==value['route_spec']['to_port'])
    tail=copy.deepcopy(value['migration_boundary_continuations'][port['id']]['egress']);tail[-1]['target_x']=port['stagingPosition'][0]
    value.update(id=value['id']+f'-original-fixture-v10-{variant}',control_plan=plan+tail,max_frames=3420,goal=[port['stagingPosition'][0]-8,port['stagingPosition'][1]-5,16,10],exit_port=port['stagingPosition'][:],original_action_contract=contract)
    value['generation_rule']['registration_source']='pcg/migration/resource_fixture_v10.py'
    value['migration_boundary_plans']={value['route_spec']['from_port']:dict(ingress=value['migration_boundary_continuations'][value['route_spec']['from_port']]['ingress'])}
    for field in('module_sha256','recorded_frames','axes','actions'):value.pop(field,None)
    doc['generationContract']['generation']['parameters'].update(controlPlan=value['control_plan'],originalActionContract=contract,original_tuning_profile=profile,original_fixture_profile=fixture)
    for route in doc['generationContract']['routes']:
        route['requiredAbilities']=value['capabilities'];route['capabilityRequirements']['allOf']=[c for c in value['capabilities']if c!='move']
    doc,cases,bindings=boundary_runtime.bind(doc,[value]);doc=godot_package_v5.bind_case_behavior(doc,cases)
    for validation in doc['generationContract']['validations']:validation['capabilityConfiguration']['available']=value['capabilities'][:]
    annotate(doc);shutil.copytree(base,out)
    for name in('physics-input-cases.json','replay-cases.json'):(out/name).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'core-restoration.json',receipt);core.write(out/'boundary-bindings.json',bindings)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',internalGeometryChanged=True);meta['adaptation']['originalFixture']=fixture;core.write(out/'migration.json',meta)
    core.contract(out/'module.mapnote.json',refresh=True);godot_package_v5.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return cases[0]


def discover(out,name):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);sources={r['id']:r for r in game_adapter.source_entries()};rows=[];cases=[];labels={}
    core.write(out/'protocol.json',dict(schema='pcg/original-exact-fixture-discovery/v10',maximumSources=3,maximumVariants=2,maximumAttempts=6,initialization='Exact pinned nativeoriginalfixture resources beforeframe0 only; neveronbindingorport',selection='First successful originalmethod before calibration/holdout; no air_chain substitution'))
    for entry in core.read(core.STATE/'original-remaining62-protocol-v1.json')['rows']:
        if entry['referenceId']not in original.FIXTURE_IDS:continue
        for variant in(0,1):
            folder=out/(entry['stableId']+f'-policy{variant}');row=dict(sourceKey=entry['sourceKey'],moduleId=entry['stableId'],referenceId=entry['referenceId'],variant=variant,prepared=core.relative(folder),status='prepared_unverified')
            try:case=prepare_one(entry,sources[entry['referenceId']],variant,folder);cases.append(case);labels[case['id']]=row
            except Exception as error:row.update(status='binding_gap',conflict=str(error))
            rows.append(row)
    core.write(out/'manifest.json',dict(rows=rows))
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=6,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT);physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'exact-native-fixture-clean'):
        row=labels[case['id']];check=purpose(case,raw);row.update(clean=check,actualGoal=raw.get('ok'),reason=raw.get('reason'),evidence=evidence,status='clean_only'if check['ok']else'current_program_failed')
        if check['ok']:core.write(core.REPO/row['prepared']/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases));print(json.dumps(row),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--name',required=True);a=p.parse_args();discover(a.out,a.name)
