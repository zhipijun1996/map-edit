"""No new physics or holdout. Re-observe the exact counter that left its legal mouth."""
import copy
from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT
from .finalize_revision059_v1 import folder_for
from .complete_revision058_protocol_v1 import actual

def main():
 row=next(r for r in rows()if label(r)=='hq05');root=core.REPO/'pcg/results/approved-r059-hq05-qualified-final-v1';old=core.read(root/'migration-physics.json');counters=core.read(root/'counterexamples.json');baselines={}
 for route in old['routes']:
  cal=core.read(core.resolve_artifact(route['calibration']['path']));w=next(v for v in cal['rows']if v['level']=='clean'and v['purpose']['ok']);_,raw=actual(root,w['evidence']);baselines[route['routeId']]=raw
 corrected=[]
 from pcg.migration.review_counter_scope_v13 import classify
 for oldcounter in counters:
  c,raw=actual(root,oldcounter['evidence']);v=copy.deepcopy(oldcounter);v['adjudication']=classify(c,raw,v['causalCheck'],v['externalOutcome'],v['adjudication'],dict(ok=baselines[c['migration_counter']['originalRouteId']]['ok']));corrected.append(v)
 core.write(root/'counterexamples-reobserved.json',corrected);passed=all(v['passed']for v in old['routes'])and all(v['check']['passed']for v in core.read(root/'boundary-probes.json'))and not any(v['adjudication']['invalidates_design']for v in corrected)
 result=dict(passed=passed,originalFormal=physics.artifact(root/'migration-physics.json'),originalFormalPassed=old['passed'],routes=old['routes'],probes=old['probes'],protocol=old['protocol'],actualAttempts=old['actualAttempts'],correctedCounters=physics.artifact(root/'counterexamples-reobserved.json'),observer=physics.artifact(core.REPO/'pcg/migration/review_counter_scope_v13.py'),newPhysicsAttempts=0,newIndependentHoldout=False,thresholdsUnchanged=True,reason='The only invalidating counter left its selected TOP aperture. Reuse unchanged 058 full-body external-scope rule for exact new approval; preserve the original false report and all raw outcomes.')
 core.write(folder_for(row)/'qualification-reobserved.json',result);core.write(OUT/'verification/hq05-counter-scope-reobserved.json',result);print('HQ05_FULL_V2_REOBSERVED',passed)
if __name__=='__main__':main()
