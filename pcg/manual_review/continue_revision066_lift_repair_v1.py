"""One genuine control adaptation under the existing FULL protocol cap of2."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import OUT as PRIOR,AUTH as PRIOR_AUTH,ID
from .run_revision065_lift_v1 import folder_for,rows
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-066-v1';AUTH=OUT/'authorization'
def main():
 assert not AUTH.exists();q=core.read(folder_for(rows()[0])/'qualification.json');assert q['passed']is False
 report=core.read(core.resolve_artifact(q['report']['path']));assert not isinstance(report['routes'][0]['holdout'],dict)
 assert core.read(physics.FULL_PROTOCOL)['maximumAdaptationRevisions']==2
 used=sum(len(core.read(p)['cases'])for p in(core.REPO/'pcg/results').glob('approved-r065-*/physics/*.input.json'));assert used+1000<5000
 core.write(AUTH/'request.json',dict(verbatim='好的，加一个中继台',sameOngoingUserTask=True,newHumanApproval=False,taskAuthorization=physics.artifact(PRIOR_AUTH/'request.json'),scope=[ID],purpose='Correct lower-launch boundary margin and delayed upper boarding found in calibration; retain the approved single relay and all original motion.',originalRound065SelectedCandidates=1,round065BudgetUnchanged=True,existingProtocol=physics.artifact(physics.FULL_PROTOCOL),existingProtocolAdaptationMaximum=2,additionalSelectedFormalCandidates=1,maximumSelectedFormalCandidatesAcrossTask=2,maximumSemanticCandidatesAcrossTask=12,maximumNewGodotCasesAcrossTask=5000,priorRawInputCaseCount=used,priorFailedQualification=q,upperRouteHoldoutNotObserved=True,holdoutTuning=False,stopping='One genuinely repaired formal candidate in this continuation. No further same-task formal candidates or rerolls.'))
 print('R066_BOUNDED_CONTROL_CONTINUATION_FROZEN',used,flush=True)
if __name__=='__main__':main()
