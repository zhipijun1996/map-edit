extends "runner_v2.gd"
## Deliberate fault injection only for Cell tests, never a content policy.
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	var mode:=str(data.get("cell_fault",""))
	for pair in pair_runtime.pairs:
		var original: Callable=pair.receiver.damage_sink
		pair.receiver.damage_sink=func(packet: Dictionary) -> bool:
			if mode=="cancel-before-hit":
				pair.cancel()
				var accepted: bool=original.call(packet)
				pair.pair_events.append({"frame":context.frame,"type":"fault_probe","kind":mode,"accepted":accepted})
				return accepted
			if mode=="stale-target-epoch":
				var stale:=packet.duplicate(true);stale.target_epoch=int(packet.target_epoch)+1
				var stale_accepted: bool=original.call(stale)
				var accepted: bool=original.call(packet)
				pair.pair_events.append({"frame":context.frame,"type":"fault_probe","kind":mode,"stale_accepted":stale_accepted,"accepted":accepted})
				return accepted
			var accepted: bool=original.call(packet)
			if mode=="duplicate-delivery":
				var duplicate: bool=original.call(packet)
				pair.pair_events.append({"frame":context.frame,"type":"fault_probe","kind":mode,"first_accepted":accepted,"duplicate_accepted":duplicate})
			elif mode=="cancel-pending":
				pair.cancel_pending()
				pair.pair_events.append({"frame":context.frame,"type":"fault_probe","kind":mode,"first_accepted":accepted})
			return accepted
