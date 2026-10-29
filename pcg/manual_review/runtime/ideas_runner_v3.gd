extends "ideas_runner_v2.gd"
## One noisy observed compound input: shoot release and jump are submitted to
## the original Router in the same physics frame. No resources are changed.
func control_plan(frame: int) -> Array:
	var before:=fired_commands.size();var requested:=super.control_plan(frame)
	for event: Dictionary in fired_commands.slice(before):
		var command: Dictionary=plan[int(event.index)]
		if command.get("jump_same_frame",false):
			controller.router.request_action(&"jump",Vector2.ZERO)
			requested.append({"type":"jump","direction":[0,0],"plan_index":int(event.index)})
	return requested
