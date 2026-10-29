"""Actual immutable evidence plus rejecting mutations; no new Godot trials."""
import copy,gzip,json
from pcg.migration import core,physics,review_boundary_observer_v1 as boundary,review_counter_scope_v8 as counter
from .prepare_review040_v3 import OUT
def load(root,e):
 return (core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']],json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']])
def main():
 root=core.REPO/'pcg/results/approved-r040-206-qualified-final-v1';report=core.read(root/'migration-physics.json');rows=[];example=None
 for batch in core.read(core.resolve_artifact(report['batches']['path'])):
  cs=core.read(root/'physics'/(batch['batch']+'.input.json'))['cases'];rs=json.loads(gzip.decompress((root/batch['gzip_path']).read_bytes()))['results']
  for c,r in zip(cs,rs):
   if boundary.observe(c,r):
    assert not r['ok'] and physics.crossing(c,r)['passed'];example=(c,r);rows.append(dict(caseId=c['id'],observation=boundary.observe(c,r)))
 assert len(rows)==6;tests=[]
 for name,mutate in [('other_module',lambda c,r:c['approved_first30'].update(reviewId='999')),('other_version',lambda c,r:c['approved_first30'].update(designVersion='other')),('other_port',lambda c,r:c['migration_probe'].update(portId='exit')),('AIR_probe',lambda c,r:c.update(air_goal_probe={'boundary':[320,854]})),('harm',lambda c,r:r.update(hp=4)),('reset',lambda c,r:r.update(returns=[1])),('unfinished',lambda c,r:r.update(plan_completed=False)),('not_grounded',lambda c,r:r['frames'][-1].update(grounded=False)),('still_moving',lambda c,r:r['frames'][-1].update(real_velocity=[5,0])),('not_at_goal',lambda c,r:r['frames'][-1].update(x=-100)),('no_air_overwrite',lambda c,r:r['frames'][-1].pop('air_exit_complete_frames'))]:
  c,r=copy.deepcopy(example);mutate(c,r);assert boundary.observe(c,r)is None,name;tests.append(name)
 core.write(OUT/'verification/boundary-observer-tests.json',dict(passed=True,actualCorrections=rows,rejectedMutations=tests,source=physics.artifact(boundary.__file__),newPhysicsAttempts=0,newIndependentHoldout=False))
 root=core.REPO/'pcg/results/approved-r040-166-qualified-final-v1';report=core.read(root/'migration-physics.json');original=core.read(core.resolve_artifact(report['counterexamples']['path']));row=next(r for r in original if r['adjudication'].get('invalidates_design'));c,r=load(root,row['evidence']);q=row['causalCheck'];o=row['externalOutcome'];j=row['adjudication'];baseline=core.read(core.resolve_artifact(report['routes'][1]['calibration']['path']))['witness']['result'];good=counter.classify(c,r,q,o,j,baseline);assert not good['invalidates_design'] and not good['accepted_module_solution'];tests=[]
 for name,mutate in [('other_module',lambda c,r,q:c['approved_implementation'].update(reviewId='999')),('other_version',lambda c,r,q:c['approved_implementation'].update(designVersion='other')),('extra_failure',lambda c,r,q:q['reasons'].append('actual_player_harm')),('harm',lambda c,r,q:r.update(hp=4)),('reset',lambda c,r,q:r.update(returns=[1])),('not_counter',lambda c,r,q:c.pop('migration_counter')),('no_actual_outside',lambda c,r,q:r.update(frames=[]))]:
  cc,rr,qq=copy.deepcopy(c),copy.deepcopy(r),copy.deepcopy(q);mutate(cc,rr,qq);assert counter.classify(cc,rr,qq,o,j,baseline)==j,name;tests.append(name)
 core.write(OUT/'verification/counter-scope-tests.json',dict(passed=True,actualCorrection=good,rejectedMutations=tests,source=physics.artifact(counter.__file__),newPhysicsAttempts=0,newIndependentHoldout=False));print('OBSERVERS_ACTUAL_AND_NEGATIVE_PASS',flush=True)
if __name__=='__main__':main()
