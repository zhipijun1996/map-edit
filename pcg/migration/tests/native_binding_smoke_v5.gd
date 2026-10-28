extends SceneTree
const PLAYER=preload("res://scenes/player/player.tscn")
const LIFE=preload("res://plains_lifecycle.gd")
func _initialize() -> void:_run.call_deferred()
func _run() -> void:
	var args:=OS.get_cmdline_user_args();var folder:=str(args[0]);var out:=str(args[1]);var root_path:=str(args[2])
	var profile_script=load(root_path.path_join("pcg/migration/runtime/native_profile_v5.gd"))
	var world:=Node2D.new();world.process_mode=Node.PROCESS_MODE_DISABLED;root.add_child(world)
	var package=load(folder.path_join("module.tscn")).instantiate();world.add_child(package)
	var motor: PlayerMotor=PLAYER.instantiate();motor.get_node("PlayerFeedback").free();world.add_child(motor)
	var actor:=motor.get_node("Controller") as PlayerController;actor.enable_shot_energy()
	var lifetime:=DemoLifetime.new();var policy:=FrameDamagePolicy.new();policy.lifetime=lifetime;world.add_child(policy)
	policy.register_target(&"player",actor.actor_resources.health,true);policy.register_player_controller(actor)
	var wallet:=RunWallet.new();var meta:=MetaProgression.new();var region:=PlainsRegionState.new()
	var missing: Dictionary=package.bind_player(actor,policy,lifetime,wallet,null,"same-instance",null,region)
	var wrong: Dictionary=package.bind_player(actor,policy,lifetime,wallet,null,"same-instance",meta,region)
	var profile: Dictionary=package.content.original_tuning_profile;var fixture: Dictionary=package.content.original_fixture_profile
	var initialized: Dictionary=profile_script.new().initialize_once(actor,profile,fixture)
	var consumed:=actor.action_resources.try_consume_shot(false);var before:=actor.action_resources.shot_charges
	var bound: Dictionary=package.bind_player(actor,policy,lifetime,wallet,null,"same-instance",meta,region);var after:=actor.action_resources.shot_charges
	var good: bool=not missing.ok and not wrong.ok and initialized.ok and consumed and before==1 and after==1 and bound.ok and wallet.balance==0 and meta.snapshot().notes==0
	var receipt:={"schema":"pcg/native-v5-actual-module-binding/v1","passed":good,"missingMeta":missing,"wrongIdentity":wrong,"initialized":initialized,"beforeBind":before,"afterBind":after,"bound":bound,"coins":wallet.balance,"notes":meta.snapshot().notes,"sourceSHA":FileAccess.get_sha256(get_script().resource_path),"manifestSHA":FileAccess.get_sha256(folder.path_join("godot-package.json")),"resources_reset_at_seam":false}
	var file:=FileAccess.open(out,FileAccess.WRITE);file.store_string(JSON.stringify(receipt));file.close();print("NATIVE_BINDING_V5 ",good)
	await LIFE.dispose(self,world,actor);quit(0 if good else 4)
