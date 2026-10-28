extends "../direct_join/carrier_pilot.gd"
## Inputs only: jump from a moving carrier, shoot the actual toggle bell while
## airborne, use the same recoil to reach the stationary upper bank.
var parked_leg := ""
func tick(frame: int) -> Array:
	var requested := super.tick(frame)
	if failed or completed: return requested
	var leg := active_leg()
	var transfer: Dictionary = leg.get("carrier_transfer", {})
	if transfer.has("park_bell") and carrier_stage == "exiting" and frame >= release_at - 5 and parked_leg != str(leg.id):
		var bell: ShotLatch
		for item: Node in host.world.get_children():
			if item is ShotLatch and item.link_id == str(transfer.park_bell): bell = item; break
		if bell == null: stop("missing_actual_parking_bell",frame); return requested
		var direction: Vector2 = (bell.bell_position-host.motor.global_position).normalized()
		host.controller.router.request_action(&"shoot_release",direction)
		requested.append({"type":"shoot_release","direction":[direction.x,direction.y],"pilot_leg":str(leg.id)})
		parked_leg = str(leg.id)
	return requested
