from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT
from .finalize_revision059_v1 import folder_for

def main():
 r=next(r for r in rows()if label(r)=='hq05');f=folder_for(r);fixture=core.REPO/'pcg/manual_review/implementation/revision-059-fixtures-v1/hq05-native-guards';cs=core.read(f/'physics-input-cases.json')['cases'][:1]
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/revision059_turret_audit_author_v1.py'
 for name in ['module.mapnote.json','migration.json']:core.write(fixture/name,core.read(f/name))
 core.write(fixture/'cases.json',dict(cases=cs));eng,cs,_=physics._engine(fixture,'approved-r059-hq05-turret-guards-v1',physics.FULL_PROTOCOL)
 for c,raw,e in eng.run(cs,'actual-parent-child-and-rejections'):
  a=raw.get('turret_audit',{});good=raw.get('ok')and raw.get('hp')==5 and all(a.get(k)for k in ['unique_parent_child','child_id_distinct','fixed_direction','duplicate_parent_rejected','self_trigger_rejected','wrong_session_rejected','wrong_target_epoch_rejected','unknown_parent_rejected','original_actor_token_invalidated'])and not a['extra_player_recoil']and not a['ammo_refund']and a['player_original_shots']==a['player_shots_after_checks']and a['player_charges_before']==a['player_charges_after'];proof=dict(passed=bool(good),audit=a,evidence=e,newPhysicsAttempts=1);core.write(eng.out/'guard-check.json',proof);core.write(OUT/'verification/hq05-turret-guards.json',dict(passed=bool(good),proof=physics.artifact(eng.out/'guard-check.json')));print('HQ05_NATIVE_PARENT_CHILD_GUARDS',bool(good))
if __name__=='__main__':main()
