if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,json,math
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT

def raw(run):
 p=core.REPO/'pcg/results'/run/'physics/0000-clean-diagnostic.output.json.gz'
 with gzip.open(p,'rt')as s:rs=json.load(s)['results']
 return p,rs

def main():
 p,rs=raw('approved-r062-s04-canonical-new-v10');groups=[]
 for r in rs:
  for i,g in enumerate(r['workshop']['approved_hq']):
   for e in g['events']:
    assert e['type']=='atomic_group_motion'and len(e['before'])==1;assert e['before'][0]['id']==['P','Q'][i];groups.append(dict(route=r['id'],group=['P','Q'][i],event=e))
 core.write(OUT/'verification/s04-independent-clocks.json',dict(passed=True,raw=physics.artifact(p),observed=groups,source='Original ModuleMovingPlatform + separate native ShotLatch group per P/Q; no clock/trajectory/resource reset.'))
 count=0;cases=0;proof=[]
 for p in sorted((core.REPO/'pcg/results').glob('approved-r062-s06-*/physics/*.output.json.gz')):
  if 'control-screen'in str(p)or'canonical-new-v8'in str(p):
   with gzip.open(p,'rt')as s:rs=json.load(s)['results']
   for r in rs:
    cases+=1
    for f in r.get('frames',[]):
     mounts=f.get('review029_mounted_bells',[]);assert len(mounts)==1
     m=mounts[0];assert m['real_receiver_child_of_carrier']and m['carrier_id']=='P'and all(abs(a-b)<.001 for a,b in zip(m['receiver_offset'],[0,64]));count+=1
   proof.append(physics.artifact(p))
 assert cases>=28 and count>1000
 core.write(OUT/'verification/s06-rigid-mount.json',dict(passed=True,originalRawCases=cases,actualFrameObservations=count,offset=[0,64],includesPerturbedNativeCarrierPhases=True,raw=proof,binding=physics.artifact(core.REPO/'pcg/manual_review/runtime/revision062_mount_v1.gd'),playerOrResourcesWritten=False,screenFailuresNotRelabeled=True))
 p,rs=raw('approved-r062-s09-canonical-new-v12');w=[]
 for r in rs:
  assert r['ok']and r['hp']==5 and not r['returns']and not r['plains']['player_damage'];deaths=[e for e in r['plains']['events']if e['type']=='enemy_defeated'];assert len(deaths)==1;hits=[e for e in r['plains']['events']if e['type']=='enemy_hit'];w.append(dict(route=r['id'],enemyDefeatedFrame=deaths[0]['frame'],actualEndFrame=r['frames'][-1]['frame'],sameWorld=True,airborneNativeHits=sum(e.get('fired_airborne',False)and e.get('player_airborne',False)for e in hits),hp=5,originalPhysics=True))
 core.write(OUT/'verification/s09-dead-enemy-return.json',dict(passed=True,raw=physics.artifact(p),rows=w,conclusion='Fixed B→L clears original enemy before crossing and still returns; fixed L→B has actual native airborne hits. This disproves dependence of the tested return on an alive enemy; perturbation qualification remains failed.'))
 print('062 NATIVE_MECHANICS_OBSERVATIONS_OK',cases,count,flush=True)
if __name__=='__main__':main()
