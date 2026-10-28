"""Read-only reuse of physical evidence for missing data projection parameters.

Never executes Godot or creates an independent experiment. Old raw inputs,
commands, outputs, evaluation seeds and source snapshots are preserved verbatim.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,shutil
from pathlib import Path
from . import core,physics,godot_package
from pcg.prototype.factory.core.quality import digest

ALLOWED_PARAMETERS={'damage','contact_interval','period','initial_phase'}


def projection_diff(old,new):
    """Only additive missing object runtime parameters; everything else exact."""
    restored=copy.deepcopy(new);changes=[]
    if len(old.get('objects',[]))!=len(restored.get('objects',[])):raise ValueError('projection_object_count_changed')
    for index,(before,after)in enumerate(zip(old.get('objects',[]),restored.get('objects',[]))):
        if before['id']!=after['id']:raise ValueError('projection_object_identity_changed')
        previous=before.get('mechanics',{}).get('runtimeParameters',{})
        parameters=after.get('mechanics',{}).get('runtimeParameters',{})
        if not previous.keys()<=parameters.keys():raise ValueError('projection_removed_existing_parameter')
        for key in parameters:
            if key in previous:
                if parameters[key]!=previous[key]:raise ValueError('projection_changed_existing_parameter:'+key)
            else:
                if key not in ALLOWED_PARAMETERS:raise ValueError('projection_unsupported_missing_parameter:'+key)
                changes.append(dict(objectId=before['id'],field='mechanics.runtimeParameters.'+key,value=parameters[key]))
        if 'mechanics'in after and 'runtimeParameters'in after['mechanics']:
            if 'runtimeParameters'in before.get('mechanics',{}):after['mechanics']['runtimeParameters']=copy.deepcopy(previous)
            else:after['mechanics'].pop('runtimeParameters')
            if 'mechanics'not in before and not after['mechanics']:after.pop('mechanics')
    if restored!=old:raise ValueError('projection_changed_geometry_ports_routes_profile_or_other_content')
    if not changes:raise ValueError('projection_has_no_missing_parameters')
    return changes


def unchanged_cases(before,after):
    if before!=after:raise ValueError('projection_changed_physical_case_bytes')


def rebind(folder,report_path,out,derived_run):
    folder=Path(folder).resolve();report_path=Path(report_path).resolve();out=Path(out).resolve();derived_run=Path(derived_run).resolve()
    if out.exists()or derived_run.exists():raise ValueError('projection_destination_exists')
    proof=physics.artifact(report_path)
    # Re-derive all original physical results before proposing a representation.
    old_report=physics.verify_report(folder,proof,deep=True)
    old_doc=core.read(folder/'module.mapnote.json');case_path=folder/'physics-input-cases.json'
    if not case_path.exists():case_path=folder/'cases.json'
    physical_bytes=case_path.read_bytes();cases=json.loads(physical_bytes)['cases']
    new_doc=godot_package.bind_case_behavior(old_doc,cases);changes=projection_diff(old_doc,new_doc)
    godot_package.audit_cases(new_doc,cases,require_replay=False)
    shutil.copytree(folder,out)
    source=out/'projection-source';source.mkdir()
    shutil.copy2(folder/'module.mapnote.json',source/'module.mapnote.json');shutil.copy2(case_path,source/'physical-cases.json')
    core.write(out/'module.mapnote.json',new_doc);core.contract(out/'module.mapnote.json',refresh=True)
    unchanged_cases(physical_bytes,(out/case_path.name).read_bytes())
    new_doc=core.read(out/'module.mapnote.json')
    old_run=report_path.parent
    shutil.copytree(old_run,derived_run,copy_function=os.link,ignore=lambda directory,names:['input-binding.json','migration-physics.json']if Path(directory)==old_run else[])
    input_binding=core.read(old_run/'input-binding.json');input_binding.update(module=physics.artifact(out/'module.mapnote.json'),cases=physics.artifact(out/case_path.name),contentVersion=new_doc['generationContract']['contentVersion'])
    core.write(derived_run/'input-binding.json',input_binding)
    identity=digest(dict(sourceBinding=old_report['sourceBinding'],batches=old_report['batches']))
    receipt=dict(schema='pcg/physical-input-projection-rebind/v1',sourceReport=proof,oldContentVersion=old_doc['generationContract']['contentVersion'],newContentVersion=new_doc['generationContract']['contentVersion'],
        projectionDiff=changes,analysisSource=physics.artifact(Path(__file__)),reusedSimulationIdentity=identity,newlyExecutedAttempts=0,actualAttempts=old_report['actualAttempts'],
        unchangedCanonicalCases=physics.artifact(source/'physical-cases.json'),oldDocument=physics.artifact(source/'module.mapnote.json'),
        evidencePolicy='Old commands, executions, raw bytes, perturbations and evaluation seeds unchanged. This edition is not another calibration or independent holdout. Count reusedSimulationIdentity once.')
    core.write(out/'projection-rebind.json',receipt)
    new_report=copy.deepcopy(old_report);new_report.update(contentVersion=new_doc['generationContract']['contentVersion'],physicalInputProjectionRebind=receipt,
        reusedSimulationIdentity=identity,newlyExecutedAttempts=0)
    core.write(derived_run/'migration-physics.json',new_report)
    # The unchanged verifier reconstructs every input and rechecks every raw.
    physics.verify_report(out,physics.artifact(derived_run/'migration-physics.json'),deep=True)
    core.certify(out,derived_run/'migration-physics.json')
    return dict(prepared=core.relative(out),report=core.relative(derived_run/'migration-physics.json'),receipt=core.relative(out/'projection-rebind.json'),
        reusedSimulationIdentity=identity,newlyExecutedAttempts=0,actualAttempts=old_report['actualAttempts'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',required=True);p.add_argument('--report',required=True);p.add_argument('--out',required=True);p.add_argument('--derived-run',required=True);a=p.parse_args()
    print(json.dumps(rebind(a.folder,a.report,a.out,a.derived_run),indent=2))
