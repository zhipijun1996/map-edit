extends Node2D
## Integration fixture: two translated instances, two external original players,
## independent original damage policies and one shared real RunWallet.
const PLAYER=preload("res://scenes/player/player.tscn")
const LIFECYCLE=preload("res://plains_lifecycle.gd")
var world: Node2D
var wallet:=RunWallet.new()
var packages: Array=[]
var controllers: Array[PlayerController]=[]
var policies: Array[FrameDamagePolicy]=[]
var lifetimes: Array[DemoLifetime]=[]

func state(actor: PlayerController) -> Dictionary:
	return {"hp":actor.actor_resources.health.current,"energy":actor.actor_resources.stamina.current,"shots":actor.action_resources.shot_charges,"jump_maximum":actor.jump_ability.maximum_jumps(),"position":actor.motor.global_position,"shot_enabled":actor.shoot_ability.enabled,"jump_enabled":actor.jump_ability.enabled}

func _ready() -> void:
	var source:="";var output:="";var args:=OS.get_cmdline_user_args()
	for i: int in args.size():
		if args[i]=="--package" and i+1<args.size():source=args[i+1]
		if args[i]=="--receipt" and i+1<args.size():output=args[i+1]
	if source.is_empty():get_tree().quit(2);return
	var scene: PackedScene=load(source.path_join("module.tscn"));world=Node2D.new();add_child(world)
	var rows: Array=[]
	for i: int in 2:
		var package=scene.instantiate();package.position=Vector2(2048+i*3072,128);world.add_child(package);packages.append(package)
		var body: PlayerMotor=PLAYER.instantiate();body.get_node("PlayerFeedback").free();body.position=package.to_global(Vector2(package.content.reward_sites[0].position[0],package.content.reward_sites[0].position[1]));world.add_child(body)
		var controller: PlayerController=body.get_node("Controller");controller.enable_shot_energy();body.get_node("KeyboardMouseAdapter").set_process_unhandled_input(false);controllers.append(controller)
		var lifetime:=DemoLifetime.new();lifetimes.append(lifetime)
		var policy:=FrameDamagePolicy.new();policy.lifetime=lifetime;world.add_child(policy);policy.register_target(&"player",controller.actor_resources.health,true);policy.register_player_controller(controller);policies.append(policy)
		var before:=state(controller);var bound: Dictionary=package.bind_player(controller,policy,lifetime,wallet,null,"placed-instance-"+str(i));var after:=state(controller)
		rows.append({"bound":bound,"same_resources_at_bind":before==after,"before":before,"after":after})
	for tick: int in 15:await get_tree().physics_frame
	var duplicate=scene.instantiate();duplicate.position=Vector2(9000,0);world.add_child(duplicate)
	var rejected: Dictionary=duplicate.bind_player(controllers[0],policies[0],lifetimes[0],wallet,null,"placed-instance-0")
	var all_claimed: bool=packages.all(func(p):return p.rewards.services.values()[0].claimed)
	var expected: int=int(packages[0].content.reward_sites[0].amount)*2
	var good: bool=wallet.balance==expected and all_claimed and rows.all(func(r):return r.bound.ok and r.same_resources_at_bind) and not rejected.ok and rejected.reason=="duplicate_instance_identity"
	var receipt:={"schema":"pcg/godot-package-game-adapter-smoke/v1","passed":good,"fixture":"two translated instances/external original actors/shared wallet","expected_coins":expected,"actual_coins":wallet.balance,"both_claimed":all_claimed,"duplicate_identity":rejected,"rows":rows,"snapshots":packages.map(func(p):return p.snapshot()),"human_playtest":false,"route_certification":false}
	if not output.is_empty():var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(receipt));file.close()
	print("GAME_ADAPTER_SMOKE ",JSON.stringify({"passed":good,"actual_coins":wallet.balance,"expected_coins":expected,"duplicate_rejected":not rejected.ok}))
	var cleanup: Dictionary=await LIFECYCLE.dispose(get_tree(),world,controllers[0]);get_tree().quit(0 if good and cleanup.released else 4)
