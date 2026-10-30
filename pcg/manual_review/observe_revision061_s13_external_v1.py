"""Read-only whole-body entry / real reward / exit observation of one native run."""
import copy,gzip,json
from pcg.migration import core,physics
from .continue_revision061_v1 import OUT

def observe(c,r):
 q=physics.crossing(c,r)
 if not(r.get('ok')and r.get('hp')==5 and not r.get('returns')and not r.get('hazard_contacts')and q['stableExit']and q['healthy']and q['noReset']and q['bodyPassedBothSides']and q['requiredWorldOutcomeSatisfied']and not q['apertureViolationFrames']):return None
 fs=r['frames'];reward=next((f['frame']for f in fs if f.get('original_pickups',{}).get('coins',0)>=4),None)
 entered=next((f['frame']for f in fs if f['x']>=12),None)
 if reward is None or entered is None or reward<=entered:return None
 exited=next((f['frame']for f in fs if f['frame']>reward and f['x']<=-12),None)
 if exited is None or not fs[0]['x']<=-12 or fs[-1]['x']>-12:return None
 if not all(f['hp']==5 and not f.get('returns')for f in fs):return None
 if not any(e.get('type')=='chest_claim'and e.get('accepted')and e.get('id')=='reward'for e in r.get('workshop',{}).get('events',[])):return None
 return dict(passed=True,wholeBodyEnteredFrame=entered,realRewardFrame=reward,wholeBodyExitedFrame=exited,noIntermediateReset=True,body=[24,36],originalSingleEgressObserver=q,observerDifference='A full same-port loop begins outside, enters, earns reward, then exits. The generic egress-only initial-direction check is not its contract.',rawUnchanged=True,newPhysicsAttempts=0,newIndependentHoldout=False)
def main():
 run=core.REPO/'pcg/results/approved-r061-s13-same-world-external-v1';p=run/'physics/0000-full-external-same-world-return.output.json.gz';c=core.read(run/'physics/0000-full-external-same-world-return.input.json')['cases'][0];r=json.loads(gzip.decompress(p.read_bytes()))['results'][0];q=observe(c,r);assert q
 negatives=[]
 for kind in ['no_reward','player_harm','reset','no_external_start','no_external_return']:
  v=copy.deepcopy(r)
  if kind=='no_reward':v['workshop']['events']=[]
  if kind=='player_harm':v['hp']=4
  if kind=='reset':v['returns']=[dict(frame=1)]
  if kind=='no_external_start':v['frames'][0]['x']=24
  if kind=='no_external_return':v['frames'][-1]['x']=24
  assert observe(c,v)is None;negatives.append(dict(kind=kind,rejected=True,syntheticObserverGuardTest=True,notGodotPhysicsEvidence=True))
 core.write(OUT/'fixtures/s13-external-loop-v1/report-reobserved.json',dict(passed=True,observation=q,source=physics.artifact(p),originalFixture=physics.artifact(OUT/'fixtures/s13-external-loop-v1/cases.json'),observerSource=physics.artifact(__file__),negativeGuardTests=negatives,originalRawOk=r['ok'],originalSingleEgressFalseRetained=True,coins=4,fixtureNeighborNeverExported=True));print('S13_EXTERNAL_SAME_WORLD_LOOP_READONLY_PASS',q['wholeBodyEnteredFrame'],q['realRewardFrame'],q['wholeBodyExitedFrame'])
if __name__=='__main__':main()
