"""Apply frozen explicit discards; retire aliases whose primary was discarded."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import shutil
from pcg.migration import core,physics
from .refresh_review040_v1 import OUT,AUTH
def main():
 assert not(OUT/'deletions.json').exists()
 request=core.read(AUTH/'request.json');decisions=core.read(AUTH/'decisions.json')['rows'];rows=[r for r in decisions if r['reviewId']in request['discardIds']];ids={r['moduleId']for r in rows};assert len(ids)==75
 catalog=core.read(core.ACTIVE/'catalog.json');ledger=core.ledger();alias_doc=core.read(core.ACTIVE/'aliases.json');removed_aliases={k:v for k,v in alias_doc['aliases'].items()if k in ids or v['primaryId']in ids};deleted=[]
 for key in removed_aliases:assert not(core.ACTIVE/key).exists(),'active_alias_needs_explicit_adjudication'
 for row in rows:
  folder=core.ACTIVE/row['moduleId'];doc=core.read(folder/'module.mapnote.json');assert doc['generationContract']['contentVersion']==row['version']
  deleted.append(dict(**row,path=core.relative(folder),files=sum(p.is_file()for p in folder.rglob('*')),documentSha256=core.sha(folder/'module.mapnote.json'),recoverFromCommit=request['startingCommit']))
 core.write(OUT/'retired-aliases.json',dict(reason='primary explicitly human-discarded; remove dangling active alias, retain duplicate archives and all historical proof',aliases=removed_aliases,recoverFromCommit=request['startingCommit']))
 for mid in ids:shutil.rmtree(core.ACTIVE/mid)
 before=len(catalog['modules']);catalog['modules']=[r for r in catalog['modules']if r['id']not in ids]
 alias_doc['aliases']={k:v for k,v in alias_doc['aliases'].items()if k not in removed_aliases}
 for entry in ledger['entries'].values():
  if entry.get('moduleId')in ids:entry.update(migrationStatus='human_discarded_deleted',humanReview='DISCARD',deletionReceipt=core.relative(OUT/'deletions.json'),previousDestination=entry.pop('destination',None))
  elif entry.get('moduleId')in removed_aliases:entry.update(migrationStatus='duplicate_primary_human_discarded',aliasRetirementReceipt=core.relative(OUT/'retired-aliases.json'),previousDestination=entry.pop('destination',None))
 core.write(core.ACTIVE/'catalog.json',catalog);core.write(core.ACTIVE/'aliases.json',alias_doc);core.write(core.JOURNAL,ledger)
 core.write(OUT/'deletions.json',dict(authorization=physics.artifact(AUTH/'request.json'),rows=deleted,count=len(deleted),catalogBefore=before,catalogAfter=len(catalog['modules']),retiredAliases=physics.artifact(OUT/'retired-aliases.json')))
 print('DELETED',len(deleted),'CATALOG',before,'->',len(catalog['modules']),'RETIRED_ALIASES',list(removed_aliases),flush=True)
if __name__=='__main__':main()
