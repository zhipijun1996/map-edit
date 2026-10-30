extends "revision060_runner_v7.gd"
func make_fixture(data: Dictionary) -> void:
 seed_serial=0;takeoff_y=0;last_native_drop=-1000;fight_jump_frame=-1000;fight_jump_release=true;fight_ready=-1;fight_actions=0;group_retry_ready=-1;group_retry_serial=0;route_mode=''
 await super.make_fixture(data)
func condition_met(state: String) -> bool:
 if state=='r060_hq02_approach':
  var p=carrier('P');var t: float=context.module.clock;return motor.is_on_floor()and p.position.y<=220 and p.definition.at_time(t+.05).y<=p.position.y and p.definition.at_time(t+.8).y<=240
 return super.condition_met(state)
