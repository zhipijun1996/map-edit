extends "../batch30_cell/main_v3.gd"
const CONTACTS=preload("contact_observer_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	for latch in pair_runtime.pairs:
		latch.gate_body.name="PairGateA_"+str(latch.link_id)
		latch.paired_gate_body.name="PairGateB_"+str(latch.link_id)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].original_slide_contacts=CONTACTS.contacts(motor)
