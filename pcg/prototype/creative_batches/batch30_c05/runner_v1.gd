extends "../batch30_cell/runner_v3.gd"
## Stable real door Node names only, shared with native consumer.
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
