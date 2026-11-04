"""Check exact approved content, native packages, source protection and budgets."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pathlib import Path
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,OUT,AUTH
from .record_revision063_native_v1 import folder_for
from .native_preflight_revision063_v1 import backend
def main():
 original=core.read('pcg/prototype/godot/source_provenance.json');assert len(original['files'])==870
 bad=[p for p,h in original['files'].items()if core.sha(core.REPO/'pcg/prototype/godot'/p)!=h];assert not bad;facts=[]
 for r in rows():
  n=label(r);f=folder_for(r);design=core.read(r['designFile']);assert core.sha(r['designFile'])==r['designFileSha256'];doc=core.read(f/'module.mapnote.json');objects={o['id']:o for o in doc['objects']}
  for visual in design['visualObjects']:
   if visual['type']=='route':continue
   actual=objects[visual['id']]
   for key in ['x','y','w','h','trackId','points','designMotion','definition']:
    if key in visual:assert actual[key]==visual[key],(n,visual['id'],key,actual.get(key),visual[key])
  ports=doc['generationContract']['ports'];assert len(ports)==len(design['ports'])
  for a,b in zip(design['ports'],ports):
   assert all(a[k]==b[k]for k in ['id','position','face','normal','surface','permission'])
  assert {p['id']for p in design['intendedRoutes']}=={p['id']for p in doc['generationContract']['routes']}
  core.verify_artifacts(list(core.read(f/'frozen.json').values()));b=backend(n);b.verify_package(f/'playable',require_loaded=True);assert core.read(f/'package-result.json')['passed']
  cs=core.read(f/'playable/cases.json')['cases'];runs=[p for p in(core.REPO/'pcg/results').glob('approved-r063-'+n+'-canonical-*')if list((p/'physics').glob('*.input.json'))];assert len(runs)<=12
  campaigns=[]
  for p in(core.REPO/'pcg/results').glob('approved-r063-'+n+'-*/migration-physics.json'):
   binding=p.parent/'input-binding.json'
   if binding.exists():campaigns.append(core.read(binding)['cases']['sha256'])
  assert len(set(campaigns))<=1,(n,'more_than_one_selected_formal_candidate')
  provenance=dict(actualCompiler=physics.artifact(inspect.getsourcefile(b)),actualDecoder=physics.artifact(core.REPO/'pcg/manual_review/revision063_content_v1.py'),nativeScene=physics.artifact(f/'playable/demo.tscn'),nativeCases=len(cs),exactApprovedGeometry=True,authorizedDesignDelta={'hq09':'TOP initial OUTPUT','s09':'lower wall/rim down16px'}.get(n,'none'),originalPhysics=True,selectedFormalCandidates=len(set(campaigns)),formalCampaignExecutions=len(campaigns),productionApproval=False)
  core.write(f/'implementation-provenance.json',provenance);facts.append(dict(name=n,designVersion=r['designVersion'],nativeCases=len(cs),nativeRoutes=len({c['route_spec']['id']for c in cs}),executedDiagnosticVersions=len(runs),selectedFormalCandidates=len(set(campaigns)),qualified=core.read(f/'qualification.json')['passed'],package=physics.artifact(f/'playable/godot-package.json')))
 inputs=list((core.REPO/'pcg/results').glob('approved-r063-*/physics/*.input.json'));attempts=sum(len(core.read(p).get('cases',[]))for p in inputs)
 native=list((core.REPO/'pcg/manual_review/implementation').glob('revision-063-*/**/load-evidence/case-*/receipt.json'));bonus=list((OUT/'fixtures').glob('*/playable/load-evidence/case-*/receipt.json'));packages=list((core.REPO/'pcg/manual_review/implementation').glob('revision-063-*/**/godot-package.json'));films=list((OUT/'videos').glob('*/command.json'));upper=attempts+len(native)+len(bonus)+2*len(packages)+len(films);assert upper<30000
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,rows=facts,nativeDirections=sum(r['nativeRoutes']for r in facts),rawInputCaseConservativeUpperBound=attempts,nativeReceipts=len(native)+len(bonus),additionalNativeSmokeUpperBound=2*len(packages),movieAttempts=len(films),totalCaseConservativeUpperBound=upper,maximumCases=30000,protectedFiles=870,protectedMismatches=[],protectedSourceCommit=original['commit'],engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),specSyncMainCommit='c04fca59',specSyncReceipt=physics.artifact('feedback/manual-review/spec-sync-r063-receipt.json'),productionAdmitted=False))
 print('R063_APPROVED_GEOMETRY_NATIVE_SOURCE_BUDGET_PASS',upper,flush=True)
if __name__=='__main__':main()
