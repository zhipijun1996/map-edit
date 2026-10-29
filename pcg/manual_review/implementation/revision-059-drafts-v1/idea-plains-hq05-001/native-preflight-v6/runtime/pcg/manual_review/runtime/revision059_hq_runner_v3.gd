extends "revision059_hq_runner_v2.gd"
func condition_met(state: String) -> bool:
 if state=='hq_gate_open':
  for l: ShotLatch in cells.latches:
   if str(l.link_id)=='turret-target-bell':return motor.is_on_floor() and l.is_open
  return false
 if state=='hq_lower':return motor.is_on_floor() and str(context.snapshot().get('support_id',''))=='P' and carrier('P').position.y>=405
 if state=='hq_mid_board':return motor.is_on_floor() and carrier('P').position.y>=385
 return super.condition_met(state)
