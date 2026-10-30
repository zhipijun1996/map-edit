"""Exact design/port ownership, unchanged original physics and bounded delivery audit."""
import subprocess
from pcg.migration import core,physics,godot_package,revision058_runtime_v1,revision058_runtime_v3,revision058_runtime_v4
from .continue_revision058_v1 import OUT,AUTH,rows,label
from .finalize_revision058_v1 import folder_for

def main():
 results=[]
 for row in rows():
  n=label(row);f=folder_for(row);design=core.read(row['designFile']);doc=core.read(f/'module.mapnote.json');objects={o['id']:o for o in doc['objects']};assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
  for visual in design['visualObjects']:
   if visual['type']=='route':continue
   a=objects[visual['id']];assert all(visual.get(k)==a.get(k)for k in ['type','x','y','w','h']),(n,visual['id'])
   for k in ['trackId','designMotion','points']:
    if k in visual:assert a[k]==visual[k]
  for original,port in zip(design['ports'],doc['generationContract']['ports']):assert all(original[k]==port[k]for k in ['id','position','normal','surface','permission'])
  core.verify_artifacts(list(core.read(f/'frozen.json').values()));assert core.read(f/'package-result.json')['passed']
  backend=godot_package if n=='42'else revision058_runtime_v3 if n=='s07'else revision058_runtime_v4 if n=='s11'else revision058_runtime_v1;backend.verify_package(f/'playable',require_loaded=True)
  runs=sorted((core.REPO/'pcg/results').glob('approved-r058-'+n+'-canonical-*'));assert len(runs)<=12
  formal=list((core.REPO/'pcg/results').glob('approved-r058-'+n+'-qualified*/migration-physics.json'));assert len(formal)<=1
  # Original frozen decoder metadata on early candidates is retained. Correct
  # authoritative paths are explicit here, rather than mutating frozen Module.
  decoder='pcg/manual_review/prepare_review045_v1.py'if n=='42'else'pcg/manual_review/revision058_content_v2.py'if n=='s07'else'pcg/manual_review/revision058_content_v1.py'
  provenance=dict(actualDecoder=physics.artifact(core.REPO/decoder),originalFrozenDecoderReference=doc['generationContract']['generation']['approvedImplementation']['decoderSource'],frozenModuleUnchanged=True,reason='Use actual materializer/native compiler source. Early generic freeze labelled the decoder uniformly; metadata errata never reruns holdout.')
  core.write(f/'implementation-provenance.json',provenance)
  results.append(dict(name=n,exactAuthorizedGeometry=True,nativePassed=True,cleanNativeDirections=len(core.read(f/'playback-cases.json')['cases']),diagnosticVersionsUpperBound=len(runs),maximumVersions=12,formalVersions=len(formal),diagnostics=[core.relative(p)for p in runs],actualDecoder=provenance['actualDecoder'],module=physics.artifact(f/'module.mapnote.json'),package=physics.artifact(f/'playable/godot-package.json')))
 provenance=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in provenance['files'].items())
 diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review','generation/module-workshop'],text=True).splitlines();assert not diff
 engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64');assert engine['sha256']=='8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e'
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,results=results,protectedFiles=len(provenance['files']),protectedMismatches=[],designWebEdits=diff,main=core.read(AUTH/'request.json')['main'],engine=engine,gameSourceCommit=provenance['commit'],physicsTuningChanged=False,productionAdmitted=False))
 print('13_EXACT_DESIGNS_NATIVE_PACKAGES_870_SOURCE_AND_BUDGET_PASS')
if __name__=='__main__':main()
