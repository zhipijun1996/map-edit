"""Explicit, versioned corrective bindings after immutable batch diagnostics."""
from __future__ import annotations
import argparse
import collections
import copy
import shutil
from pathlib import Path
from . import core


def bind_references(prepared_root, out):
    from .adaptation import bind_internal_waypoints, persist_macro_components
    from .purpose_compat import bind as bind_compatibility
    source_root, target_root = Path(prepared_root).resolve(), Path(out).resolve()
    if target_root.exists():raise ValueError('revision_destination_exists')
    target_root.mkdir(parents=True)
    rows=[]
    journal=core.ledger()
    for file in sorted(source_root.glob('*/module.mapnote.json')):
        folder=file.parent;meta=core.read(folder/'migration.json')
        if journal['entries'].get(meta['sourcePath'],{}).get('migrationStatus')=='active':
            continue
        row=dict(source=folder.name,status='not_affected')
        try:
            original=core.resolve_artifact(meta['sourcePath']+'/record.json').parent
            original_cases=core.legacy_cases(original)
            doc=core.read(file);cases=core.read(folder/'cases.json')['cases']
            doc,cases,waypoints=bind_internal_waypoints(doc,cases,original_cases)
            doc,cases,compatibility=bind_compatibility(doc,cases,original_cases)
            macro=doc['generationContract']['kind']=='macro'
            if not waypoints['rows'] and not compatibility and not macro:
                rows.append(row);continue
            target=target_root/folder.name
            shutil.copytree(folder,target)
            for name in ('replay-cases.json','physics-input-cases.json','godot-package.json'):
                (target/name).unlink(missing_ok=True)
            if macro:
                doc,children=persist_macro_components(original,target,doc)
                core.write(target/'component-receipts.json',children)
            for validation in doc['generationContract']['validations']:
                validation.update(result='UNKNOWN',artifacts=[],method='pending_corrective_revision_revalidation',unverified=['new_version_not_tested'])
            doc['generationContract']['generation']['migration']['correctiveRevision']=dict(
                previousContentVersion=core.read(file)['generationContract']['contentVersion'],
                internalWaypoints=waypoints['rows'],compatibilityBindings=compatibility,
                policy='Preserve original real assertions; explicit internal docks and retired ownership replaced, no gate lowered.')
            core.write(target/'module.mapnote.json',doc)
            core.write(target/'cases.json',dict(cases=cases))
            meta.update(status='prepared_unverified',evidence=[])
            meta.pop('physicsReport',None);meta.pop('boundaryProbe',None);meta.pop('godotLoad',None)
            core.write(target/'migration.json',meta)
            core.write(target/'reference-revision.json',dict(waypoints=waypoints,compatibility=compatibility))
            result=core.contract(target/'module.mapnote.json',refresh=True)
            row.update(status='prepared_unverified',prepared=core.relative(target),
                contentVersion=result.get('contentVersion'),internalWaypoints=len(waypoints['rows']),
                compatibilityBindings=len(compatibility),macroComponentsRebound=macro)
        except Exception as error:
            row.update(status='repair_required',conflict=str(error))
        rows.append(row)
    report=dict(schema='pcg/migration-reference-revisions/v1',rows=rows,
        counts=dict(collections.Counter(row['status']for row in rows)),technicalAdmission=False)
    core.write(target_root/'manifest.json',report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared-root',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();r=bind_references(a.prepared_root,a.out)
    print(__import__('json').dumps(r['counts'],ensure_ascii=False))
