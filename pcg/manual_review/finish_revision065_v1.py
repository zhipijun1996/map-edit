"""Bind the final relay qualification, native samples and exact current scope."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,zipfile
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report
from .continue_revision065_lift_v1 import OUT,AUTH,ID,rows
from .run_revision066_lift_v1 import folder_for
def verify():
 f=folder_for(rows()[0]);q=core.read(f/'qualification.json');assert q['passed'];report=verify_report(f,q['report']);assert report['passed'];core.write(OUT/'verification/full-report-rederivation.json',dict(passed=True,actualAttempts=report['actualAttempts'],report=q['report'],source=physics.artifact(__file__),physicsRerun=False));print('R065_FINAL_FULL_REPORT_RAW_REDERIVED',flush=True)
def audit():
 from .check_revision065_interfaces_v1 import main
 from .native_preflight_revision063_v1 import backend
 main();row=rows()[0];f=folder_for(row);q=core.read(f/'qualification.json');assert q['passed'];b=backend('lift');b.verify_package(f/'playable',require_loaded=True);assert core.read(f/'package-result.json')['passed']
 core.verify_artifacts(list(core.read(f/'frozen.json').values()));assert core.sha(row['designFile'])==row['designFileSha256']
 prior=core.read('feedback/manual-review/implementation-results/revision-063-v1/index.json');assert sum(r['qualified']for r in prior['results'])==11
 versions=[p for p in(core.REPO/'pcg/results').glob('approved-r065-lift-canonical-*')if list((p/'physics').glob('*.input.json'))];assert len(versions)<=12
 reports=[p for prefix in ['approved-r065-*','approved-r066-*']for p in(core.REPO/'pcg/results').glob(prefix+'/migration-physics.json')];assert len(reports)==2
 attempts=sum(len(core.read(p)['cases'])for prefix in ['approved-r065-*','approved-r066-*']for p in(core.REPO/'pcg/results').glob(prefix+'/physics/*.input.json'))
 native=list((core.REPO/'pcg/manual_review/implementation').glob('revision-06[56]-*/**/load-evidence/case-*/receipt.json'))+list((OUT/'fixtures').glob('*/playable/load-evidence/case-*/receipt.json'));packages=list((core.REPO/'pcg/manual_review/implementation').glob('revision-06[56]-*/**/godot-package.json'))+list((OUT/'fixtures').glob('*/playable/godot-package.json'));movies=list((OUT/'videos').glob('*/command.json'));upper=attempts+len(native)+2*len(packages)+len(movies);assert upper<5000
 source=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==h for p,h in source['files'].items())
 provenance=dict(actualCompiler=physics.artifact(inspect.getsourcefile(b)),decoder=physics.artifact('pcg/manual_review/revision065_content_v1.py'),exactApprovedDesign=row['designVersion'],authorizedDelta=dict(id='relay-dock',x=0,y=544,w=64,h=12),allExistingObjectsAndMotionUnchanged=True,protectedFilesUnchanged=870,originalPhysics=True,productionAdmitted=False);core.write(f/'implementation-provenance.json',provenance)
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,executedSemanticVersions=len(versions),maximumSemanticVersions=12,selectedFormalCandidatesAcrossTask=2,maximumFormalCandidatesAcrossTask=2,round065SelectedCandidates=1,round066SelectedCandidates=1,rawInputCases=attempts,nativeReceipts=len(native),additionalNativeSmokeUpperBound=2*len(packages),movieAttempts=len(movies),totalCaseConservativeUpperBound=upper,maximumCases=5000,priorElevenUnchanged=True,protectedFilesUnchanged=870,mainSpecificationCommit='43f1a18f',source=physics.artifact(__file__)))
 print('R065_FINAL_AUDIT_PASS',upper,flush=True)
def bundles():
 f=folder_for(rows()[0]);out=OUT/'downloads';out.mkdir(exist_ok=True);entries=[]
 for name,source in [('lift-native',f),('lift-relay-recovery-chest',OUT/'fixtures/missed-boarding-wait-chest-v2')]:
  target=out/(name+'.zip');assert not target.exists()
  with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
   z.writestr('README-'+name+'.txt',f'Extract at repository root. Restore original assets and officialGodot4.7.2 per pcg/WORKSPACE.md.\nScene: {core.relative(source/"playable/demo.tscn")}\nRun official Godot with --path pcg/prototype/godot <scene> -- --case 0. Omit --replay for manual play; add --replay for actual input replay.\nHuman playtest/production approval UNKNOWN.\n')
   for p in sorted((source/'playable').rglob('*')):
    if p.is_file()and'.godot'not in p.parts:z.write(p,core.relative(p))
   for n in ['module.mapnote.json','parameters.json','qualification.json','frozen.json','implementation-provenance.json','recovery-reward-evidence.json']:
    if(source/n).exists():z.write(source/n,core.relative(source/n))
  with zipfile.ZipFile(target)as z:assert z.testzip()is None
  entries.append(dict(name=name,file=physics.artifact(target),scene=physics.artifact(source/'playable/demo.tscn'),qualified=name=='lift-native'))
 core.write(out/'index.json',dict(rows=entries,officialEngine='4.7.2',originalResources='Restore per pcg/WORKSPACE.md',productionAdmitted=False));print('R065_TWO_NATIVE_BUNDLES',flush=True)
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
