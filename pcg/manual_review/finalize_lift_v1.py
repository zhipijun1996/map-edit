"""Freeze current all-clean native candidate; never turn a failed screen into certification."""
import inspect,sys
from pcg.migration import core,physics,lift_runtime_v1 as backend
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_first40_v1 as shared
from .lift_idea_v1 import rows,AUTH,decode,OUT
ROOT=core.REPO/'pcg/manual_review/implementation/lift-idea-final-v1'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row):
    draft=core.REPO/row['outputDirectory'];screen=core.REPO/'pcg/results/approved-lift-lift-control-screen-v12/screen.json';native=draft/'native-preflight-v12.json'
    assert core.read(native)['passed']
    source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-lift-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/lift_idea_v1.py')
    namespace={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),namespace);namespace['freeze'](row)
    selected=core.read(screen)['passed'];core.write(folder_for(row)/'selection.json',dict(version='v12',allScreenPassed=selected,selectedForFormal=selected,screen=physics.artifact(screen),native=physics.artifact(native),demoOnlyIfUnqualified=True))
    if not selected:core.write(folder_for(row)/'qualification-not-run.json',dict(passed=False,status='UNQUALIFIED',independentHoldoutUsed=False,reason='Twelve executed semantic versions exhausted without all-route screen pass. All-clean native sample is a demonstration only.',screen=physics.artifact(screen),designImpossible=False))
def deliver(row):
    f=folder_for(row);eng,cs,authors=physics._engine(f,'approved-lift-lift-delivery-final-v1',physics.FULL_PROTOCOL);checks=[];items=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery')for c in cs],'native-delivery')):
        check=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=check,evidence=e))
        if check['ok']:items.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(passed=len(items)==len(cs),rows=checks));assert len(items)==len(cs)
    core.write(f/'playback-cases.json',dict(cases=items));backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);print('LIFT_NATIVE',result['passed'],flush=True)
if __name__=='__main__':globals()[sys.argv[1]](rows()[0])
