extends ModuleMovingPlatform
## NEW Cell controller only. Inherit real collision, shape and carrying.
## Never write actor transforms, velocities or action resources.
var signed_direction:=1
var reversals: Array=[]
var scope
func _physics_process(delta: float) -> void:
	if motion_running:
		motion_clock=clampf(motion_clock+signed_direction*delta,definition.minimum_clock(),definition.maximum_clock())
	position=definition.at_time(motion_clock)
func bind_bell_control() -> void:
	bell_controlled=true;motion_clock=module.clock;motion_running=true
func set_motion_running(_legacy_toggle_value: bool) -> void:
	# Original ShotLatch's fully validated commit invokes this bridge. For this
	# explicitly new Cell this means REVERSE, never pause. No seek/teleport.
	var before:=position
	signed_direction=-signed_direction
	reversals.append({"frame":scope.frame,"type":"carrier_reverse","id":str(definition.platform_id),"direction":signed_direction,"clock":motion_clock,"position_before":[before.x,before.y],"position_after":[position.x,position.y],"airborne":not scope.controller.motor.is_on_floor()})
func snapshot_reverse() -> Dictionary:
	var v: Vector2=PhysicsServer2D.body_get_state(get_rid(),PhysicsServer2D.BODY_STATE_LINEAR_VELOCITY)
	return {"id":str(definition.platform_id),"cell":"manual_reverse_on_hit/v1","signed_direction":signed_direction,"clock":motion_clock,"running":motion_running,"position":[position.x,position.y],"physics_velocity":[v.x,v.y],"endpoint_hold":is_equal_approx(motion_clock,definition.minimum_clock())or is_equal_approx(motion_clock,definition.maximum_clock()),"events":reversals.duplicate(true)}
