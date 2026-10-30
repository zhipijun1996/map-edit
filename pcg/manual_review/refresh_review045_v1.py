"""Freeze final approvals and a new explicitly continued repair round."""
import copy,inspect,subprocess
from pcg.migration import core,physics
from . import delete_review040_v1 as deletion
OUT=core.REPO/'feedback/manual-review/implementation-results/review-045-v1'
AUTH=OUT/'authorization'
RETRIES={'115','220','223','225'}
def rows():return core.read(AUTH/'handoff.json')['rows']
def main():
 assert not AUTH.exists()
 handoff=core.read('feedback/manual-review/implementation-handoff-v1.json');decisions=core.read('feedback/manual-review/received-design-decisions-v1.json');old=core.read('feedback/manual-review/implementation-results/review-040-v1/authorization/decisions.json')['rows'];known={r['reviewId']:r for r in old};new=[r for r in decisions['rows']if r['decision']=='KEEP'and known.get(r['reviewId'],{}).get('decision')!='KEEP'];newids={r['reviewId']for r in new};selected=copy.deepcopy([r for r in handoff['rows']if r['reviewId']in newids|RETRIES]);discards=[r['reviewId']for r in decisions['rows']if r['decision']=='DISCARD'and known.get(r['reviewId'],{}).get('decision')!='DISCARD'];assert len(newids)==10 and len(discards)==8 and len(handoff['rows'])==82
 for r in selected:
  assert core.sha(core.REPO/r['designFile'])==r['designFileSha256'] and core.sha(core.REPO/r['sourceModule']['file'])==r['sourceModule']['sha256']
  d=core.read(r['designFile']);assert d['designVersion']==r['designVersion'];assert any(v['reviewId']==r['reviewId']and v['decision']=='KEEP'and v['version']==r['designVersion']for v in decisions['rows'])
  if r['reviewId']in RETRIES:r['previousOutputDirectory']=r['outputDirectory'];r['outputDirectory']='pcg/manual_review/implementation/review-045-drafts-v1/'+r['moduleId']
 request=dict(verbatim='更新main，所有审批完成了',baseMain=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startingCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),mode='new final approvals and continued remaining implementation in independent worktree',keepIds=sorted(newids,key=int),retryIds=sorted(RETRIES,key=int),carriedDesignConflict=['196'],discardIds=discards,pendingIds=[],totalApproved=82,totalDiscarded=143,previousRound=physics.artifact(core.REPO/'feedback/manual-review/implementation-results/review-040-v1/index.json'),previousStoppingPreserved=True,newContinuationRound=True,noDesignEdits=True,originalPhysicsAndQuality=True,developmentBudget=dict(maximumRevisionsPerModule=6,maximumDiagnosticTrialsPerRoutePerRevision=18,maximumScreenTrialsPerRoutePerRevision=13,maximumNativePreflightPerRoutePerRevision=1,selection='first unchanged version passing clean, bounded screen and native preflight; no holdout selection',formalVersionsPerModule=1),screenSeedUnchanged=271028029,duplicate61='explicitly retained by human; audit equivalence to 41, do not claim another gameplay family or independent evidence',existing157Override='feedback/manual-review/implementation-results/157-upper-block-v1/authorization/request.json',existingClarifications='feedback/manual-review/implementation-results/clarified-three-v1/authorization/version-bindings.json')
 core.write(AUTH/'request.json',request);core.write(AUTH/'handoff.json',{**handoff,'rows':selected});core.write(AUTH/'decisions.json',decisions)
 source=inspect.getsource(deletion.main).replace('len(ids)==75','len(ids)==8');scope={**deletion.__dict__,'OUT':OUT,'AUTH':AUTH};exec(compile(source,__file__,'exec'),scope);scope['main']()
 print('FROZEN_FINAL_APPROVALS',request['keepIds'],'REPAIR_ROUND',request['retryIds'],flush=True)
if __name__=='__main__':main()
