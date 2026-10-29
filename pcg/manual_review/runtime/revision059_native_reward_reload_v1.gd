extends "../../migration/runtime/package_demo_revision053_v1.gd"
var audited:=false
func _ready() -> void:
 var args:=OS.get_cmdline_user_args()
 for i: int in args.size():
  if args[i]=='--native-scene' and i+1<args.size():scene_file_path=args[i+1]
 super._ready()
func _finish() -> void:
 if audited:return
 audited=true;context.freeze();world.process_mode=Node.PROCESS_MODE_DISABLED
 var state: Dictionary=package.export_saved_state();var balance: int=wallet.balance
 var packed: PackedScene=load(scene_file_path.get_base_dir().path_join('module.tscn'));var loaded=packed.instantiate();world.add_child(loaded)
 var supplied: bool=loaded.provide_saved_state(state);var bound: Dictionary=loaded.bind_player(controller,context.policy,context.lifetime,wallet,null,'reward-reentry-fixture');loaded.capture()
 var restored: Dictionary=loaded.export_saved_state();var no_reward_service: bool=loaded.rewards.services.is_empty();var second_load: bool=loaded.provide_saved_state(state)
 var stale: Dictionary=state.duplicate();stale.run_epoch=int(state.run_epoch)+1;var other=packed.instantiate();world.add_child(other);var stale_supplied: bool=other.provide_saved_state(stale);var stale_binding: Dictionary=other.bind_player(controller,context.policy,context.lifetime,wallet,null,'reward-wrong-run-fixture')
 var passed: bool=state.get('claimed',false) and state.get('swapped',false) and supplied and bound.ok and restored==state and no_reward_service and not second_load and stale_supplied and not stale_binding.ok and wallet.balance==balance and balance==4
 var result: Dictionary={'passed':passed,'real_successful_reward_state':state,'restored_state':restored,'bound':bound,'no_new_reward_service':no_reward_service,'no_repeated_load':not second_load,'wrong_run_rejected':not stale_binding.ok,'wallet_before':balance,'wallet_after':wallet.balance,'same_run_reentry':true,'new_physics_attempts':1,'actor_or_resource_writes':false}
 if not output_path.is_empty():var file:=FileAccess.open(output_path+'.persistence.json',FileAccess.WRITE);file.store_string(JSON.stringify(result));file.close()
 if not passed:setup_error='native_reward_reentry_failed'
 super._finish()
