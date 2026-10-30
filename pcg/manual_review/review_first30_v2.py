"""Apply the user's explicit first-30 scope to exact recorded design decisions."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
import copy
import shutil
import subprocess
from pathlib import Path
from pcg.migration import core, physics

OUT = core.REPO/'feedback/manual-review/implementation-results/first-30-v2'
AUTH = OUT/'authorization'


def freeze_authorization():
    if AUTH.exists():
        raise ValueError('authorization_snapshot_already_exists')
    handoff = core.read(core.REPO/'feedback/manual-review/implementation-handoff-v1.json')
    decisions = core.read(core.REPO/'feedback/manual-review/received-design-decisions-v1.json')
    rows = [r for r in decisions['rows'] if 1 <= int(r['reviewId']) <= 30]
    assert sorted(int(r['reviewId']) for r in rows) == list(range(1,31))
    approved = [r for r in handoff['rows'] if int(r['reviewId']) <= 30]
    keep = {r['reviewId']:r for r in rows if r['decision']=='KEEP'}
    assert set(keep) == {r['reviewId'] for r in approved}
    for row in approved:
        design=core.REPO/row['designFile'];source=core.REPO/row['sourceModule']['file']
        assert core.sha(design)==row['designFileSha256']
        assert core.read(design)['designVersion']==row['designVersion']==keep[row['reviewId']]['version']
        assert core.sha(source)==row['sourceModule']['sha256']
        assert core.read(source)['generationContract']['contentVersion']==row['sourceModule']['contentVersion']
    core.write(AUTH/'handoff.json',{**handoff,'rows':approved})
    core.write(AUTH/'decisions.json',decisions)
    core.write(AUTH/'request.json',dict(
        verbatim='修正1，2，3。同时前30个module已经经过人工审核需要修改和废弃。废弃的直接删掉。修改的按照新skill实现。',
        baseMain=subprocess.check_output(['git','rev-parse','origin/main'],cwd=core.REPO,text=True).strip(),
        startingCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core.REPO,text=True).strip(),
        mode='approved-design-implementation-and-explicit-deletion',
        keepIds=sorted(keep),discardIds=[r['reviewId'] for r in rows if r['decision']=='DISCARD'],
        noDesignEdits=True,originalPhysicsAndQuality=True,skillsCommit='8d40619cbc7c883b363ab350e4edb7cec84a88cc'))
    print('Frozen:',len(approved),'implementations,',30-len(approved),'explicit deletions')


def discard():
    if (OUT/'deletions.json').exists():raise ValueError('deletion_receipt_already_exists')
    rows=[r for r in core.read(AUTH/'decisions.json')['rows'] if int(r['reviewId'])<=30 and r['decision']=='DISCARD']
    catalog=core.read(core.ACTIVE/'catalog.json');ledger=core.ledger();removed=[]
    aliases=core.read(core.ACTIVE/'aliases.json')['aliases']
    for row in rows:
        folder=core.ACTIVE/core.safe_id(row['moduleId'])
        doc=core.read(folder/'module.mapnote.json')
        assert doc['generationContract']['contentVersion']==row['version'],row['reviewId']
        assert not any(k==row['moduleId'] or v['primaryId']==row['moduleId'] for k,v in aliases.items())
        files=[p for p in folder.rglob('*') if p.is_file()]
        removed.append(dict(**row,directory=core.relative(folder),fileCount=len(files),
            module=physics.artifact(folder/'module.mapnote.json'),
            previousMigration=core.read(folder/'migration.json'),
            restoration='Git history before this deletion; no new recycle package'))
    ids={r['moduleId'] for r in rows}
    for row in rows:
        shutil.rmtree(core.ACTIVE/row['moduleId'])
    catalog['modules']=[r for r in catalog['modules'] if r['id'] not in ids]
    for entry in ledger['entries'].values():
        if entry.get('moduleId') in ids:
            entry.update(migrationStatus='human_discarded_deleted',humanReview='DISCARD',
                deletionReceipt=core.relative(OUT/'deletions.json'),
                previousDestination=entry.pop('destination',None))
    core.write(core.ACTIVE/'catalog.json',catalog);core.write(core.JOURNAL,ledger)
    core.write(OUT/'deletions.json',dict(schema='pcg/explicit-module-deletions/v1',
        authorization=physics.artifact(AUTH/'request.json'),rows=removed,
        deletedCount=len(removed),remainingActiveCount=len(catalog['modules']),
        auditAndDesignHistoryPreserved=True,activeDiscardedModules=[]))
    assert all(not (core.ACTIVE/r['moduleId']).exists() for r in rows)
    print('Deleted',len(removed),'active packages;',len(catalog['modules']),'remain')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','discard'])
    args=parser.parse_args()
    (freeze_authorization if args.action=='freeze' else discard)()
