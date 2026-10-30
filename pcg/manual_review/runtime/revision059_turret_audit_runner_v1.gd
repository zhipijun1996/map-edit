extends "revision059_hq_runner_v3.gd"
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if result.get('rejected',false):return result
 var turret
 for cell in hq.custom:
  if 'definition'in cell and cell.definition.get('kind','')=='hit_turret':turret=cell
 var accepted: Array=turret.events.filter(func(e: Dictionary):return e.type=='turret_parent_accepted');var emitted: Array=turret.events.filter(func(e: Dictionary):return e.type=='turret_child_emitted')
 var parent: String=accepted[0].parent;var bits:=parent.split(':');var ctx: Dictionary={'event_id':parent,'source_actor_id':controller.motor.get_instance_id(),'session_id':controller.session_id,'shot_id':int(bits[-1]),'target_actor_id':turret.body.get_instance_id(),'target_epoch':turret.health.epoch,'source_faction':&'player'}
 var replay_rejected: bool=not turret._receive(ctx);var wrong:=ctx.duplicate();wrong.source_faction=&'turret_shot';var self_rejected: bool=not turret._receive(wrong);wrong=ctx.duplicate();wrong.session_id=-1;var session_rejected: bool=not turret._receive(wrong);wrong=ctx.duplicate();wrong.target_epoch=-1;var target_rejected: bool=not turret._receive(wrong);wrong=ctx.duplicate();wrong.shot_id=999999;wrong.event_id='unknown-parent';var unknown_rejected: bool=not turret._receive(wrong)
 var before_shots: int=result.shots;var before_charges: int=controller.action_resources.shot_charges;var old_token: DemoToken=context.lifetime.token();context.lifetime.invalidate_actor();var expired_token_rejected: bool=not context.lifetime.accepts(old_token)
 result.turret_audit={'real_accepted_parent_count':accepted.size(),'real_emitted_child_count':emitted.size(),'unique_parent_child':emitted.size()==1 and accepted.size()==1 and emitted[0].parent==accepted[0].parent,'child_id_distinct':int(emitted[0].child)!=int(bits[-1]),'fixed_direction':emitted[0].direction==data.approved_hq_cells[0].direction,'extra_player_recoil':emitted[0].extra_recoil,'ammo_refund':emitted[0].ammo_refund,'player_original_shots':before_shots,'player_shots_after_checks':counters.shots,'player_charges_before':before_charges,'player_charges_after':controller.action_resources.shot_charges,'duplicate_parent_rejected':replay_rejected,'self_trigger_rejected':self_rejected,'wrong_session_rejected':session_rejected,'wrong_target_epoch_rejected':target_rejected,'unknown_parent_rejected':unknown_rejected,'original_actor_token_invalidated':expired_token_rejected}
 return result
