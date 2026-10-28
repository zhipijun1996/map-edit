"""Read-only accepted events and resource transitions from actual native raw."""
import gzip,json
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/review-029-v1'
def raw_for(n,unqualified=False):
 run=core.REPO/'pcg/results'/('approved-r029-'+n+('-unqualified-delivery-v1'if unqualified else'-delivery-final-v1'))
 row=core.read(run/'canonical.json')['rows'][0];e=row['evidence'];raw=json.loads(gzip.decompress((run/e['output']).read_bytes()))['results'][e['index']]
 return raw,dict(run=core.relative(run),evidence=e,sourceBinding=physics.artifact(run/'source_binding.json'))
r,ref=raw_for('173');frames=r['frames'];hits=[e for e in r['plains']['events']if e.get('type')=='enemy_hit'and e.get('fired_airborne')and e.get('player_airborne')];assert hits
hit=hits[0];at=hit['frame'];before=next(f for f in frames if f['frame']==at);after=next(f for f in frames if f['frame']==at+1);assert before['shot_charges']==0 and after['shot_charges']==1 and not before['grounded']and not after['grounded']
shots=[e for e in r['fired_commands']if e['op']=='shoot'];assert len(shots)==2 and all(not e['grounded']for e in shots)
air_refund=dict(passed=True,source=ref,hit=hit,before=dict(frame=before['frame'],grounded=before['grounded'],shotCharges=before['shot_charges']),after=dict(frame=after['frame'],grounded=after['grounded'],shotCharges=after['shot_charges']),airborneShots=shots)
r,ref=raw_for('163');states=[(f['frame'],f['plains']['bells'][0])for f in r['frames']if f.get('plains',{}).get('bells')];armed=[f for f,b in states if b['sequence_step']==1 and not b['open']];opened=[f for f,b in states if b['open']];assert armed and opened and min(armed)<min(opened)
sequence=dict(passed=True,source=ref,actualArmedClosedFrame=min(armed),actualOpenedAfterSecondFrame=min(opened),approvedReceiverOffset=[0,-96])
r,ref=raw_for('175',True);events=r['plains']['events'];dock=[e for e in events if e.get('type')=='dock_occupied'];mounts=[m for f in r['frames']for m in f.get('review029_mounted_bells',[])];assert any(e['occupied']for e in dock)and any(not e['occupied']for e in dock);assert mounts and all(m['real_receiver_child_of_carrier']and m['receiver_offset']==[0,-46]for m in mounts)
carrier=dict(consumerWiringPassed=True,source=ref,dockEvents=dock,maximumMountedBellOffsetError=0,finalRouteQualification='UNQUALIFIED',finalReason=r.get('reason'),actualPlayerHp=r.get('hp'))
core.write(OUT/'verification/actual-mechanisms.json',dict(passed=True,newPhysicsAttempts=0,newHoldout=False,airRefund173=air_refund,sequence163=sequence,nativeDockAndMountedBell175=carrier,scope='These local causal observations do not upgrade 175 or any untested direction.'))
print('ACTUAL_NATIVE_MECHANISMS_PASS')
