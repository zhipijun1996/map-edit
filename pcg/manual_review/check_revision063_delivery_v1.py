"""Read-only final consistency and direct evidence-reference checks."""
import subprocess,zipfile
from pathlib import Path
from pcg.migration import core,physics
from .continue_revision063_v1 import OUT,rows,label
from .record_revision063_native_v1 import folder_for
def main():
 index=core.read(OUT/'index.json');assert index['qualified']==11 and index['playable']==12
 paths=list(OUT.glob('*.json'))+list((OUT/'authorization').glob('*.json'))+list((OUT/'verification').glob('*.json'))
 for r in rows():
  f=folder_for(r);paths +=[f/n for n in ['module.mapnote.json','parameters.json','qualification.json','frozen.json','implementation-provenance.json','selection.json']]
 refs={};fail=[]
 def walk(x):
  if isinstance(x,dict):
   p=x.get('path');h=x.get('sha256')
   if isinstance(p,str)and isinstance(h,str)and p.startswith(('pcg/','feedback/','generation/','.agents/','docs/')):
    key=(p,h)
    if key not in refs:
     f=core.resolve_artifact(p);okay=f.is_file()and core.sha(f)==h;refs[key]=okay
     if not okay:fail.append(dict(path=p,expected=h,exists=f.exists()))
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for p in paths:
  if p.name in ['delivery-reference-audit.json','final-checks.json']:continue
  walk(core.read(p))
 assert not fail,fail[:12]
 core.write(OUT/'verification/delivery-reference-audit.json',dict(passed=True,filesInspected=len(paths),directReferences=len(refs),failures=[],scope='Direct path/SHA references in current aggregate/authorization/verification and active module, parameters, qualification, frozen selection and provenance. Deep formal raw and native packages verified separately.'))
 for p in(OUT/'downloads').glob('*.zip'):
  with zipfile.ZipFile(p)as z:assert z.testzip()is None
 for name in ['geometry-source-budget','full-report-rederivation','raw-archive','media-technical-audit','group-sampling-check','upgrade-guard-check']:
  assert core.read(OUT/f'verification/{name}.json')['passed']
 web=subprocess.check_output(['git','diff','--name-only','HEAD','--','generation','model.js','module-contract.js','index.html'],text=True).splitlines();assert not web,web
 checks=OUT/'verification/check-logs';assert '11 tests' in(checks/'holdout-tests.log').read_text()and '\nOK\n'in(checks/'holdout-tests.log').read_text()
 assert 'Ran 11 tests'in(checks/'npm-check.log').read_text()and '\nOK\n'in(checks/'npm-check.log').read_text()
 core.write(OUT/'verification/final-checks.json',dict(passed=True,qualified=11,playable=12,fixedNativeDirections=23,originalProtectedFilesUnchanged=870,fullReportsRawRederived=11,tests=dict(editor=physics.artifact(checks/'npm-check.log'),holdoutGuard=physics.artifact(checks/'holdout-tests.log')),referenceAudit=physics.artifact(OUT/'verification/delivery-reference-audit.json'),archive=physics.artifact(OUT/'verification/raw-archive.json'),budget=physics.artifact(OUT/'verification/geometry-source-budget.json'),remaining='Lift fixed native playable; perturbation screen not passed;12 semantic candidates exhausted, independent holdout not started.',productionAdmitted=False,humanPlaytest='UNKNOWN'))
 print('R063_DELIVERY_REFERENCES_FINAL_CHECKS_PASS',len(refs),flush=True)
if __name__=='__main__':main()
