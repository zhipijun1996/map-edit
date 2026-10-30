import copy
from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT
from .finalize_revision059_v1 import folder_for
from .prepare_review045_v1 import at,end

def main():
 r=next(r for r in rows()if label(r)=='hq04');f=folder_for(r);cs=core.read(f/'physics-input-cases.json')['cases'];c=physics.fresh(cs[0],'same-world-exterior-reward-loop');doc=core.read(f/'module.mapnote.json');port=doc['generationContract']['ports'][0];neighbor=physics.exterior_floor(c,port);c['spawn']=[-48,334];c['control_plan']=at(24,334)+c['control_plan']+end(-48,334);c['goal']=[-52,331,8,6];c['generation_rule']['registration_source']='pcg/manual_review/revision059_reward_audit_author_v1.py';fixture=core.REPO/'pcg/manual_review/implementation/revision-059-fixtures-v1/hq04-same-world-loop'
 for name in ['module.mapnote.json','migration.json']:core.write(fixture/name,core.read(f/name))
 core.write(fixture/'cases.json',dict(cases=[c]));eng,cs,_=physics._engine(fixture,'approved-r059-hq04-same-world-loop-v1',physics.FULL_PROTOCOL)
 for c,raw,e in eng.run(cs,'external-L-reward-external-L-no-reset'):
  fs=raw.get('frames',[]);crossings=[]
  for a,b in zip(fs,fs[1:]):
   if (a['x']<0<=b['x'])or(a['x']>0>=b['x']):crossings.append(dict(frame=b['frame'],ingress=b['x']>a['x'],fullBodyWithin64pxMouth=all(abs(v['y']-320)+18<=32.05 for v in [a,b])))
  audit=raw.get('reward_transaction_audit',{});passed=raw.get('ok')and raw.get('hp')==5 and not raw.get('returns')and len(crossings)==2 and crossings[0]['ingress']and not crossings[1]['ingress']and all(v['fullBodyWithin64pxMouth']for v in crossings)and audit.get('replay_status')==1 and audit.get('duplicate_status')==5 and audit.get('switches_before')==1 and all(audit.get(k)for k in ['real_claimed','restored','restored_open_b','repeated_restore_rejected','stale_run_rejected','no_new_coins','no_duplicate_switch'])
  proof=dict(passed=bool(passed),sameWorld=True,noIntermediateReset=True,neighbor=neighbor,crossings=crossings,transactionAudit=audit,evidence=e,newPhysicsAttempts=1,scope='actual original reward in one exterior-L/interior/reward/low-return/exterior-L traversal; original service replay and adapter save/load tests');core.write(eng.out/'loop-check.json',proof);core.write(OUT/'verification/hq04-reward-loop.json',dict(passed=bool(passed),proof=physics.artifact(eng.out/'loop-check.json')));print('HQ04_SINGLE_WORLD_REWARD_LOOP',bool(passed))
if __name__=='__main__':main()
