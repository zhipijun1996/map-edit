"""Freeze and qualify the height-feedback dock repair; preserve prior failures."""
import argparse,copy,inspect,shutil
from pcg.migration import core,physics,godot_package,holdout_guard,review_air_runtime
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_first40_v1 as shared
ROOT=core.REPO/'pcg/manual_review/implementation/first-40-final-v2'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row):
    old=shared.folder_for(row);folder=folder_for(row)
    if folder.exists():raise ValueError('repair_already_frozen')
    selection=core.REPO/'pcg/results/approved-b040-35-control-screen-v7/screen.json';c=copy.deepcopy(core.read(selection)['selected']);assert c
    for k in ('noise','module_sha256','recorded_frames','factory_evidence'):c.pop(k,None)
    c['id']='approved-first40-final-v2-35-entry-to-exit';cases=[c];doc=core.read(old/'module.mapnote.json');g=doc['generationContract'];a=physics.author_for(c)
    g['generation']['approvedImplementation'].update(controlProgramsSha256=digest([c['control_plan']]),repairSelection=physics.artifact(selection),runtimeSource=physics.artifact(physics.runner_for(c,a)),observerSource=physics.artifact(inspect.getsourcefile(a.purpose)))
    doc=godot_package.bind_case_behavior(doc,cases);core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'physics-input-cases.json',dict(cases=cases));core.write(folder/'migration.json',core.read(old/'migration.json'))
    params=core.read(old/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])],repairSelection=physics.artifact(selection));core.write(folder/'parameters.json',params)
    core.write(folder/'frozen.json',{k:physics.artifact(folder/v)for k,v in dict(module='module.mapnote.json',cases='physics-input-cases.json',parameters='parameters.json').items()})
    print('35 v2 frozen',flush=True)
def qualify(row):
    folder=folder_for(row);core.verify_artifacts(list(core.read(folder/'frozen.json').values()));guard=holdout_guard.check(folder,protocol_path=physics.FULL_PROTOCOL)
    c=core.read(folder/'cases.json')['cases'][0];doc=core.read(folder/'module.mapnote.json');costs=dict(routes=72,boundaries=len(physics.seam_cases(c,doc))+2,counters=len(physics.counter_cases(c)));assert sum(costs.values())<=core.read(physics.FULL_PROTOCOL)['maximumAttemptsPerModule']
    core.write(folder/'preflight.json',dict(guard=guard,protocol=physics.artifact(physics.FULL_PROTOCOL),costs=costs,maximumAttempts=sum(costs.values()),selection='first predeclared eligible dock variant; previous failed calibration and all screens retained',priorHoldout='NOT_RUN',stopping='one frozen formal execution; unchanged quality gates'))
    r=physics.run(folder,'approved-b040-35-qualified-final-v2',protocol_path=physics.FULL_PROTOCOL);core.write(folder/'qualification.json',dict(passed=r['passed'],report=physics.artifact(core.REPO/'pcg/results/approved-b040-35-qualified-final-v2/migration-physics.json'),actualAttempts=r['actualAttempts']));print('35 v2 qualified',r['passed'],r['actualAttempts'],flush=True)
def deliver(row):
    folder=folder_for(row);eng,cases,authors=physics._engine(folder,'approved-b040-35-delivery-final-v2',physics.FULL_PROTOCOL);items=[];checks=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery-final')for c in cases],'native-delivery-final')):
        q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));print('35 canonical',q['ok'],q['reasons'],flush=True)
        if q['ok']:items.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(items)==len(cases)));assert len(items)==len(cases)
    core.write(folder/'playback-cases.json',dict(cases=items))
    # This design has no paired gears or AIR ports: the existing diver adapter
    # is the correct original Cell consumer. Do not mutate old first30 backend.
    godot_package.compile_package(folder/'module.mapnote.json',folder/'playback-cases.json',folder/'playable',stable_id=row['moduleId'],_extension=review_air_runtime)
    result=godot_package.run_package_validation(folder/'playable');core.write(folder/'package-result.json',result);print('35 native',result['passed'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);a=p.parse_args();row=next(r for r in core.read(shared.AUTH/'handoff.json')['rows']if r['reviewId']=='35');globals()[a.action](row)
