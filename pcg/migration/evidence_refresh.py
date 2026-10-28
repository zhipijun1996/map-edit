"""Narrow proof for correcting a validation's recorded available capabilities.

This changes evidence metadata only. It grants no capability, changes no physics
input, reruns no calibration, and bypasses none of the native package validators.
The caller installs the resulting package through core's existing refresh WAL.
"""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from . import core


def _canonical(value):
    # Typed JSON comparison also rejects bool/int and int/float substitutions.
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def _artifact(path):return dict(path=core.relative(path),sha256=core.sha(path))


def prove_available_correction(current_folder,prepared_folder):
    """Validate both native packages and prove only actual bound caps changed.

    A returned dict is an inline WAL/history proof, not a new physics certificate.
    Every original identity and human/production field remains subject to the
    enclosing refresh_package checks as well.
    """
    current=Path(current_folder).resolve();prepared=Path(prepared_folder).resolve()
    old=core.read(current/'module.mapnote.json');new=core.read(prepared/'module.mapnote.json')
    old_meta=core.read(current/'migration.json');new_meta=core.read(prepared/'migration.json')
    if old.get('generationContract',{}).get('contentVersion')!=new.get('generationContract',{}).get('contentVersion'):
        raise ValueError('evidence_refresh_content_version_changed')
    if old_meta.get('physicsReport')!=new_meta.get('physicsReport'):
        raise ValueError('evidence_refresh_original_physics_report_changed')
    # These calls require original raw/calibration/holdout, source bindings, and
    # actual native replay bound to each package's respective document bytes.
    core.validate(current,require_certified=True)
    core.validate(prepared,require_certified=True)
    proof=old_meta.get('physicsReport')
    if not isinstance(proof,dict)or not proof.get('path'):
        raise ValueError('evidence_refresh_original_physics_report_required')
    core.verify_artifacts([proof])
    report_path=core.resolve_artifact(proof['path']);report=core.read(report_path)
    binding_path=report_path.parent/'input-binding.json';binding=core.read(binding_path)
    version=old['generationContract']['contentVersion']
    if report.get('contentVersion')!=version or binding.get('contentVersion')!=version:
        raise ValueError('evidence_refresh_original_physics_version_mismatch')
    inputs=[]
    for folder in (current,prepared):
        path=folder/'physics-input-cases.json'
        if not path.is_file()or core.sha(path)!=binding.get('cases',{}).get('sha256'):
            raise ValueError('evidence_refresh_actual_bound_cases_changed')
        inputs.append(_artifact(path))
    cases=core.read(current/'physics-input-cases.json')['cases'];caps={}
    for case in cases:
        route=case.get('route_spec',{}).get('id');available=case.get('capabilities')
        if not isinstance(route,str)or not isinstance(available,list)or not available or any(not isinstance(a,str)or not a for a in available)or len(set(available))!=len(available)or route in caps:
            raise ValueError('evidence_refresh_unambiguous_actual_route_caps_required')
        caps[route]=available
    if set(caps)!={r['routeId']for r in report['routes']}:
        raise ValueError('evidence_refresh_actual_report_route_set_changed')
    a=copy.deepcopy(old);b=copy.deepcopy(new)
    old_validations=a['generationContract'].get('validations',[]);new_validations=b['generationContract'].get('validations',[])
    if len(old_validations)!=len(new_validations):raise ValueError('evidence_refresh_validation_set_changed')
    changes=[]
    for before,after in zip(old_validations,new_validations):
        previous=before.get('capabilityConfiguration',{});updated=after.get('capabilityConfiguration',{})
        if 'available'not in previous or 'available'not in updated:
            if _canonical(before)!=_canonical(after):raise ValueError('evidence_refresh_existing_available_field_required')
            continue
        if _canonical(previous['available'])==_canonical(updated['available']):continue
        route=before.get('routeId')
        if before.get('kind')!='physics'or route not in caps or _canonical(updated['available'])!=_canonical(caps[route]):
            raise ValueError('evidence_refresh_available_must_equal_actual_bound_route_caps')
        changes.append(dict(validationId=before.get('id'),routeId=route,before=copy.deepcopy(previous['available']),after=copy.deepcopy(updated['available'])))
        previous.pop('available');updated.pop('available')
    if _canonical(a)!=_canonical(b):raise ValueError('evidence_refresh_other_document_field_changed')
    if not changes:raise ValueError('evidence_refresh_no_available_correction')
    archive=core.RECYCLE/old_meta['moduleId']/('compiled-'+core.sha(current/'godot-package.json'))
    result=dict(schema='pcg/validation-available-correction/v1',contentVersion=version,
        previousDocument=_artifact(current/'module.mapnote.json'),correctedDocument=_artifact(prepared/'module.mapnote.json'),
        archivedPreviousDocument=dict(path=core.relative(archive/'module.mapnote.json'),sha256=core.sha(current/'module.mapnote.json')),
        originalPhysicsReport=copy.deepcopy(proof),originalInputBinding=_artifact(binding_path),canonicalInputs=inputs,
        changes=changes,validatorSource=_artifact(Path(__file__)),
        nativePackagesRevalidated=True,newPhysicsExperiments=0,humanApprovalChanged=False,
        scope='Only validations[*].capabilityConfiguration.available corrected to exact existing canonical route capabilities. All other document fields and original physics evidence unchanged; native replay separately required.')
    result['proofSha256']=hashlib.sha256(_canonical(result).encode()).hexdigest()
    return result
