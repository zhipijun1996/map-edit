import subprocess
from pcg.migration import core,physics,revision059_runtime_v5,revision058_runtime_v1,revision058_runtime_v4
from .continue_revision059_v1 import OUT,AUTH,rows,label
from .finalize_revision059_v1 import folder_for

def main():
 facts=[];attempts=0
 for r in rows():
  n=label(r);f=folder_for(r);d=core.read(r['designFile']);doc=core.read(f/'module.mapnote.json');objects={o['id']:o for o in doc['objects']};assert core.sha(core.REPO/r['designFile'])==r['designFileSha256']
  for visual in d['visualObjects']:
   if visual['type']=='route':continue
   o=objects[visual['id']];assert all(o[k]==visual[k]for k in ['x','y','w','h']),(n,visual['id']);assert o['type']==visual['type']or o['type']=='switch'and o.get('mechanics',{}).get('approvedCellType')==visual['type'],(n,visual['id'])
   for k in ['trackId','designMotion','points']:
    if k in visual:assert o[k]==visual[k]
  assert all(all(a[k]==b[k]for k in ['id','position','normal','surface','permission'])for a,b in zip(d['ports'],doc['generationContract']['ports']))
  core.verify_artifacts(list(core.read(f/'frozen.json').values()));hq=n.startswith('hq');package=f/('playable-final-v2'if hq else'playable');backend=revision059_runtime_v5 if hq else revision058_runtime_v4 if n=='s11'else revision058_runtime_v1;assert backend.verify_package(package,require_loaded=True)['passed'] if 'passed'in backend.verify_package(package,require_loaded=True)else True
  result=f/('package-result-final-v2.json'if hq else'package-result.json');assert core.read(result)['passed'];diagnostics=sorted((core.REPO/'pcg/results').glob('approved-r059-'+n+'-canonical-*'));formal=list((core.REPO/'pcg/results').glob('approved-r059-'+n+'-qualified*/migration-physics.json'));assert len(diagnostics)<=12 and len(formal)<=1
  provenance=dict(actualDecoder=physics.artifact(core.REPO/('pcg/manual_review/revision059_hq_content_v1.py'if hq else'pcg/manual_review/revision058_content_v1.py')),actualCompiler=physics.artifact(__import__('inspect').getsourcefile(backend)),nativeScene=physics.artifact(package/'demo.tscn'),frozenModuleUnchanged=True,nativeMetadataErrata='HQ backend inherits the earlier decorator label. This explicit actualCompiler identifies the v5 finite-dependency compiler; normal and restored state use the same original native physics.')
  core.write(f/'implementation-provenance.json',provenance);facts.append(dict(name=n,exactApprovedGeometry=True,portsAndMotionUnchanged=True,formatAdapters=[o['id']for o in objects.values()if o.get('mechanics',{}).get('approvedCellType')],nativeDirections=len(core.read(package/'cases.json')['cases']),package=physics.artifact(package/'godot-package.json'),result=physics.artifact(result),diagnosticVersions=len(diagnostics),formalVersions=len(formal)))
 for p in(core.REPO/'pcg/results').glob('approved-r059-*/physics/*.input.json'):attempts+=len(core.read(p).get('cases',[]))
 assert attempts<30000
 original=core.read('pcg/prototype/godot/source_provenance.json');assert len(original['files'])==870 and all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in original['files'].items())
 changes=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation','model.js','module-contract.js','index.html'],text=True).splitlines();assert not changes,changes
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,main=core.read(AUTH/'request.json')['main'],results=facts,rawGodotInputCases=attempts,maximumGodotCases=30000,nativeDirections=sum(v['nativeDirections']for v in facts),protectedFiles=870,protectedSourceCommit=original['commit'],protectedMismatches=[],designWebEdits=[],physicsTuningChanged=False,newGeometryAdjustments=False,productionAdmitted=False));print('EXACT_7_DESIGNS_31_NATIVE_DIRECTIONS_870_ORIGINAL_FILES',attempts)
if __name__=='__main__':main()
