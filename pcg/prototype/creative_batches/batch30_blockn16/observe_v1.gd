extends RefCounted
## Read-only original collisions and post-step projected velocity.
static func snapshot(host) -> Dictionary:
	var contacts: Array=[]
	for i: int in host.motor.get_slide_collision_count():
		var hit: KinematicCollision2D=host.motor.get_slide_collision(i)
		var collider=hit.get_collider()
		var n:=hit.get_normal()
		var travel:=hit.get_travel()
		contacts.append({"collider":str(collider.name) if collider!=null else "UNKNOWN","normal":[n.x,n.y],"travel":[travel.x,travel.y]})
	var recoil: Vector2=host.motor.recoil_velocity
	var normal: Vector2=host.motor.normal_velocity
	return {"contacts":contacts,"recoil_velocity":[recoil.x,recoil.y],"normal_velocity":[normal.x,normal.y],"burst_remaining":host.motor.recoil_burst_remaining}
