"""Positive and fail-closed negatives against unchanged original196 raw."""
import copy,gzip,json
from pcg.migration import core,physics,review_counter_scope_v11 as scope
from .continue_revision053_v1 import OUT

def main():
 p=core.REPO/'pcg/results/approved-r053-196-qualified-final-v1';report=core.read(p/'migration-physics.json');row=next(v for v in core.read(p/'counterexamples.json')if v['adjudication']['invalidates_design']);e=row['evidence'];raw=json.loads(gzip.decompress((p/e['output']).read_bytes()))['results'][e['index']];case=core.read(p/'physics'/(e['batch']+'.input.json'))['cases'][e['index']]
 calibration=core.read(core.resolve_artifact(report['routes'][0]['calibration']['path']));w=next(v for v in calibration['rows']if v['level']=='clean');ew=w['evidence'];baseline=json.loads(gzip.decompress((p/ew['output']).read_bytes()))['results'][ew['index']]
 args=[case,raw,row['causalCheck'],row['externalOutcome'],row['adjudication'],baseline];positive=scope.classify(*args);assert not positive['invalidates_design']and not positive['accepted_module_solution'];tests=[]
 for name in ['different-version','harm','reset','another-refusal','no-outside','failed-goal','failed-baseline','enabled-wall-jump']:
  c,r,ch,o,j,b=copy.deepcopy(args)
  if name=='different-version':c['approved_implementation']['designVersion']='wrong'
  elif name=='harm':r['hp']=4
  elif name=='reset':r['returns']=1
  elif name=='another-refusal':ch['reasons'].append('real_hook_sequence_missing')
  elif name=='no-outside':ch['causal']['outsideFrames']=[]
  elif name=='failed-goal':o['ok']=False
  elif name=='failed-baseline':b['ok']=False
  else:r['wall_jumps']=1
  result=scope.classify(c,r,ch,o,j,b);assert result==j;tests.append(dict(name=name,retainsOriginalRefusal=True))
 core.write(OUT/'verification/counter-measurement-regression.json',dict(passed=True,positive=positive,negativeTests=tests,originalCounter=physics.artifact(p/'counterexamples.json'),source=physics.artifact(scope.__file__),newPhysicsAttempts=0,newIndependentHoldout=False,rawUnchanged=True,reason='Apply the existing external-space scoping rule to the newly user-revised196 design identity; never admit this shortcut as an internal route.'))
 print('COUNTER_MEASUREMENT_POSITIVE_AND_8_FAIL_CLOSED_NEGATIVES_PASS')
if __name__=='__main__':main()
