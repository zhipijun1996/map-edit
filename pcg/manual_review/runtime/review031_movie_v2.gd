extends "clarified_three_movie_v3.gd"
## 198 has neither paired gates nor retractable gears. Its original harness
## does not install those consumers or serialize their empty extension arrays.
## Keep the comparator and all physical/event values unchanged.
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if not active or replay_trace.is_empty() or case_data.approved_implementation.reviewId!="198":return
	assert(case_data.get("paired_gates",[]).is_empty() and case_data.get("retractable_groups",[]).is_empty())
	var state: Dictionary=replay_trace[-1].workshop
	for key: String in ["paired_gates","retractable_groups"]:
		assert(state.get(key,[]).is_empty())
		state.erase(key)
