import ast,shutil
from pathlib import Path
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT,rows,label
from .finalize_revision062_v1 import folder_for
from .reference_audit_revision060_061_v1 import references

def main():
 inputs=[OUT/'index.json',*[OUT/(label(r)+'.json')for r in rows()],*list((OUT/'verification').glob('*.json')),*list((OUT/'fixtures').glob('*/*.json'))];refs={}
 for p in inputs:
  if p.name in ['delivery-reference-audit.json','final-checks.json','public-downloads.json']or p.name.startswith('partial-holdout-lock-snapshot'):continue
  for r in references(core.read(p)):refs[(r['path'],r['sha256'])]=r
 core.verify_artifacts(list(refs.values()));qualified=[r for r in rows()if core.read(folder_for(r)/'qualification.json')['passed']];assert len(qualified)==4
 for r in qualified:assert core.read(OUT/('verification/rederived-'+label(r)+'.json'))['passed']
 # The original raw archive predates read-only observation metadata. Those new
 # JSON files and aliases are tracked directly in Git; every physical raw is
 # already in the SHA-verified archive, without changing its original bytes.
 alias=core.read(OUT/'verification/rs12-same-reserved-execution-alias.json')
 for row in alias['links']:assert (core.REPO/row['aliasPath']).is_symlink()and core.sha(core.REPO/row['aliasPath'])==row['source']['sha256']
 (OUT/'verification/check-logs').mkdir(exist_ok=True)
 for source,name in [('/tmp/r060061-npm-check.log','npm-library-check.log'),('/tmp/r062-partial-holdout-guard-final-test.log','partial-holdout-guard.log'),('/tmp/r062-verify-rs12.log','rejected-report-location.log')]:shutil.copyfile(source,OUT/'verification/check-logs'/name)
 syntax=[]
 for p in sorted((core.REPO/'pcg/manual_review').glob('*062*.py'))+sorted((core.REPO/'pcg/migration').glob('*062*.py'))+[core.REPO/'pcg/migration/partial_holdout_exposure_v1.py',core.REPO/'pcg/migration/holdout_guard.py',core.REPO/'pcg/migration/physics.py']:
  ast.parse(p.read_text(),filename=str(p));syntax.append(core.relative(p))
 core.write(OUT/'verification/delivery-reference-audit.json',dict(passed=True,references=len(refs),qualifiedReports=len(qualified),readOnlyAliasFiles=len(alias['links']),source=physics.artifact(__file__),archivePlusDirectTrackedReadOnlyMetadata=True,globalHistoricalLockSnapshotScope='Snapshot byte hashes verified; ancient other-round raw references inside the global ledger are not restored or re-certified by this task.'))
 core.write(OUT/'verification/final-checks.json',dict(passed=True,nativePlayableDirections=34,actualMovies=8,qualifiedReportsRawRederived=4,knownHQ07ReplayNotIndependentlyQualified=True,protectedOriginalFiles=870,designWebChanged=False,pythonSyntax=syntax,checks=['npm library/contract/workshop checks +11 tests after main merge; no product edits since','actual Godot native packages and films, input/body/HP/support comparison','partial holdout exposure regression on actual old raw and isolated metadata-only negative checks','native original0.08 safe margin probe, actual six-boundary raw contact reanalysis and six synthetic observer vetoes','archive parts +whole ZIP +every entry SHA verified','all linked delivery bytes and strict registered-pool original execution identity'],humanPlaytest='UNKNOWN',productionApproval=False))
 print('062 DELIVERY_REFERENCES_PASS',len(refs),flush=True)
if __name__=='__main__':main()
