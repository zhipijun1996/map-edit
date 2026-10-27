extends SceneTree
const PLAYER=preload("res://scenes/player/player.tscn")
const LIFE=preload("res://plains_lifecycle.gd")
var results: Array=[]
func _initialize() -> void:_run.call_deferred()
func _run() -> void:
	var args:=OS.get_cmdline_user_args();var root_path:=str(args[0]);var output:=str(args[1])
	var profile_script=load(root_path.path_join("pcg/migration/runtime/native_profile_v5.gd"))
	var chest_script=load(root_path.path_join("pcg/migration/runtime/original_region_chests_v5.gd"))
	var specs: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(args[2])))
	var world:=Node2D.new();world.process_mode=Node.PROCESS_MODE_DISABLED;root.add_child(world)
	var motor: PlayerMotor=PLAYER.instantiate();motor.get_node("PlayerFeedback").free();world.add_child(motor)
	var actor:=motor.get_node("Controller") as PlayerController;actor.enable_shot_energy()
	var provider=profile_script.new();var initial: Dictionary=provider.initialize_once(actor,specs.profile,specs.fixture)
	var consumed: bool=actor.action_resources.try_consume_shot(false);var before:=actor.action_resources.shot_charges
	var verified: Dictionary=provider.verify_existing(actor,specs.profile,specs.fixture)
	var again: Dictionary=provider.initialize_once(actor,specs.profile,specs.fixture)
	var forged: Dictionary=specs.fixture.duplicate(true);forged.source.sha256="0".repeat(64)
	var forged_result: Dictionary=provider.verify_existing(actor,specs.profile,forged)
	results.append({"kind":"exact_profile","ok":initial.get("ok",false) and consumed and before==int(initial.get("shots",0))-1 and verified.get("ok",false) and actor.action_resources.shot_charges==before and not again.get("ok",true) and not forged_result.get("ok",true),"initial":initial,"before_bind":before,"verified":verified,"reinitialize":again,"forged_source":forged_result})
	var lifetime:=DemoLifetime.new();var scope:=Node.new();scope.set_meta("unused",true)
	# Reuse the actual existing damage/context lifetime API; this native consumer
	# test exercises transactions only, not a substitute movement simulation.
	var scope_script=load(root_path.path_join("pcg/migration/tests/native_services_scope_v5.gd"));scope.free();scope=scope_script.new();scope.lifetime=lifetime;world.add_child(scope)
	var wallet:=RunWallet.new();var meta:=MetaProgression.new();var state:=PlainsRegionState.new()
	var data: Array=[{"id":"cache","position":[0,0],"tier":"high","items":[],"coins":6,"reward_mode":"resources","resources":[{"kind":"coin","amount":6},{"kind":"note","amount":2}]}]
	var chest=chest_script.new();world.add_child(chest);var bound: Dictionary=chest.setup(data,world,actor,scope,wallet,meta,state,"coin-instance")
	chest.request_interaction();chest.capture();var opened: Dictionary=chest.snapshot()
	chest.request_choice("dash");chest.capture();var invalid: Dictionary=chest.snapshot()
	chest.request_choice("coin");chest.capture();var coin: Dictionary=chest.snapshot()
	chest.request_interaction();chest.request_choice("note");chest.capture();var repeated: Dictionary=chest.snapshot()
	results.append({"kind":"original_region_coin_choice","ok":bound.ok and opened.modal_open and opened.coins==0 and opened.notes==0 and invalid.modal_open and invalid.coins==0 and coin.coins==6 and coin.notes==0 and coin.chests[0].claimed and repeated.coins==6 and repeated.notes==0,"open":opened,"invalid":invalid,"chosen":coin,"repeated":repeated})
	var note=chest_script.new();world.add_child(note);note.setup(data,world,actor,scope,wallet,meta,state,"note-instance");note.request_interaction();note.request_choice("note");note.capture();var chosen_note: Dictionary=note.snapshot()
	results.append({"kind":"original_region_note_choice","ok":chosen_note.coins==6 and chosen_note.notes==2 and chosen_note.chests[0].claimed and not chosen_note.modal_open,"result":chosen_note})
	var reload_chest=chest_script.new();world.add_child(reload_chest);reload_chest.setup(data,world,actor,scope,wallet,meta,state,"coin-instance");reload_chest.request_interaction();reload_chest.request_choice("coin");reload_chest.capture();var reload_state: Dictionary=reload_chest.snapshot()
	results.append({"kind":"shared_state_reload_does_not_farm","ok":reload_state.coins==6 and reload_state.notes==2 and reload_state.chests[0].claimed and not reload_state.modal_open,"result":reload_state})
	var far=chest_script.new();world.add_child(far);var far_data: Array=data.duplicate(true);far_data[0].position=[80,0];far.setup(far_data,world,actor,scope,wallet,meta,state,"boundary-instance");far.request_interaction();far.request_choice("coin");far.capture();var far_state: Dictionary=far.snapshot()
	results.append({"kind":"strict_native_80px_radius","ok":not far_state.modal_open and not far_state.chests[0].claimed and far_state.coins==6 and far_state.notes==2,"result":far_state})
	var missing=chest_script.new();world.add_child(missing);var missing_result: Dictionary=missing.setup(data,world,actor,scope,wallet,null,state,"missing-meta")
	results.append({"kind":"explicit_shared_meta_required","ok":not missing_result.ok,"result":missing_result})
	var stale=chest_script.new();world.add_child(stale);stale.setup(data,world,actor,scope,wallet,meta,state,"stale-token");stale.request_interaction();stale.capture();lifetime.invalidate_actor();stale.request_choice("coin");stale.capture();var stale_state: Dictionary=stale.snapshot()
	results.append({"kind":"stale_lifetime_token_rejects_claim","ok":not stale_state.chests[0].claimed and stale_state.coins==6 and stale_state.notes==2,"result":stale_state})
	paused=false
	var good:=true
	for result: Dictionary in results:good=good and result.ok
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify({"schema":"pcg/native-services-v5-smoke/v1","passed":good,"results":results,"source_sha256":FileAccess.get_sha256(get_script().resource_path),"profile_helper_sha256":FileAccess.get_sha256(profile_script.resource_path),"region_helper_sha256":FileAccess.get_sha256(chest_script.resource_path),"engine_sha256":FileAccess.get_sha256(OS.get_executable_path()),"new_physics_implementation":false}));file.close()
	print("NATIVE_SERVICES_V5 ",good)
	await LIFE.dispose(self,world,actor)
	quit(0 if good else 4)
