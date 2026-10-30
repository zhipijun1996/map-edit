"""Correct provenance labels without changing or rerunning any held-out trial."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,inspect,shutil
from pcg.migration import core,physics
from .finalize_first40_v1 import AUTH,folder_for as original_folder
ROOT=core.REPO/'pcg/manual_review/implementation/first-40-bound-v1'
def folder_for(row):return ROOT/row['moduleId']

def run(row):
    n=row['reviewId'];old=original_folder(row);folder=folder_for(row)
    if folder.exists():raise ValueError('metadata_correction_already_exists')
    key='qualification-repaired.json'if n=='34'else'qualification.json';proof=core.read(old/key)['report'];physics.verify_report(old,proof)
    previous=core.read(core.resolve_artifact(proof['path']));cases=core.read(old/'physics-input-cases.json')['cases'];author=physics.author_for(cases[0]);runner=physics.runner_for(cases[0],author);observer=inspect.getsourcefile(author.purpose)
    doc=core.read(old/'module.mapnote.json');impl=doc['generationContract']['generation']['approvedImplementation'];impl['runtimeSource']=physics.artifact(runner);impl['observerSource']=physics.artifact(observer)
    for name in ('cases.json','physics-input-cases.json','parameters.json','migration.json'):folder.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,folder/name)
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);doc=core.read(folder/'module.mapnote.json')
    record=dict(schema='pcg/review-runtime-label-correction/v1',sourceReport=proof,originalModule=physics.artifact(old/'module.mapnote.json'),correctedModule=physics.artifact(folder/'module.mapnote.json'),canonicalCases=physics.artifact(folder/'physics-input-cases.json'),actualRunner=physics.artifact(runner),actualObserver=physics.artifact(observer),newPhysicsAttempts=0,newIndependentHoldout=False,scope='Only approvedImplementation.runtimeSource and observerSource provenance labels; exact executed input, geometry, routes, resources, protocol and all raw unchanged')
    report=copy.deepcopy(previous);report.update(contentVersion=doc['generationContract']['contentVersion'],metadataCorrection=record)
    target=core.resolve_artifact(proof['path']).parent/'migration-physics-runtime-labels-v1.json'
    if target.exists():raise ValueError('metadata_report_already_exists')
    core.write(target,report);updated=physics.artifact(target);physics.verify_report(folder,updated,deep=True)
    core.write(folder/'qualification-corrected.json',dict(passed=True,report=updated,sourceReport=proof,newIndependentHoldout=False,newPhysicsAttempts=0))
    core.write(folder/'frozen.json',{k:physics.artifact(folder/v)for k,v in dict(module='module.mapnote.json',cases='physics-input-cases.json',parameters='parameters.json').items()})
    print(n,'runtime labels rebound and deeply verified',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');a=p.parse_args()
    for r in core.read(AUTH/'handoff.json')['rows']:
        if r['reviewId']in a.ids:run(r)
