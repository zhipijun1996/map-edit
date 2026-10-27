extends RefCounted
## Reads original Motor collision reports; no transform/state/resource writes.
static func contacts(motor: CharacterBody2D) -> Array:
	var result: Array=[]
	for index: int in motor.get_slide_collision_count():
		var hit:=motor.get_slide_collision(index)
		var body:=hit.get_collider()
		result.append({"body":str(body.name) if is_instance_valid(body) else "", "normal":[hit.get_normal().x,hit.get_normal().y], "position":[hit.get_position().x,hit.get_position().y], "travel":[hit.get_travel().x,hit.get_travel().y], "remainder":[hit.get_remainder().x,hit.get_remainder().y]})
	return result
