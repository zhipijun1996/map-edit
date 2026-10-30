"""Bounded adapted-repair continuation under the same ongoing user task.

Round063's selected formal versions and failures stay immutable. This uses
the pre-existing FULL protocol adaptation cap, with genuinely revised programs
frozen before new pool allocation. The original task's total case cap remains.
"""
from pcg.migration import core,physics,holdout_guard,pool_protocols
from .continue_revision063_v1 import rows,label,OUT as PRIOR_OUT,AUTH as PRIOR_AUTH
from .record_revision063_native_v1 import folder_for
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-064-v1'
AUTH=OUT/'authorization'
def selected():return [r for r in rows()if label(r)in ['hq07','s09']]
def main():
 assert not AUTH.exists();protocol=core.read(physics.FULL_PROTOCOL);assert protocol['maximumAdaptationRevisions']==2
 inputs=list((core.REPO/'pcg/results').glob('approved-r063-*/physics/*.input.json'));used=sum(len(core.read(p).get('cases',[]))for p in inputs);assert used+2000<30000
 frozen=[]
 for row in selected():
  f=folder_for(row);q=core.read(f/'qualification.json');assert not q['passed'];core.verify_artifacts(list(core.read(f/'frozen.json').values()));repair=core.read(core.resolve_artifact(q['knownCalibrationFailuresRepaired']['path']));assert repair['passed'];sel=core.read(f/'selection.json');assert core.read(core.resolve_artifact(sel['screen']['path']))['passed'] and core.read(core.resolve_artifact(sel['native']['path']))['passed'] and core.read(f/'package-result.json')['passed']
  prior=q['priorFailedQualification'];signature=holdout_guard._program_signature(core.read(f/'physics-input-cases.json')['cases']);oldreport=core.read(core.resolve_artifact(prior['report']['path']));oldbinding=core.read(core.resolve_artifact(prior['report']['path']).parent/'input-binding.json');oldcases=core.read(core.resolve_artifact(oldbinding['cases']['path']))['cases'];assert signature!=holdout_guard._program_signature(oldcases)
  frozen.append(dict(name=label(row),reviewId=row['reviewId'],designVersion=row['designVersion'],folder=core.relative(f),module=physics.artifact(f/'module.mapnote.json'),cases=physics.artifact(f/'physics-input-cases.json'),parameters=physics.artifact(f/'parameters.json'),priorFailedQualification=prior,calibrationRepair=q['knownCalibrationFailuresRepaired'],screen=sel['screen'],native=sel['native'],programSignature=signature,source=holdout_guard._identity(f)))
 request=dict(verbatim=core.read(PRIOR_AUTH/'request.json')['verbatim'],sameOngoingUserTask=True,newHumanApproval=False,taskAuthorization=physics.artifact(PRIOR_AUTH/'request.json'),purpose='Finish the already requested HQ07/S09 control repairs after calibration-only diagnosis.',scope=['hq07','s09'],existingProtocol=physics.artifact(physics.FULL_PROTOCOL),existingGlobalAdaptationLimit=2,additionalSelectedFormalCandidatesPerSpec=1,maximumSelectedFormalCandidatesPerSpecAcrossTask=2,originalRound063FormalBudgetUnchanged=True,originalTaskTotalCaseLimit=30000,priorRawInputCaseConservativeCount=used,additionalFormalCaseUpperBound=2000,newGeometryChanges=False,seedsAllocated=False,noHoldoutTuning=True,stopping='One genuinely repaired candidate per specification in this continuation. All prior failures retained. No further same-task formal candidates after the global cap.')
 core.write(AUTH/'request.json',request);core.write(AUTH/'frozen-repairs.json',dict(rows=frozen))
 for v in frozen:
  f=core.REPO/v['folder'];core.verify_artifacts([v[k]for k in ['module','cases','parameters','calibrationRepair','screen','native']]);core.write(f/'selection-r064.json',dict(selectedForFormal=True,authorization=physics.artifact(AUTH/'request.json'),frozenCandidate=v,selection='Both requested repairs included; no selection from newly allocated pools.'))
 print('R064_ADAPTED_REPAIRS_FROZEN',used,[r['name']for r in frozen],flush=True)
if __name__=='__main__':main()
