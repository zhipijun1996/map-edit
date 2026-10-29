import copy
from pcg.migration import core,physics
from .continue_revision060_v1 import rows,label,OUT
from .finalize_revision060_v1 import folder_for

def main():
 r=next(r for r in rows()if label(r)=='hq07');f=folder_for(r);old=core.REPO/'pcg/results/approved-r060-hq07-qualified-final-v1';fixture=OUT/'fixtures/hq07-counter-v1';assert not fixture.exists();cs=core.read(f/'physics-input-cases.json')['cases'];modified=copy.deepcopy(cs)
 for c in modified:c['generation_rule']['registration_source']='pcg/manual_review/revision060_counter_author_v1.py'
 core.write(fixture/'module.mapnote.json',core.read(f/'module.mapnote.json'));core.write(fixture/'cases.json',dict(cases=modified));eng,cases,authors=physics._engine(fixture,'approved-r060-hq07-counter-completion-v1',physics.FULL_PROTOCOL);baselines={};routes=[]
 for i,c in enumerate(cs):
  cal=core.read(old/f'calibration-{i}.json');hold=old/f'holdout-{i}.json';passed=cal['quality_gate']['status']=='awaiting_human_review'and hold.exists()and core.read(hold)['quality_gate']['status']=='awaiting_human_review';routes.append(dict(routeId=c['route_spec']['id'],passed=passed,calibration=physics.artifact(old/f'calibration-{i}.json'),holdout=physics.artifact(hold)if hold.exists()else'NOT_RUN'))
  if cal.get('witness'):baselines[c['route_spec']['id']]=cal['witness']['result']
 counters=physics._run_counters(eng,cases,authors,'directionless-wait-counter-completion',baselines);core.write(eng.out/'counterexamples.json',counters);boundary=core.read(old/'boundary-probes.json');passed=all(v['passed']for v in routes)and all(v['check']['passed']for v in boundary)and not any(v['adjudication']['invalidates_design']for v in counters)
 core.write(f/'qualification.json',dict(passed=passed,actualAttempts=sum(b['cases']for b in core.read(old/'batches.json'))+eng.sim.cases,originalFailedCounterAttempts=len(core.read(old/'physics/0007-cheap-adaptation-counters.input.json')['cases']),report=physics.artifact(eng.out/'counterexamples.json'),routes=routes,boundary=physics.artifact(old/'boundary-probes.json'),counterDriverRepair=physics.artifact(core.REPO/'pcg/manual_review/runtime/revision060_counter_runner_v1.gd'),originalFailure=physics.artifact(old/'physics/0007-cheap-adaptation-counters.log'),noNewCalibrationOrHoldout=True,noNominalControlChange=True,failedCalibrationStillFails=True));print('hq07 COUNTER_COMPLETION',passed,eng.sim.cases,flush=True)
if __name__=='__main__':main()
