extends "formal_mechanics.gd"
## A physical chest can be claimed by contact. Enemy refund is an interesting
## demonstrated strategy, not an artificial lock on an otherwise open chest.
func capture(frame: int, value: Dictionary) -> void:
	super.capture(frame,value)
	if not actor.motor.is_on_floor():return
	for node: Dictionary in optional:
		if node.get("required_bell","")!="" or node.get("required_enemy","")!="":continue
		var service: SimpleRoomReward=services[str(node.id)]
		var r: Array=node.target.region
		if service.claimed or not Rect2(r[0],r[1],r[2],r[3]).has_point(actor.motor.position):continue
		var receipt:=service.claim(context.lifetime.token(),StringName("r2_map:"+str(node.id)))
		var event:=state(frame);event.challenge_id=node.id;event.accepted=receipt.accepted()
		event.amount_applied=receipt.amount_applied;event.balance=receipt.coins
		optional_events.append(event)
