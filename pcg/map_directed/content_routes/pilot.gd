extends "../woven_region/pilot.gd"
## Observe actual enemy death and select another input plan. Never restore it.
func _start(frame: int) -> void:
	super._start(frame)
	if failed:return
	var leg:=active_leg()
	if not leg.has("depleted_enemy"):return
	var specs:Array=host.current_case.get("enemies",[])
	for i:int in specs.size():
		if str(specs[i].id)!=str(leg.depleted_enemy):continue
		if not host.cells.enemies[i].health.terminal:return
		host.plan=leg.depleted_plan.duplicate(true)
		current_log.input_program=host.plan.duplicate(true)
		current_log.observed_enemy_defeated=str(leg.depleted_enemy)
		for cmd:Dictionary in host.plan:
			var trigger:Dictionary=cmd.get("trigger",{})
			if trigger.has("dynamic") and not trigger.has("state"):trigger.state="__dynamic__"
		return
