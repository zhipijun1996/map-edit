"""Freeze the newly approved exact versions and apply explicit discard decisions."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,subprocess,shutil
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/review-029-v1'
AUTH=OUT/'authorization'
def main():
    if AUTH.exists():raise ValueError('refresh_already_frozen')
    prior=core.read('feedback/manual-review/implementation-results/review-refresh-v1/authorization/handoff.json'); prior['rows']+=core.read('feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json')['rows'];done={r['reviewId']:r for r in prior['rows']}
    handoff=core.read('feedback/manual-review/implementation-handoff-v1.json');decisions=core.read('feedback/manual-review/received-design-decisions-v1.json');old_decisions={r['reviewId']:r for r in core.read('feedback/manual-review/implementation-results/review-refresh-v1/authorization/decisions.json')['rows']}
    new=[r for r in handoff['rows']if r['reviewId']not in done or r['designVersion']!=done[r['reviewId']]['designVersion']]
    changed=[r for r in decisions['rows']if old_decisions.get(r['reviewId'])!=r]
    for row in new:
        assert core.sha(core.REPO/row['sourceModule']['file'])==row['sourceModule']['sha256']
        assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
        d=core.read(core.REPO/row['designFile']);assert d.get('designVersion',d.get('generationContract',{}).get('contentVersion'))==row['designVersion']
        assert any(d['reviewId']==row['reviewId']and d['decision']=='KEEP'and d['version']==row['designVersion']for d in decisions['rows'])
    request=dict(existing157Override='feedback/manual-review/implementation-results/157-upper-block-v1/authorization/request.json',developmentBudget=dict(maximumRevisionsPerModule=6,maximumDiagnosticTrialsPerRevision=18,maximumScreenTrialsPerRevision=26,selection='first version passing unchanged screen; no holdout-directed selection',formalVersionsPerModule=1),verbatim='更新最新，继续实现和修改已经经过审核的',baseMain=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startingCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),keepIds=[r['reviewId']for r in new],discardIds=[r['reviewId']for r in changed if r['decision']=='DISCARD'],pendingIds=[r['reviewId']for r in changed if r['decision']=='CHANGE'],mode='approved exact versions; existing discard authorization continues',noDesignEdits=True,originalPhysicsAndQuality=True,selection='freeze once; do not follow subsequent design/main changes')
    core.write(AUTH/'request.json',request);core.write(AUTH/'handoff.json',{**handoff,'rows':new});core.write(AUTH/'decisions.json',decisions)
    catalog=core.read(core.ACTIVE/'catalog.json');ledger=core.ledger();aliases=core.read(core.ACTIVE/'aliases.json')['aliases'];deleted=[]
    for row in [r for r in changed if r['decision']=='DISCARD']:
        folder=core.ACTIVE/row['moduleId'];doc=core.read(folder/'module.mapnote.json');assert doc['generationContract']['contentVersion']==row['version'];assert not any(k==row['moduleId']or v['primaryId']==row['moduleId']for k,v in aliases.items())
        deleted.append(dict(**row,path=core.relative(folder),files=len([p for p in folder.rglob('*')if p.is_file()]),documentSha256=core.sha(folder/'module.mapnote.json'),recoverFromCommit=request['startingCommit']))
    ids={r['moduleId']for r in deleted}
    for mid in ids:shutil.rmtree(core.ACTIVE/mid)
    catalog['modules']=[r for r in catalog['modules']if r['id']not in ids]
    for entry in ledger['entries'].values():
        if entry.get('moduleId')in ids:
            entry.update(migrationStatus='human_discarded_deleted',humanReview='DISCARD',deletionReceipt=core.relative(OUT/'deletions.json'),previousDestination=entry.pop('destination',None))
    core.write(core.ACTIVE/'catalog.json',catalog);core.write(core.JOURNAL,ledger)
    core.write(OUT/'deletions.json',dict(authorization=physics.artifact(AUTH/'request.json'),rows=deleted,count=len(deleted),catalogBefore=len(catalog['modules'])+len(deleted),catalogAfter=len(catalog['modules'])))
    print('FROZEN',len(new),'approved;',len(deleted),'discarded;',request['pendingIds'],'pending')
if __name__=='__main__':main()
