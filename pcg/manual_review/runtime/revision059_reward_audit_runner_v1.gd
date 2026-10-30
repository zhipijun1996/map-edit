extends "revision059_hq_runner_v3.gd"
## Post-route service checks; all travel and reward acquisition use native inputs.
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if result.get('rejected',false):return result
 var pair
 for cell in hq.custom:
  if cell.has_method('export_state'):pair=cell
 var service: SimpleRoomReward=extra.services['reward'];var before:=extra.wallet.balance;var switches: int=pair.open_count
 var replay:=service.claim(context.lifetime.token(),&'workshop:reward');var duplicate:=service.claim(context.lifetime.token(),&'new-duplicate-event');var state: Dictionary=pair.export_state()
 var loaded=load('revision059_reward_pair_v1.gd').new();world.add_child(loaded);loaded.link_id='reward-pair-load';loaded.setup_pair(controller,context.lifetime,Vector2(-4096,-4096),pair.gate_rect,pair.paired_gate_rect,'A',context);loaded.bell_body.collision_layer=0
 var restored: bool=loaded.restore_state(state);var second_restore: bool=loaded.restore_state(state)
 var stale=state.duplicate();stale.run_epoch=int(state.run_epoch)+1
 var stale_pair=load('revision059_reward_pair_v1.gd').new();world.add_child(stale_pair);stale_pair.setup_pair(controller,context.lifetime,Vector2(-4096,-4096),pair.gate_rect,pair.paired_gate_rect,'A',context);stale_pair.bell_body.collision_layer=0
 var rejected_stale: bool=not stale_pair.restore_state(stale)
 result.reward_transaction_audit={'real_claimed':service.claimed,'wallet_before':before,'wallet_after':extra.wallet.balance,'replay_status':int(replay.status),'duplicate_status':int(duplicate.status),'switches_before':switches,'switches_after':pair.open_count,'saved_state':state,'restored':restored,'restored_open_a':loaded.open_a,'restored_open_b':not loaded.open_a,'repeated_restore_rejected':not second_restore,'stale_run_rejected':rejected_stale,'no_new_coins':before==extra.wallet.balance,'no_duplicate_switch':switches==pair.open_count,'real_original_service':true}
 return result
