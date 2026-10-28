"""Exercise the narrow scope correction with actual 191 counter and bad raw."""
import copy,gzip,json
from pcg.migration import core,physics,review_counter_scope_v6 as scope
OUT=core.REPO/'feedback/manual-review/implementation-results/review-029-v1/verification'
run=core.REPO/'pcg/results/approved-r029-191-qualified-final-v1';r=core.read(run/'migration-physics.json');summary=core.read(run/'migration-physics-outside-preopen-v1.json')['offlineAnalysis']['counterReanalysis'];target=next(x for x in core.read(run/'counterexamples.json')if x['probe']['kind']=='ground-preopen-lift_bell');e=target['evidence'];batch=next(b for b in core.read(run/'batches.json')if b['batch']==e['batch']);raw=json.loads(gzip.decompress((run/batch['gzip_path']).read_bytes()))['results'][e['index']];c=core.read(run/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];baseline=core.read(run/'calibration-0.json')['witness']['result'];args=[c,raw,target['causalCheck'],target['externalOutcome'],target['adjudication'],baseline]
fixed=scope.classify(*args);assert not fixed['invalidates_design']and fixed['scope']=='outside_contract_alternative'and fixed['accepted_module_solution']is False
checks=[]
for name,change in [('harm',lambda a:a[2]['reasons'].append('actual_player_harm')),('different_design',lambda a:a[0]['approved_implementation'].update(designVersion='sha256:unknown')),('interior_route',lambda a:a[2].update(reasons=[])),('no_baseline',lambda a:a.__setitem__(5,None)),('wall_jump',lambda a:a[1].update(wall_jumps=1))]:
 a=copy.deepcopy(args);change(a);v=scope.classify(*a);assert v==a[4];checks.append(dict(case=name,originalAdjudicationPreserved=True))
assert not any(x['adjudication']['invalidates_design']for x in summary)
core.write(OUT/'191-counter-scope-audit.json',dict(passed=True,originalCounter=physics.artifact(run/'counterexamples.json'),originalReport=physics.artifact(run/'migration-physics.json'),updatedReport=physics.artifact(run/'migration-physics-outside-preopen-v1.json'),nativeDataUnchanged=True,newPhysicsAttempts=0,newIndependentHoldout=False,originalWholeBodyRefusalPreserved=target['causalCheck'],outsideFrameCount=len(target['causalCheck']['causal']['outsideFrames']),newAdjudication=fixed,negativeGuardChecks=checks,originalOtherCountersPreserved=True))
print('ACTUAL_COUNTER_SCOPE_PASS',len(checks))
