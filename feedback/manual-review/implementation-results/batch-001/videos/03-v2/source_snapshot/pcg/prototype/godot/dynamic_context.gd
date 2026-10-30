extends Node
## Scheduling adapter only. Original dynamics, damage and Motor own gameplay.
signal tick_finished
var runner
var module: PlatformingModule
var controller: PlayerController
var policy: RecordingPolicy
var lifetime: DemoLifetime
var respawn: SegmentRespawn
var frame:=0
var running:=false
var returns: Array=[]
var damage: Array=[]
var contact_history: Array=[]
var fatal:=false
var anchor_ready:=false
var driver_mode:=false

class RecordingPolicy extends FrameDamagePolicy:
	var records: Array=[]
	var context
	func submit(request: DamageRequest) -> bool:
		var accepted:=super.submit(request)
		records.append({"frame":context.frame,"event_id":str(request.event_id),"source_id":str(request.source_id),"source":str(request.source_id).split("@")[0],"amount":request.amount,"accepted":accepted,"actor_epoch":request.actor_epoch,"physics_tick":request.physics_tick})
		return accepted

class ControllerDriver extends Node:
	var context
	func _physics_process(delta: float) -> void:
		if context.running and context.driver_mode:context.controller._physics_process(delta)

class Observer extends Node:
	var context
	func _physics_process(_delta: float) -> void:
		if not context.running:return
		context.runner.capture_dynamic_frame()
		context.tick_finished.emit()

func _ready() -> void:
	process_physics_priority=-10
	var driver:=ControllerDriver.new();driver.context=self;driver.process_physics_priority=0;add_child(driver)
	var observer:=Observer.new();observer.context=self;observer.process_physics_priority=1100;add_child(observer)

func _physics_process(_delta: float) -> void:
	if not running:return
	if not anchor_ready:
		anchor_ready=respawn.activate_anchor(&"entry")
		if not anchor_ready:runner.setup_error="unsafe_entry_anchor"
	runner.prepare_dynamic_frame()

func attach_damage() -> void:
	lifetime=DemoLifetime.new()
	policy=RecordingPolicy.new();policy.context=self;policy.lifetime=lifetime
	add_child(policy)
	policy.register_target(&"player",controller.actor_resources.health,true)
	policy.register_player_controller(controller)
	respawn=SegmentRespawn.new();respawn.configure(controller,lifetime)
	respawn.danger_bounds=module.world_dangers()
	respawn.add_anchor(&"entry",module.world_entry())
	policy.environment_return_requested.connect(func():
		var clock_before:=module.clock
		var before:=controller.motor.global_position
		var epoch_before:=lifetime.actor_epoch
		var ok:=respawn.return_to_anchor()
		returns.append({"frame":frame,"returned":ok,"from":[before.x,before.y],"to":[controller.motor.position.x,controller.motor.position.y],"clock_before":clock_before,"clock_after":module.clock,"actor_epoch_before":epoch_before,"actor_epoch_after":lifetime.actor_epoch})
		if ok:policy.protect_player())
	policy.player_fatal.connect(func():fatal=true;controller.die())
	policy.batch_resolved.connect(func(results: Array[DamageResult]):
		for result: DamageResult in results:
			damage.append({"frame":frame,"source_id":str(result.request.source_id),"source":str(result.request.source_id).split("@")[0],"amount":result.request.amount,"hp":result.health.current,"lethal":result.lethal,"request_actor_epoch":result.request.actor_epoch,"actor_epoch":lifetime.actor_epoch}))
	module.setup_damage(controller,policy,lifetime)

func phase_condition(query: Dictionary) -> bool:
	var kind: String=query.get("kind","")
	if kind=="actor_x":
		return controller.motor.position.x>=float(query.value) if query.get("direction","gte")=="gte" else controller.motor.position.x<=float(query.value)
	if kind=="on_platform":return support_id()==str(query.id)
	var phase:=-1.0
	if kind=="platform_phase":
		for platform: ModuleMovingPlatform in module.moving_platforms:
			if str(platform.definition.platform_id)==str(query.id):phase=fposmod(module.clock/platform.definition.period()+platform.definition.initial_phase,1.)
	elif kind=="saw_phase":
		for saw: ModuleSawHazard in module.hazards:
			if str(saw.definition.source_id)==str(query.id):phase=fposmod(module.clock/saw.definition.period+saw.definition.initial_phase,1.)
	if phase<0:return false
	var window: Array=query.window
	return phase>=float(window[0]) and phase<=float(window[1]) if float(window[0])<=float(window[1]) else phase>=float(window[0]) or phase<=float(window[1])

func support_id() -> String:
	var motor:=controller.motor
	if not motor.is_on_floor():return ""
	for i: int in motor.get_slide_collision_count():
		var collision:=motor.get_slide_collision(i)
		if collision.get_normal().y<-.7:
			var body=collision.get_collider()
			if body is ModuleMovingPlatform:return str(body.definition.platform_id)
			if body is Node:return str(body.name)
	return ""

func snapshot() -> Dictionary:
	var platforms: Array=[];var saws: Array=[];var contacts: Array=[]
	for child: Node in module.get_children():
		if child is DemoContactEmitter and child._was_touching:contacts.append({"source":str(child.source_id),"kind":"static_contact"})
	for platform: ModuleMovingPlatform in module.moving_platforms:
		platforms.append({"id":str(platform.definition.platform_id),"position":[platform.position.x,platform.position.y],"phase":fposmod(module.clock/platform.definition.period()+platform.definition.initial_phase,1.),"physics_velocity":platform_velocity(platform)})
	for saw: ModuleSawHazard in module.hazards:
		saws.append({"id":str(saw.definition.source_id),"position":[saw.position.x,saw.position.y],"phase":fposmod(module.clock/saw.definition.period+saw.definition.initial_phase,1.),"touching":saw._touching})
	var velocity:=controller.motor.get_platform_velocity()
	return {"module_clock":module.clock,"static_contacts":contacts,"hazard_contacts":contacts_now(),"moving_platforms":platforms,"saws":saws,"support_id":support_id(),"platform_velocity":[velocity.x,velocity.y],"actor_epoch":lifetime.actor_epoch,"lifetime_active":lifetime.active,"dead":fatal,"damage_commits":damage.size(),"damage_submissions":policy.records.size(),"returns":returns.size()}

func platform_velocity(platform: ModuleMovingPlatform) -> Array:
	var velocity: Vector2=PhysicsServer2D.body_get_state(platform.get_rid(),PhysicsServer2D.BODY_STATE_LINEAR_VELOCITY)
	return [velocity.x,velocity.y]

func freeze() -> void:
	running=false;controller.set_physics_process(false);module.set_physics_process(false);policy.set_physics_process(false)
	for child: Node in module.get_children():child.set_physics_process(false)

func contacts_now() -> Array:
	var result: Array=[]
	for saw: ModuleSawHazard in module.hazards:
		if saw._touching:result.append({"source":str(saw.definition.source_id),"kind":"saw_contact"})
	for child: Node in module.get_children():
		if child is DemoContactEmitter and child._was_touching:result.append({"source":str(child.source_id),"kind":"static_contact"})
	return result
