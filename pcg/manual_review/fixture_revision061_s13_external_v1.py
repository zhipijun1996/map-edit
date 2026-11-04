if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from .continue_revision061_v1 import rows,label,OUT
from .finalize_revision061_v1 import folder_for

def main():
 row=next(r for r in rows()if label(r)=='s13');f=folder_for(row);doc=core.read(f/'module.mapnote.json');base=core.read(f/'physics-input-cases.json')['cases'][0];entry=physics.continuous_entry(base,doc);exit=physics.continuous_exit(base,doc);c=copy.deepcopy(exit);c.update(id='r061-s13-external-L-reward-external-L',spawn=entry['spawn'],entry_port=entry['spawn'],max_frames=3600);c['control_plan']=entry['control_plan']+c['control_plan'];c['migration_probe'].update(sameWorldExternalEntry=True,noIntermediateReset=True,requiredRealReward=True);out=OUT/'fixtures/s13-external-loop-v1';assert not out.exists();core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=[c]));eng,cs,authors=physics._engine(out,'approved-r061-s13-same-world-external-v1',physics.FULL_PROTOCOL);actual=next(eng.run(cs,'full-external-same-world-return'));c,raw,e=actual;cross=physics.crossing(c,raw);assert cross['passed']and raw['hp']==5 and not raw['returns']and raw['original_pickups']['coins']>=4
 core.write(out/'report.json',dict(passed=True,sourceModule=physics.artifact(f/'module.mapnote.json'),evidence=e,rawDirectory=core.relative(eng.out),crossing=cross,coins=raw['original_pickups']['coins'],originalPickupEvents=raw['original_pickups']['events'],actualInputs=raw['fired_commands'],externalEntry=entry['spawn'],externalExitGoal=c['goal'],noIntermediateReset=True,nativeOriginalPhysics=True,fixtureNeighborNeverExported=True,newIndependentHoldout=False));print('S13_REAL_EXTERNAL_SAME_WORLD_REWARD_RETURN_PASS',raw['ticks'],flush=True)
if __name__=='__main__':main()
