extends "../content_domains/native_runner.gd"
## Input-only combat leg. Actor, weapons, hit detection and Boss are originals.
func control_plan(frame:int)->Array:
	if pilot==null or extra==null or not extra.has_method("duel_input"):return super.control_plan(frame)
	var leg:Dictionary=pilot.active_leg()
	if not leg.has("boss_duel"):return super.control_plan(frame)
	var value:Dictionary=extra.duel_input(str(leg.boss_duel),frame,leg.target.position)
	if value.get("done",false):return super.control_plan(frame)
	return value.get("requested",[])
