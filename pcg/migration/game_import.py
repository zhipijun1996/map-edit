"""Pin original game Module sources without editing the formal game checkout.

The existing source snapshot is reused when its actual Git blob matches the
fixed remote inventory. This is source import, never Module certification.
"""
import hashlib
import shutil
from pathlib import Path
from . import core


def git_blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def run():
    inventory=core.read(core.STATE/'inventory-game-v1.json')
    commit=inventory['remote']['commit']
    rows=[]; conflicts=[]
    registries={**inventory['remote']['registries'], 'dependencies':inventory['extra_remote_verified_files']}
    # The old Map layout generator is reference history, not a Module dependency.
    for kind in ('resources','scenes','generation','foundry','dependencies'):
        for entry in registries[kind]:
            if entry.get('type','file')!='file' or not entry.get('git_blob_sha'):continue
            path=entry['path']
            target=core.REPO/'library/source'/path
            original=Path('/workspace/gunman-rush')/path
            expected=entry['git_blob_sha']
            action='reused_exact_existing_copy'
            if not target.is_file() or git_blob(target)!=expected:
                if not original.is_file() or git_blob(original)!=expected:
                    conflicts.append(dict(path=path,reason='fixed_remote_source_not_available_locally'));continue
                # Never overwrite the historical snapshot. Only differing new
                # dependencies occupy this single current import subdirectory.
                target=core.REPO/'library/source/game-import'/path
                if target.exists()and git_blob(target)!=expected:
                    conflicts.append(dict(path=path,reason='current_import_conflict'));continue
                if not target.exists():
                    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
                action='copied_verified_original'
            rows.append(dict(kind=kind,originalPath=path,path=core.relative(target),
                sha256=core.sha(target),gitBlobSha=expected,sourceCommit=commit,action=action))
    with core._migration_lock():
        journal=core.ledger()
        for row in rows:
            if row['kind']!='resources':continue
            key=row['path']
            previous=journal['entries'].get(key,{})
            if previous.get('migrationStatus')in ('active','recycled'):continue
            journal['entries'][key]=dict(sourceType='original_game',sourceCommit=commit,
                source=key,sha256=row['sha256'],migrationStatus='needs_repair',destination='original',
                gaps=['original_resource_to_exact_v2_Cell_and_external_mechanism_decoder',
                      'rectangle_height_and_real_boundary_port_adaptation',
                      'pinned_runtime_and_actual_route_certification'],
                humanReview='UNKNOWN')
        core.write(core.JOURNAL,journal)
    report=dict(schema='pcg/game-module-source-import/v1',sourceCommit=commit,
        moduleResourceCount=sum(row['kind']=='resources'for row in rows),
        verifiedFiles=len(rows),reusedFiles=sum(row['action']=='reused_exact_existing_copy'for row in rows),
        copiedFiles=sum(row['action']=='copied_verified_original'for row in rows),
        files=rows,conflicts=conflicts,originalGameModified=False,newPhysicsCases=0,
        foundationCertifiedModules=0,
        warning='Exact source import is not a migrated/physics-certified Module. Old 177 references include procedural samples and composites.')
    core.write(core.STATE/'game-source-import.json',report)
    return {k:v for k,v in report.items()if k!='files'}


if __name__=='__main__':
    import json
    print(json.dumps(run(),ensure_ascii=False,indent=2))
