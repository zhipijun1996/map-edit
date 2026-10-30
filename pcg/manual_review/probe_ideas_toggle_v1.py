"""Actual original ShotLatch start/pause/resume, without editing the loop."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core, physics
from .new_ideas_v1 import rows, label
from .finalize_ideas_v1 import folder_for
from .prepare_review045_v1 import at
from pcg.prototype.workshop.rules import cmd

def main():
    row=next(r for r in rows() if label(r)=='orbit')
    eng,cases,_=physics._engine(folder_for(row),'approved-ideas-orbit-toggle-cell-v1',physics.FULL_PROTOCOL)
    c=physics.fresh(cases[0],'real-toggle-cell')
    c['goal']=[-5000,-5000,1,1]
    c['control_plan']=at(84,334)
    for _ in range(4):
        c['control_plan'] += [dict(op='shoot',aim_cell=dict(kind='bell',id='bell'),trigger=dict(after=4,state='grounded_shot_ready',timeout=180))]+at(84,334)+[cmd('wait',60)]
    c['control_plan'] += [cmd('wait',150)]
    c['max_frames']=600
    output=[]
    for case,raw,evidence in eng.run([c],'real-bell-pause-resume'):
        toggles=[e for e in raw['workshop']['events'] if e['type']=='carrier_toggle']
        poses=[f['idea_loops'][0] for f in raw['frames']]
        pauses=[(a,b) for a,b in zip(poses,poses[1:]) if not a['running'] and not b['running']]
        movement=max((abs(a['clock']-b['clock']) for a,b in pauses),default=999)
        check=dict(toggles=toggles,pausedClockDelta=movement,maximumPoseError=max(p['expected_error']for p in poses),hp=raw['hp'],worldReturns=raw['returns'])
        check['passed']=bool([e['running']for e in toggles]==[True,False,True,False] and movement==0 and check['maximumPoseError']<.002 and raw['hp']==5 and not raw['returns'])
        output.append(dict(check=check,evidence=evidence));print(check,flush=True)
    core.write(eng.out/'toggle-checks.json',dict(simulationTrials=1,rows=output,independentHoldout=False))
if __name__=='__main__':main()
