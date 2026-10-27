"""Preserve scratch experiment inputs as immutable evidence, never a Module library.

The source path and observed byte SHA are recorded separately from historical
experiment references. A post-certification document is not relabelled as its
earlier input byte image. Multiple observed revisions are retained by hash.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
from . import core

SUFFIXES={'.json','.py','.gd','.tscn','.mjs','.md','.tres','.uid','.svg','.log'}
DEFAULT=core.REPO/'pcg/results/foundation-migration-preparation-snapshots-v2'


def capture(out=DEFAULT):
    out=Path(out).resolve();source=core.REPO/'.cache/migration'
    if not out.is_relative_to(core.REPO/'pcg/results'):
        raise ValueError('evidence_snapshot_must_live_in_existing_experiment_archive_namespace')
    out.mkdir(parents=True,exist_ok=True)
    index_path=out/'index.json'
    index=core.read(index_path)if index_path.exists()else dict(
        schema='pcg/migration-scratch-evidence/v1',purpose='immutable_experiment_input_evidence_not_a_candidate_library',
        sourceRoot=core.relative(source),files={},missingHistoricalByteImages='Not reconstructed or claimed by this snapshot.')
    captured=skipped=0
    for path in sorted(source.rglob('*')):
        if not path.is_file()or path.suffix not in SUFFIXES or any(p in ('.godot','__pycache__','frozen-sources','deep-verification')for p in path.parts):
            continue
        try:
            before=path.stat();data=path.read_bytes();after=path.stat()
            if (before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                skipped+=1;continue
            if path.suffix=='.json':
                try:__import__('json').loads(data)
                except (ValueError,UnicodeError):skipped+=1;continue
            checksum=hashlib.sha256(data).hexdigest()
            target=out/'objects'/checksum[:2]/(checksum+path.suffix)
            if not target.exists():
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb')as stream:stream.write(data)
            if core.sha(target)!=checksum:raise ValueError('immutable_snapshot_object_changed:'+str(target))
            relative=core.relative(path)
            versions=index['files'].setdefault(relative,[])
            if not any(v['sha256']==checksum for v in versions):
                versions.append(dict(sha256=checksum,bytes=len(data),object=target.relative_to(out).as_posix(),
                    observation='observed_current_bytes_not_assumed_historical_execution_input'))
                captured+=1
        except FileNotFoundError:
            skipped+=1
    # Current migration source is a separate analysis/build tool snapshot. It is
    # never substituted for a historical run's already-frozen source image.
    tools={}
    for path in sorted((core.REPO/'pcg/migration').rglob('*')):
        if not path.is_file()or path.suffix not in {'.py','.gd','.mjs'}or'__pycache__'in path.parts:continue
        data=path.read_bytes();checksum=hashlib.sha256(data).hexdigest()
        target=out/'tool-source'/path.relative_to(core.REPO/'pcg/migration')
        if target.exists()and core.sha(target)!=checksum:
            target=out/'tool-source-revisions'/checksum/path.name
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        tools[core.relative(path)]=dict(sha256=checksum,object=target.relative_to(out).as_posix())
    index['currentToolSources']=tools
    index['sourcePaths']=len(index['files'])
    index['observedVersions']=sum(map(len,index['files'].values()))
    index['lastCapture']=dict(newObservedVersions=captured,mutatingOrMissingFilesSkipped=skipped)
    core.write(index_path,index)
    return {k:v for k,v in index.items()if k not in ('files','currentToolSources')}


def restore(source_path,checksum,out=DEFAULT):
    target=(core.REPO/source_path).resolve()
    if not target.is_relative_to(core.REPO/'.cache/migration'):
        raise ValueError('restore_only_to_original_migration_scratch_namespace')
    index=core.read(Path(out)/'index.json')
    records=index['files'].get(source_path,[])
    record=next((v for v in records if v['sha256']==checksum),None)
    if record is None:raise ValueError('exact_historical_byte_image_not_in_snapshot')
    stored=(Path(out)/record['object']).resolve()
    if not stored.is_relative_to(Path(out).resolve())or core.sha(stored)!=checksum:
        raise ValueError('snapshot_integrity_or_path_failure')
    if target.exists():
        if core.sha(target)!=checksum:raise ValueError('existing_scratch_bytes_differ_preserved')
        return dict(status='already_present',path=source_path,sha256=checksum)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb')as stream:stream.write(stored.read_bytes())
    return dict(status='restored',path=source_path,sha256=checksum)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=DEFAULT)
    p.add_argument('--restore-path');p.add_argument('--sha256');a=p.parse_args()
    if a.restore_path and not a.sha256:p.error('--restore-path needs exact --sha256')
    result=restore(a.restore_path,a.sha256,a.out)if a.restore_path else capture(a.out)
    print(__import__('json').dumps(result,ensure_ascii=False))
