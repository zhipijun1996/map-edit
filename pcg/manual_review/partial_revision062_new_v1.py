"""Preserve native playable new designs without claiming a failed screen passed."""
import shutil,sys
from pcg.migration import core,physics,godot_package,revision062_runtime_v2 as backend
from .continue_revision062_v1 import rows,label,OUT,FINAL
from .execution_revision062_v1 import frozen_row

def main(version,n):
 r=next(r for r in rows()if label(r)==n);source=core.REPO/frozen_row(r,version)['outputDirectory'];f=FINAL/r['moduleId'];assert not f.exists();canonical=core.REPO/'pcg/results'/('approved-r062-'+n+'-canonical-'+version);assert core.read(canonical/'canonical.json')['passed'];f.mkdir(parents=True)
 for p in ['module.mapnote.json','parameters.json','migration.json','cases.json']:shutil.copyfile(source/p,f/p)
 cs=core.read(f/'cases.json')['cases'];core.write(f/'physics-input-cases.json',dict(cases=cs));core.write(f/'playback-cases.json',core.read(canonical/'playback-cases.json'));params=core.read(f/'parameters.json');params['controls']=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs];params['actualVersion']=version;params['fixedEvidence']=physics.artifact(canonical/'canonical.json');core.write(f/'parameters.json',params);screen=core.REPO/'pcg/results'/('approved-r062-'+n+'-control-screen-'+version)/'screen.json'
 core.write(f/'qualification.json',dict(passed=False,actualAttempts=0,formalAttempts=0,status='FIXED_NATIVE_PLAYABLE_SCREEN_UNQUALIFIED',reason='Bounded perturbation screen failed; no independent holdout was opened.',screen=physics.artifact(screen)if screen.exists()else'NOT_RUN',fixed=physics.artifact(canonical/'canonical.json'),noDesignGeometryChange=True))
 core.write(f/'selection.json',dict(version=version,allGatesPassed=False,purpose='reviewable playable sample only; NOT selected for formal qualification',executionInputs=physics.artifact(source/'execution-input-freeze.json')));core.write(f/'frozen.json',dict(module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),cases=physics.artifact(f/'physics-input-cases.json')))
 backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=r['moduleId']);result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);assert result['passed'];print(n,'PARTIAL_NATIVE_DELIVERED',len(cs),flush=True)
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
