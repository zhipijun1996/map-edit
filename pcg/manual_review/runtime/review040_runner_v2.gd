extends "review040_runner_v1.gd"
const COMMITTED_RELEASE=preload("review040_reward_release_v1.gd")
var committed_release
func validate_plan(raw: Variant) -> String:
	var copy: Variant=raw.duplicate(true) if raw is Array else raw
	if copy is Array:
		for command: Dictionary in copy:
			if command.get("trigger",{}).get("state","")=="enemy_below":command.trigger.state="airborne"
	return super.validate_plan(copy)
func condition_met(state: String) -> bool:
	if state=="reward_released":return committed_release!=null and committed_release.released
	if state=="enemy_below":
		var q: Dictionary=plan[plan_index].enemy_window;var enemy:=observed_enemy(str(q.id))
		return enemy!=null and not enemy.health.terminal and not motor.is_on_floor() and enemy.motor.position.y-motor.position.y>=float(q.get("minimum_drop",15))
	return super.condition_met(state)
func make_fixture(data: Dictionary) -> void:
	committed_release=null
	await super.make_fixture(data)
	if data.has("review040_release"):
		committed_release=COMMITTED_RELEASE.new();committed_release.configure(data.review040_release,context.module.get_node("Platform"+str(int(data.review040_release.platform_index))),extra)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and committed_release!=null:
		committed_release.step(int(captured[-1].frame));captured[-1].review040_release=committed_release.snapshot()
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if committed_release!=null:result.review040_release=committed_release.snapshot()
	return result
