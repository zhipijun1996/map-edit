"""Full ascent with a missed boarding, ten-second relay wait and native reward."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics,godot_package,revision053_runtime_v1 as backend
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from pcg.prototype.workshop.rules import cmd
from .continue_revision065_lift_v1 import OUT,ID
from .run_revision065_lift_v1 import folder_for,rows
from .prepare_review045_v1 import at,axis
def main():
 row=rows()[0];source=folder_for(row);f=OUT/'fixtures/missed-boarding-wait-chest-v1';assert not f.exists();doc=core.read(source/'module.mapnote.json');case=core.read(source/'physics-input-cases.json')['cases'][0];case['id']+='-relay-miss-wait-chest';p=case['control_plan']
 j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='relay065_choose_upper')
 # Remain in the outside lane on a real full jump, deliberately missing L2.
 # Settle back on the same relay, wait600 native frames, then retry normally.
 p[j:j]=[axis(0),cmd('jump'),cmd('jump_release',24)]+at(20,526)+[cmd('wait',600)]
 j=next(i for i,v in enumerate(p)if v['op']=='shoot'and v.get('aim_cell',{}).get('id')=='top-exit-bell');p[j:j]=at(208,46)+at(192,46);case.update(required_rewards=['reward'],expected_reward=4)
 doc=godot_package.bind_case_behavior(doc,[case]);core.write(f/'module.mapnote.json',doc);core.write(f/'cases.json',dict(cases=[case]));core.write(f/'physics-input-cases.json',dict(cases=[case]));core.write(f/'migration.json',core.read(source/'migration.json'));core.write(f/'parameters.json',dict(original=physics.artifact(source/'module.mapnote.json'),changes='Only native input demonstration: miss one upper boarding, return to relay, wait600 frames, retry and collect optional chest.',ownedGeometryChanged=False))
 eng,cs,authors=physics._engine(f,'approved-r065-lift-relay-recovery-chest-v1',physics.FULL_PROTOCOL);recordings=[]
 for c,raw,e in eng.run([physics.fresh(case,'relay-recovery-chest')],'same-world-relay-recovery'):
  q=checked_purpose(authors[0],c,raw);core.write(eng.out/'check.json',dict(passed=q['ok'],check=q,evidence=e));assert q['ok'],q
  frames=raw['frames'];ground=[v['frame']for v in frames if v['grounded']and v['support_id']=='Platform2'and abs(v['y']-526)<.1];assert len(ground)>=600
  gaps=[(a,b)for a,b in zip(ground,ground[1:])if b-a>20];assert gaps
  assert raw['hp']==5 and not raw['returns']and raw['workshop']['coins']==4 and any(v.get('type')=='chest_claim'and v.get('accepted')and v.get('amount')==4 for v in raw['workshop']['events'])
  core.write(f/'recovery-reward-evidence.json',dict(passed=True,sameWorld=True,missedBoarding=True,relayDepartureReturnFramePairs=gaps,actualRelayGroundFrames=len(ground),minimumExplicitWaitFrames=600,actualCoins=4,originalRewardConsumer=True,worldResets=0,actorOrResourceWrites=False,raw=physics.artifact(eng.out/e['output']),source=physics.artifact(__file__),formalQualification=False));recordings.append(physics._recording(c,raw))
 core.write(f/'playback-cases.json',dict(cases=recordings));backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=ID+'-relay-recovery-chest');result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);assert result['passed'];print('R065_NATIVE_RELAY_RECOVERY_WAIT_AND_CHEST_PASS',flush=True)
if __name__=='__main__':main()
