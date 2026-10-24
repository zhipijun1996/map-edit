extends "res://runner_plains.gd"
## Entire assembled map is one original physics fixture and one continuous clock.
const MAP_OBSERVER = preload("map_observer.gd")
var map_observer

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	map_observer = MAP_OBSERVER.new()
	map_observer.configure(case, controller, context)
	if not map_observer.error.is_empty(): setup_error = map_observer.error

func prepare_dynamic_frame() -> void:
	# The first action may jump immediately; inspect the actual settled entry
	# before Router receives it, rather than requiring a post-action grounded frame.
	if warmup_left == 0 and current_frame == 0 and map_observer != null:
		map_observer.observe(-1, controller, context, cells.events)
	super.prepare_dynamic_frame()

func capture_dynamic_frame() -> void:
	var active := warmup_left == 0
	var index := current_frame
	if active and map_observer != null: map_observer.observe(index, controller, context, cells.events)
	super.capture_dynamic_frame()
	if active and not captured.is_empty(): captured[-1].map = map_observer.report()

func run_case(case: Dictionary) -> Dictionary:
	map_observer = null
	var result: Dictionary = await super.run_case(case)
	if map_observer != null:
		result.map_validation = map_observer.report()
		if not result.map_validation.ok:
			result.ok = false
			if result.reason == "settled_goal": result.reason = "map_route_or_reward_incomplete"
	return result
