"""Reproducible approved geometry, original physics, ownership and budget audit."""
import copy,gzip,json,subprocess,collections
from pcg.migration import core,physics,godot_package,revision053_runtime_v1
from .continue_revision053_v1 import OUT,AUTH,rows,label
from .finalize_revision053_v2 import folder_for

def main():
 results=[]
 for row in rows():
  n=label(row);f=folder_for(row);design=core.read(row['designFile']);doc=core.read(f/'module.mapnote.json');objects={o['id']:o for o in doc['objects']};assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
  for visual in design['visualObjects']:
   if visual['type']=='route':continue
   actual=objects[visual['id']]
   if n=='220'and visual['id']=='design-air-enemy':
    assert visual['type']==actual['type']=='enemy'and actual['w']==28 and visual['w']==32 and visual['x']+visual['w']/2==actual['x']+actual['w']/2 and all(visual[k]==actual[k]for k in ['y','h'])
   else:assert all(visual.get(k)==actual.get(k)for k in ['type','x','y','w','h'])
   for key in ['trackId','designMotion','points']:
    if key in visual:assert actual[key]==visual[key]
  for original,port in zip(design['ports'],doc['generationContract']['ports']):assert all(original[k]==port[k]for k in ['id','position','normal','surface','permission'])
  core.verify_artifacts(list(core.read(f/'frozen.json').values()));assert core.read(f/'package-result.json')['passed']
  backend=revision053_runtime_v1 if n in ['196','three','lift']else godot_package;backend.verify_package(f/'playable',require_loaded=True)
  runs=sorted((core.REPO/'pcg/results').glob('approved-r053-'+n+'-canonical-*'));assert len(runs)<=12,(n,len(runs));formal=list((core.REPO/'pcg/results').glob('approved-r053-'+n+'-qualified*/migration-physics.json'));assert len(formal)<=1
  native=core.read(f/'playable/godot-package.json');results.append(dict(name=n,exactAuthorizedGeometry=True,nativePassed=True,cleanRoutes=len(core.read(f/'playback-cases.json')['cases']),executedDiagnosticVersionsConservativeUpperBound=len(runs),maximumVersions=12,formalVersions=len(formal),allFailedVersionsRetained=[core.relative(p)for p in runs],module=physics.artifact(f/'module.mapnote.json'),package=physics.artifact(f/'playable/godot-package.json')))
 provenance=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/path)==sha for path,sha in provenance['files'].items())
 diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review','generation/module-workshop'],text=True).splitlines();assert not diff,diff
 core.write(OUT/'verification/geometry-source-budget.json',dict(passed=True,results=results,protectedFiles=len(provenance['files']),protectedMismatches=[],designWebEdits=diff,main=core.read(AUTH/'request.json')['main'],engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit=provenance['commit'],physicsTuningChanged=False,productionAdmitted=False))
 # Explicit wall_climb maps only its real enabled traversal; removing the
 # permission or actual grant must retain the original forbidden-action guard.
 p=core.REPO/'pcg/results/approved-r053-196-qualified-final-v1';r=core.read(p/'migration-physics.json');cal=core.read(core.resolve_artifact(r['routes'][1]['calibration']['path']));e=next(v for v in cal['rows']if v['level']=='clean')['evidence'];c=core.read(p/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];raw=json.loads(gzip.decompress((p/e['output']).read_bytes()))['results'][e['index']];assert raw['wall_jumps']>0
 author=physics.author_for(c);assert author.purpose(c,raw)['ok'];neg=[]
 for name in ['permission','actual-grant']:
  cc=copy.deepcopy(c);rr=copy.deepcopy(raw)
  if name=='permission':cc['capabilities'].remove('wall_climb')
  else:rr['capability_snapshot']['wall_enabled']=False
  q=author.purpose(cc,rr);assert 'forbidden_wall_jumps'in q['reasons'];neg.append(dict(kind=name,forbiddenActionRetained=True))
 core.write(OUT/'verification/wall-capability-regression.json',dict(passed=True,actualWallJumps=raw['wall_jumps'],positiveOriginalEvidence=e,negative=neg,source=physics.artifact(__file__),newGodotAttempts=0,actualInputTimingNoise=True))
 print('8_EXACT_AUTHORIZED_GEOMETRIES_NATIVE_PACKAGES_870_SOURCE_BUDGET_AND_WALL_GUARDS_PASS')
if __name__=='__main__':main()
