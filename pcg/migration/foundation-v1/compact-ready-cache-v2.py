"""Remove only successful compiled scratch copies with exact immutable byte images.

Pending candidates, current/recycle libraries and real experiment raw are excluded.
Every removed file remains recoverable by original cache path and SHA.
"""
from pathlib import Path
import argparse,shutil
from pcg.migration import core


def run(execute=False):
    image=core.REPO/'pcg/results/foundation-migration-preparation-snapshots-v2'
    index_path=image/'index.json';index_hash=core.sha(index_path)
    frozen_index=image/'index-history'/(index_hash+'.json')
    frozen_index.parent.mkdir(parents=True,exist_ok=True)
    if not frozen_index.exists():shutil.copy2(index_path,frozen_index)
    if core.sha(frozen_index)!=index_hash:raise ValueError('immutable_snapshot_index_changed')
    index=core.read(index_path);journal=core.ledger();rows=[];skipped=[]
    for manifest in sorted((core.REPO/'.cache/migration').rglob('godot-package.json')):
        folder=manifest.parent
        if not(folder/'migration.json').is_file():continue
        meta=core.read(folder/'migration.json');entry=journal['entries'].get(meta.get('sourcePath'),{})
        if entry.get('migrationStatus')!='active' or meta.get('godotLoad',{}).get('passed')is not True:continue
        current=core.ACTIVE/entry['moduleId']
        if not(current/'module.mapnote.json').is_file():continue
        version=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion']
        if version!=core.read(current/'module.mapnote.json')['generationContract']['contentVersion']:continue
        files=[];reason=None
        for p in sorted(folder.rglob('*')):
            if p.is_symlink():reason='symlink_preserved';break
            if not p.is_file():continue
            relative=core.relative(p);checksum=core.sha(p)
            record=next((v for v in index['files'].get(relative,[])if v['sha256']==checksum),None)
            if record is None or not(image/record['object']).is_file()or core.sha(image/record['object'])!=checksum:
                reason='exact_snapshot_missing';break
            files.append(dict(path=relative,sha256=checksum,bytes=p.stat().st_size,object=record['object']))
        if reason:skipped.append(dict(path=core.relative(folder),reason=reason));continue
        rows.append(dict(path=core.relative(folder),moduleId=entry['moduleId'],contentVersion=version,current=core.relative(current),files=files,bytes=sum(f['bytes']for f in files)))
    receipt=dict(schema='pcg/successful-compiled-cache-compaction/v1',execute=execute,packages=len(rows),bytes=sum(r['bytes']for r in rows),rows=rows,skipped=skipped,
        snapshotIndex=dict(path=core.relative(frozen_index),sha256=index_hash),
        policy='Only already-active compiled scratch copies, every byte independently retained in immutable experiment-input image. All pending candidates, original sources, current/recycle content and actual raw preserved.')
    # Persist exact recovery inventory before deleting any rebuildable copy.
    core.write(core.STATE/('compiled-cache-compaction-v2.json'if execute else'compiled-cache-compaction-preview-v2.json'),receipt)
    if execute:
        for row in rows:shutil.rmtree(core.REPO/row['path'])
    return {k:receipt[k]for k in ('execute','packages','bytes')}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args();print(run(args.execute))
