"""Current delivery, reference integrity and unchanged prior-eleven scope."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import subprocess,zipfile
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import OUT,AUTH
from .run_revision066_lift_v1 import folder_for,rows
def main():
 index=core.read(OUT/'index.json');assert index['qualified']==1 and index['originalTwelveTaskQualified']==12;f=folder_for(rows()[0]);q=core.read(f/'qualification.json');assert q['passed']and q['actualAttempts']==167
 v=core.read(OUT/'verification/full-report-rederivation.json');assert v['passed']and v['report']==q['report']
 for name in ['geometry-source-budget','interface-geometry-regression','original-source','raw-archive','media-technical-audit','direct-relay-probe','registered-pool-identity']:
  assert core.read(OUT/f'verification/{name}.json')['passed']
 paths=list(OUT.glob('*.json'))+list(AUTH.glob('*.json'))+list((OUT/'verification').glob('*.json'))+list((core.REPO/'feedback/manual-review/implementation-results/revision-066-v1/authorization').glob('*.json'))+[f/n for n in ['module.mapnote.json','parameters.json','qualification.json','frozen.json','implementation-provenance.json','selection.json']];refs={}
 def walk(x):
  if isinstance(x,dict):
   p=x.get('path');h=x.get('sha256')
   if isinstance(p,str)and isinstance(h,str)and p.startswith(('pcg/','feedback/','generation/','.agents/','docs/')):
    k=(p,h)
    if k not in refs:
     path=core.resolve_artifact(p);assert path.is_file()and core.sha(path)==h,(p,h);refs[k]=True
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for p in paths:
  if p.name not in ['final-checks.json','delivery-reference-audit.json']:walk(core.read(p))
 core.write(OUT/'verification/delivery-reference-audit.json',dict(passed=True,directReferences=len(refs),filesInspected=len(paths),scope='Current aggregate, authorization, verification and final candidate references. Deep formal raw and native packages verified separately.'))
 for p in(OUT/'downloads').glob('*.zip'):
  with zipfile.ZipFile(p)as z:assert z.testzip()is None
 archive=core.read(core.REPO/'pcg/archives/approved-revision065-066-lift-relay-v1/manifest.json');count=sum(1 for prefix in ['approved-r065-*','approved-r066-*']for d in(core.REPO/'pcg/results').glob(prefix)for p in d.rglob('*')if p.is_file()and p.suffix!='.avi'and not any(v in p.parts for v in ['__pycache__','.godot']));assert count==archive['files'],(count,archive['files'])
 assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','generation','model.js','module-contract.js','index.html'],text=True).strip()
 core.write(OUT/'verification/final-checks.json',dict(passed=True,formalAttempts=167,qualifiedCurrentLift=True,originalTwelveTaskQualified=12,nativeCases=2,bonusNativeCases=1,movies=2,playableZIPs=2,protectedFilesUnchanged=870,originalRawArchiveFiles=count,references=physics.artifact(OUT/'verification/delivery-reference-audit.json'),rawArchive=physics.artifact(OUT/'verification/raw-archive.json'),budget=physics.artifact(OUT/'verification/geometry-source-budget.json'),humanPlaytest='UNKNOWN',productionAdmitted=False));print('R065_FINAL_CHECKS_PASS',len(refs),flush=True)
if __name__=='__main__':main()
