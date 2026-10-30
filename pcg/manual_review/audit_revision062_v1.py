import inspect,subprocess
from pcg.migration import core,physics,revision060_runtime_v1,revision061_runtime_v2,revision062_runtime_v2
from .continue_revision062_v1 import rows,label,OUT,AUTH
from .finalize_revision062_v1 import folder_for

def main():
 original=core.read('pcg/prototype/godot/source_provenance.json');assert len(original['files'])==870;bad=[p for p,h in original['files'].items()if core.sha(core.REPO/'pcg/prototype/godot'/p)!=h];assert not bad;facts=[]
 for r in rows():
  n=label(r);f=folder_for(r);d=core.read(r['designFile']);assert core.sha(r['designFile'])==r['designFileSha256'];doc=core.read(f/'module.mapnote.json');obs={o['id']:o for o in doc['objects']}
  for visual in d['visualObjects']:
   if visual['type']=='route':continue
   o=obs[visual['id']]
   for k in ['x','y','w','h','trackId','points','designMotion','definition']:
    if k in visual:assert o[k]==visual[k],(n,visual['id'],k,o[k],visual[k])
  assert all(all(p[k]==q[k]for k in ['id','position','face','normal','surface','permission'])for p,q in zip(d['ports'],doc['generationContract']['ports']))
  core.verify_artifacts(list(core.read(f/'frozen.json').values()));backend=revision060_runtime_v1 if n.startswith('hq')else revision061_runtime_v2 if n in ['rs10','rs12']else revision062_runtime_v2;backend.verify_package(f/'playable',require_loaded=True);assert core.read(f/'package-result.json')['passed'];directions=len(core.read(f/'playable/cases.json')['cases']);runs=[p for p in(core.REPO/'pcg/results').glob('approved-r062-'+n+'-canonical-*')if list((p/'physics').glob('*.input.json'))];assert len(runs)<=12
  provenance=dict(actualCompiler=physics.artifact(inspect.getsourcefile(backend)),actualDecoder=physics.artifact(core.REPO/('pcg/manual_review/revision062_repair_content_v1.py'if r['implementationMode']=='repair_input_policy'else'pcg/manual_review/revision062_content_v1.py')),nativeScene=physics.artifact(f/'playable/demo.tscn'),nativeCases=directions,exactApprovedGeometry=True,designGeometryChanges=[],originalPhysics=True,mirror='UNKNOWN',closureConfigurations='UNKNOWN',productionApproval=False)
  if n=='s06':provenance.update(bindingStatus='IMPLEMENTED_NATIVE_RIGID_MOUNT',rigidMount=physics.artifact(core.REPO/'pcg/manual_review/runtime/revision062_mount_v1.gd'),sourceProposalMetadata='Original proposed/missing-binding wording is retained as source history; actual consumer is approved_hq_cells/rigid_mounted_bell and verified native ShotLatch.')
  core.write(f/'implementation-provenance.json',provenance);facts.append(dict(name=n,reviewId=r['reviewId'],designVersion=r['designVersion'],nativeDirections=directions,executedDiagnosticVersions=len(runs),qualified=core.read(f/'qualification.json')['passed'],package=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json')))
 attempts=sum(len(core.read(p).get('cases',[]))for p in(core.REPO/'pcg/results').glob('approved-r062-*/physics/*.input.json'));native=sum(1 for p in(core.REPO/'pcg/manual_review/implementation').glob('revision-062-*/**/load-evidence/case-*/receipt.json'));movies=len(list((OUT/'videos').glob('*/native-receipt.json')));assert attempts+native+movies<30000;web=subprocess.check_output(['git','diff','--name-only','HEAD','--','generation','model.js','module-contract.js','index.html'],text=True).splitlines();assert not web
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,main=core.read(AUTH/'request.json')['main'],rows=facts,rawInputCaseConservativeUpperBound=attempts,nativeCaseReceipts=native,actualMovieRuns=movies,totalCaseConservativeUpperBound=attempts+native+movies,maximumCases=30000,countsIncludeReadOnlyCachedBatchInputDuplicates=True,nativeDirections=sum(x['nativeDirections']for x in facts),protectedFiles=870,protectedMismatches=[],protectedSourceCommit=original['commit'],engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),designWebEdits=[],originalPhysicsChanged=False,productionAdmitted=False));print('062 EXACT_APPROVED_GEOMETRY_NATIVE_ORIGINAL_BUDGET_PASS',attempts,flush=True)
if __name__=='__main__':main()
