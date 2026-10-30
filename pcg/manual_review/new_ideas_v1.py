"""Frozen exact-version scope for the three newly approved idea specifications."""
import subprocess
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/new-ideas-v1'
AUTH=OUT/'authorization'
def rows():return core.read(AUTH/'handoff.json')['rows']
def label(r):return 'orbit'if r['reviewId']=='idea-orbit-choice-001'else r['sourceIdea']['variantKey']
def main():
 assert not AUTH.exists()
 h=core.read('feedback/manual-review/implementation-handoff-v1.json');selected=[r for r in h['rows']if r['reviewId'].startswith('idea-')];assert len(selected)==3
 for r in selected:
  assert core.sha(core.REPO/r['designFile'])==r['designFileSha256'];assert core.read(r['designFile'])['designVersion']==r['designVersion']
  core.verify_artifacts([physics.artifact(core.REPO/r['designDecisionSource'])])
 core.write(AUTH/'request.json',dict(verbatim='更新，拿到新的创意实现，然后进行具体实现',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startingCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),mode='exact approved design implementation',scope=[r['reviewId']for r in selected],families=2,geometryAndDesignPagesFrozen=True,protectedSource='pcg/prototype/godot/source_provenance.json',budget=dict(maximumProgramVersionsPerSpecification=12,maximumDiagnosticTrialsPerRoutePerVersion=18,maximumScreenTrialsPerRoutePerVersion=13,maximumNativePreflightPerRoutePerVersion=1,formalSelectedVersionsPerSpecification=1,screenSeed=271028029,selection='first unchanged candidate passing all clean, clean1/mild6/moderate>=5 of6 and native preflight; no holdout selection',fullProtocol=physics.artifact(physics.FULL_PROTOCOL),additionalCellAndRecoveryTrials=48),existingUnresolvedNotInRound=['42','50','51','52','196','220'],productionAdmission=False))
 core.write(AUTH/'handoff.json',{**h,'rows':selected});core.write(AUTH/'decisions.json',core.read('feedback/manual-review/received-design-decisions-v1.json'));print('FROZEN_NEW_IDEAS',len(selected))
if __name__=='__main__':main()
