"""Classify from existing calibration; do not select or tune on held-out trials."""
from pcg.migration import core,physics
from .continue_revision062_v1 import rows,label,AUTH
from .finalize_revision060_v1 import folder_for as f60
from .finalize_revision061_v1 import folder_for as f61
SOURCES={'hq01':('060','approved-r060-hq01-qualified-final-v1-same-input-resume-v1'),'hq03':('060','approved-r060-hq03-qualified-final-v1'),'hq07':('060','approved-r060-hq07-qualified-final-v1'),'rs10':('061','approved-r061-s10-qualified-final-v1'),'rs12':('061','approved-r061-s12-qualified-final-v1')}
PROPOSALS={'hq01':'Correct close Q→P walk-off input target; stable grounded left recoil; align safe top takeoff.','hq03':'Keep right-side native combat guard at368 below eave; actual airborne shots and hit refunds; no enemy/terrain change.','hq07':'Use actual shot height as the shoot trigger, eliminating extra delayed wait→shoot reset; retain same recoil/bridge/anti-crush.','rs10':'Freeze takeoff axes and add existing-ledge position margin before left/right recoil; keep eave/saw/ports.','rs12':'Height-driven right boarding recoil above highest Q; safe top takeoff from Q-left; preserve independent clocks.'}
def main():
 assert not(AUTH/'failure-triage.json').exists();records=[]
 for r in rows():
  n=label(r)
  if n not in SOURCES:continue
  version,run=SOURCES[n];f=(f60 if version=='060'else f61)(r);cases=core.read(f/'physics-input-cases.json')['cases'];evidence=[]
  for i,c in enumerate(cases):
   cal=core.REPO/'pcg/results'/run/f'calibration-{i}.json';d=core.read(cal)
   if d['quality_gate']['status']=='awaiting_human_review':continue
   failed=next(v for v in d['rows']if not v['purpose']['ok']);e=failed['evidence'];inp=core.REPO/'pcg/results'/run/'physics'/(e['batch']+'.input.json');trial=core.read(inp)['cases'][e['index']];evidence.append(dict(route=c['route_spec']['id'],calibration=physics.artifact(cal),failedCheck=failed['purpose'],input=trial,inputArtifact=physics.artifact(inp),evidence=e))
  target=AUTH/'prior-calibration'/(n+'.json');core.write(target,dict(sourceModule=physics.artifact(f/'module.mapnote.json'),physicsCases=physics.artifact(f/'physics-input-cases.json'),rows=evidence,assessment='Control/driver failure observed; no proven geometric impossibility.',proposal=PROPOSALS[n]));records.append(dict(name=n,failedCalibrationRoutes=len(evidence),source=physics.artifact(target)))
 core.write(AUTH/'failure-triage.json',dict(rows=records,source='actual calibration raw, not held-out seed selection',HQ09='Separate real initial TOP thorn conflict; awaiting specific permission/design choice'));print('CALIBRATION_TRIAGE',[(r['name'],r['failedCalibrationRoutes'])for r in records])
if __name__=='__main__':main()
