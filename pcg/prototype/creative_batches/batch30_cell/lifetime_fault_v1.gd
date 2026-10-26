extends "runner_v2.gd"
## Component fault probe only: invalidate the real pending shot's lifetime token.
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	for pair in pair_runtime.pairs:
		var original: Callable=pair.receiver.damage_sink
		pair.receiver.damage_sink=func(packet: Dictionary) -> bool:
			var accepted: bool=original.call(packet)
			context.lifetime.invalidate_actor()
			pair.pair_events.append({"frame":context.frame,"type":"fault_probe","kind":"invalidate-actor-after-real-hit","first_accepted":accepted,"new_actor_epoch":context.lifetime.actor_epoch})
			return accepted
