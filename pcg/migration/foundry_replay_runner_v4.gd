extends "game_world_runner_v4.gd"
## Replay original INPUT events through the existing Harness action scheduler.
## axes_v3/actions_v3 and their timing/aim disturbances are produced by the
## existing runner_v3; recorded poses never enter movement or collision code.
var native_until:=0

func make_fixture(case: Dictionary) -> void:
	var probe: Dictionary=case.get("migration_probe",{})
	var counter: Dictionary=case.get("migration_counter",{})
	var active: bool=case.has("original_replay_frame_count") and probe.get("kind","")not in ["local_boundary","continuous_entry"] and (counter.is_empty() or counter.get("keepNativeTimeline",false))
	var routed:=case.duplicate(true)
	if not active:
		routed.erase("axes");routed.erase("actions")
	await super.make_fixture(routed)
	native_until=int(case.get("original_replay_frame_count",0))if active else 0

func control_plan(frame: int) -> Array:
	if frame>=native_until:return super.control_plan(frame)
	var requests: Array=[]
	for action: Dictionary in actions_v3.get(frame,[]):
		controller.router.request_action(StringName(action.type),point(action.get("direction",[0,0])))
		requests.append(action)
	return requests
