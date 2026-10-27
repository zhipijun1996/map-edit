extends SceneTree
## Real service-boundary negatives; never modifies game resources or tuning.
const PLAYER=preload("res://scenes/player/player.tscn")
const CAPS=preload("res://capability_adapter.gd")
const LIFECYCLE=preload("res://plains_lifecycle.gd")
func _initialize() -> void:
	_run.call_deferred()
func _run() -> void:
	var args:=OS.get_cmdline_user_args()
	if args.size()<2:quit(2);return
	var folder:=str(args[0]);var receipt_path:=str(args[1])
	var world:=Node2D.new();world.process_mode=Node.PROCESS_MODE_DISABLED;root.add_child(world)
	var packed: PackedScene=load(folder.path_join("module.tscn"));var package=packed.instantiate();world.add_child(package)
	var motor: PlayerMotor=PLAYER.instantiate();motor.get_node("PlayerFeedback").free();world.add_child(motor)
	var actor:=motor.get_node("Controller") as PlayerController;actor.enable_shot_energy();CAPS.apply(actor,["move","jump","shot_recoil"])
	var lifetime:=DemoLifetime.new();var policy:=FrameDamagePolicy.new();policy.lifetime=lifetime;world.add_child(policy)
	policy.register_target(&"player",actor.actor_resources.health,true);policy.register_player_controller(actor)
	var wallet:=RunWallet.new();var meta:=MetaProgression.new()
	var missing_meta: Dictionary=package.bind_player(actor,policy,lifetime,wallet)
	var wrong_profile: Dictionary=package.bind_player(actor,policy,lifetime,wallet,null,"negative-profile",meta)
	var initialized:=FoundryCatalog.apply_profile(actor,"air_chain")
	var initial:=actor.action_resources.shot_charges
	var consumed_one:=actor.action_resources.try_consume_shot(false)
	var consumed_two:=actor.action_resources.try_consume_shot(false)
	var before:=actor.action_resources.shot_charges
	var bound: Dictionary=package.bind_player(actor,policy,lifetime,wallet,null,"native-boundary-no-refill",meta)
	var after:=actor.action_resources.shot_charges
	var good: bool=initialized and initial==4 and consumed_one and consumed_two and before==2 and after==2 and bound.get("ok",false) and not missing_meta.get("ok",true) and missing_meta.get("reason")=="explicit_meta_required_for_notes" and not wrong_profile.get("ok",true) and wrong_profile.get("reason")=="existing_actor_native_profile_mismatch"
	var receipt:={"schema":"pcg/native-package-service-boundary/v1","passed":good,"missingMeta":missing_meta,"wrongProfile":wrong_profile,"nativeProfileInitializedBeforeBind":initialized,"initialShotCharges":initial,"realShotsConsumed":int(consumed_one)+int(consumed_two),"beforeBindShotCharges":before,"afterBindShotCharges":after,"bound":bound,"wallet":wallet.balance,"notes":meta.snapshot().notes,"originalActionResources":"try_consume_shot(false)","module_profile_granted":false,"module_resources_reset":false,"script_sha256":FileAccess.get_sha256(get_script().resource_path),"package_manifest_sha256":FileAccess.get_sha256(folder.path_join("godot-package.json"))}
	var file:=FileAccess.open(receipt_path,FileAccess.WRITE);file.store_string(JSON.stringify(receipt));file.close();print("NATIVE_BINDING_SMOKE ",JSON.stringify(receipt))
	await LIFECYCLE.dispose(self,world,actor)
	quit(0 if good else 4)
