extends "revision062_runner_v1.gd"
func condition_met(state: String) -> bool:
 if state=='r062_left_pose_ok':return carrier('P').position.x<=285
 return super.condition_met(state)
