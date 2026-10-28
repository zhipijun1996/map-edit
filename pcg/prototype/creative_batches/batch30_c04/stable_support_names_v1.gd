extends RefCounted
## Stable semantic Node names only. Same original bodies/shapes/positions.
static func install(host) -> void:
	for latch in host.cells.latches:
		if not latch.has_method("snapshot_pair"):continue
		var prefix: String=str(latch.link_id).validate_node_name()
		latch.gate_body.name=prefix+"_gate_A"
		latch.paired_gate_body.name=prefix+"_gate_B"
