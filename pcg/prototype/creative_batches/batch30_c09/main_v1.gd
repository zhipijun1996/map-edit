extends "../batch30_cell/main_v3.gd"
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
