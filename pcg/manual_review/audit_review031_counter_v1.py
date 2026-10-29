"""Test the narrow correction with actual raw and rejecting mutations."""
import copy,gzip,json
from pcg.migration import core,physics,review_counter_scope_v7 as scope
from .prepare_review031_v1 import OUT
def main():
 root=core.REPO/'pcg/results/approved-r031-197-qualified-final-v1';report=core.read(root/'migration-physics.json');row=core.read(core.resolve_artifact(report['counterexamples']['path']))[-1];e=row['evidence'];case=core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
 baseline=core.read(core.resolve_artifact(report['routes'][0]['calibration']['path']))['witness']['result'];q=row['causalCheck'];o=row['externalOutcome'];j=row['adjudication'];good=scope.classify(case,raw,q,o,j,baseline);assert not good['invalidates_design']and not good['accepted_module_solution']and good['actualOutsideFrames']==q['causal']['outsideFrames']
 tests=[]
 for name,mutate in [('other_module',lambda c,r,q:c['approved_implementation'].update(reviewId='198')),('other_version',lambda c,r,q:c['approved_implementation'].update(designVersion='sha256:other')),('unrelated_refusal',lambda c,r,q:q['reasons'].append('actual_player_harm')),('actual_harm',lambda c,r,q:r.update(hp=4)),('reset',lambda c,r,q:r.update(returns=[dict(frame=1)])),('inside_body',lambda c,r,q:r.update(frames=[dict(frame=0,x=100,y=168)])),('different_counter',lambda c,r,q:c['migration_counter'].update(kind='ordinary-jump'))]:
  c,r,check=copy.deepcopy(case),copy.deepcopy(raw),copy.deepcopy(q);mutate(c,r,check);assert scope.classify(c,r,check,o,j,baseline)==j;tests.append(name)
 core.write(OUT/'verification/counter-scope-tests.json',dict(passed=True,actualCorrection=good,rejectedMutations=tests,source=physics.artifact(scope.__file__),sourceReport=physics.artifact(root/'migration-physics.json'),newPhysicsAttempts=0,newIndependentHoldout=False,calibrationHoldoutAndModuleUnchanged=True));print('COUNTER_SCOPE_ACTUAL_AND_NEGATIVE_PASS',flush=True)
if __name__=='__main__':main()
