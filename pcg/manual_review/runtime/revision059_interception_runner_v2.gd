extends "revision059_interception_runner_v1.gd"
var observed_serial:=0
func condition_met(state: String) -> bool:
 if state=='hq_native_seed':
  for actor: EnemyActor in cells.enemies:
   if actor.attack_behavior!=null and actor.attack_behavior._serial>observed_serial and not actor.attack_behavior._projectiles.is_empty():observed_serial=actor.attack_behavior._serial;return true
  return false
 return super.condition_met(state)
