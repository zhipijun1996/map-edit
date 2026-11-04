"""Exact approved geometry, protected original files, frozen inputs and native packages."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import importlib,subprocess
from pcg.migration import core,physics,revision060_runtime_v1,revision060_runtime_v2,revision061_runtime_v2

def main():
 original=core.read('pcg/prototype/godot/source_provenance.json');assert len(original['files'])==870;bad=[p for p,h in original['files'].items()if core.sha(core.REPO/'pcg/prototype/godot'/p)!=h];assert not bad
 for version in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+version+'_v1');final=importlib.import_module('pcg.manual_review.finalize_revision'+version+'_v1');facts=[]
  for row in scope.rows():
   n=scope.label(row);f=final.folder_for(row);d=core.read(row['designFile']);assert core.sha(row['designFile'])==row['designFileSha256'];doc=core.read(f/'module.mapnote.json');obs={o['id']:o for o in doc['objects']};adjust=[]
   for visual in d['visualObjects']:
    if visual['type']=='route':continue
    o=obs[visual['id']]
    for k in ['x','y','w','h']:
     if version=='060'and n=='hq02'and visual['id']=='middle'and k=='w':assert visual[k]==64 and o[k]==112;adjust.append('authorized middle width64→112');continue
     assert o[k]==visual[k],(version,n,visual['id'],k,o[k],visual[k])
    for k in ['trackId','points']:
     if k in visual:assert o[k]==visual[k]
    if visual.get('designMotion')and not(version=='061'and n=='s11'):assert o['designMotion']==visual['designMotion']
   assert all(all(p[k]==q[k]for k in ['id','position','face','normal','surface','permission'])for p,q in zip(d['ports'],doc['generationContract']['ports']))
   core.verify_artifacts(list(core.read(f/'frozen.json').values()));p=f/('playable-presentation-v2'if version=='060'and n=='hq09'else'playable');backend=revision060_runtime_v2 if version=='060'and n=='hq09'else revision060_runtime_v1 if version=='060'else revision061_runtime_v2;verified=backend.verify_package(p,require_loaded=True);result=f/('package-result-presentation-v2.json'if p.name=='playable-presentation-v2'else'package-result.json');assert core.read(result)['passed'];native_cases=core.read(p/'cases.json')['cases'];runs=sorted((core.REPO/'pcg/results').glob('approved-r'+version+'-'+n+'-canonical-*'));executed=[x for x in runs if list((x/'physics').glob('*.input.json'))];assert len(executed)<=12,(n,len(executed))
   provenance=dict(actualDecoder=physics.artifact(core.REPO/('pcg/manual_review/revision060_content_v1.py'if version=='060'else'pcg/manual_review/revision061_content_v2.py')),actualCompiler=physics.artifact(__import__('inspect').getsourcefile(backend)),nativeScene=physics.artifact(p/'demo.tscn'),nativeCases=len(native_cases),exactApprovedGeometry=True,authorizedAdjustments=adjust,originalPhysics=True,mirror='UNKNOWN',closureConfigurations='UNKNOWN',productionApproval=False);core.write(f/'implementation-provenance.json',provenance);facts.append(dict(name=n,reviewId=row['reviewId'],designVersion=row['designVersion'],nativeDirections=len(native_cases),geometryAdjustments=adjust,executedDiagnosticVersions=len(executed),qualification=core.read(f/'qualification.json')['passed'],package=physics.artifact(p/'godot-package.json'),result=physics.artifact(result)))
  attempts=sum(len(core.read(p).get('cases',[]))for p in(core.REPO/'pcg/results').glob('approved-r'+version+'-*/physics/*.input.json'));assert attempts<30000;web=subprocess.check_output(['git','diff','--name-only','HEAD','--','generation','model.js','module-contract.js','index.html'],text=True).splitlines();assert not web,web
  core.write(scope.OUT/'verification/geometry-source-budget.json',dict(passed=True,main=core.read(scope.AUTH/'request.json')['main'],rows=facts,rawInputCaseConservativeUpperBound=attempts,maximumCases=30000,countsIncludeReadOnlyCachedBatchInputDuplicates=True,nativeDirections=sum(x['nativeDirections']for x in facts),protectedFiles=870,protectedMismatches=bad,protectedSourceCommit=original['commit'],engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),designWebEdits=[],originalPhysicsChanged=False,productionAdmitted=False))
  print(version,'EXACT_GEOMETRY_NATIVE_PROTECTED_BUDGET_PASS',attempts,len(facts),flush=True)
if __name__=='__main__':main()
