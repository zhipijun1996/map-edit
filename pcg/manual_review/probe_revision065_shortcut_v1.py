"""Bounded direct-bottom-to-relay attempts; internal goal, not a new Port."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from .continue_revision065_lift_v1 import OUT
from .run_revision065_lift_v1 import rows,folder_for
from .prepare_review045_v1 import at,axis
def main():
 f=folder_for(rows()[0]);source=core.read(f/'physics-input-cases.json')['cases'][0];eng,_,_=physics._engine(f,'approved-r065-lift-direct-relay-probe-v1',physics.FULL_PROTOCOL);inputs=[];results=[]
 for hold in [18,20,22,24,26,28]:
  for delay in [0,3]:
   c=copy.deepcopy(source);c['id']+=f'-direct-relay-h{hold}-d{delay}';c['goal']=[13,522,14,8];c['max_frames']=1000
   c['control_plan']=copy.deepcopy(source['control_plan'][:3])+at(20,846)+[axis(0),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,direction=[0,1])]+at(20,526);c['module_sha256']=physics.module_hash(c);inputs.append(c)
 for c,raw,e in eng.run(inputs,'bounded-one-shot-direct-relay'):
  moving={v['support_id']for v in raw['frames']} & {'L1','R1','L2','R2'};assert not moving
  reached=any(v['grounded']and v['support_id']=='Platform2'and abs(v['y']-526)<.1 for v in raw['frames']);assert not reached
  results.append(dict(caseId=c['id'],relayReached=reached,minimumPlayerCenterY=min(v['y']for v in raw['frames']),hp=raw['hp'],movingSupportsUsed=sorted(moving),evidence=e))
 core.write(OUT/'verification/direct-relay-probe.json',dict(passed=True,attempts=len(results),rows=results,rawRun=core.relative(eng.out),claim='None of12 full-height jump + one native upward recoil attempts reached relay directly from bottom in the outside lane. Finite test, not a proof against every alternative or enemy-refund route.',source=physics.artifact(__file__),independentHoldout=False,newPort=False));print('R065_DIRECT_RELAY_PROBES',len(results),'none reached',flush=True)
if __name__=='__main__':main()
