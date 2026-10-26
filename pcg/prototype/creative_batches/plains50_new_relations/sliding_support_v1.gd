extends ShotLatch
## One shot moves the original AnimatableBody to its rail stop. No actor damage
## commit callback is executed, so hitting the mechanism grants no air resource.
var stop_clock:=1.15
var rail_stopped:=false
func _commit_open(request:Dictionary)->void:
	if rail_stopped:return
	super._commit_open(request)
func _physics_process(delta:float)->void:
	super._physics_process(delta)
	if not is_instance_valid(motion_target):return
	bell_position=motion_target.position+Vector2(-motion_target.definition.size.x/2.-10.,0.)
	bell_body.position=bell_position
	if motion_target.motion_running and motion_target.motion_clock>=stop_clock:
		motion_target.set_motion_running(false);rail_stopped=true;bell_body.collision_layer=0
	queue_redraw()
