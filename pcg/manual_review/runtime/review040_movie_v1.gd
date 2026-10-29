extends "clarified_three_movie_v3.gd"
const COMMITTED_RELEASE=preload("review040_reward_release_v1.gd")
const RELEASE_OVERLAY=preload("review040_release_overlay_v1.gd")
var committed_release
func rebuild(new_mode: String) -> void:
	committed_release=null
	await super.rebuild(new_mode)
	if not prepared or not case_data.has("review040_release"):return
	committed_release=COMMITTED_RELEASE.new();committed_release.configure(case_data.review040_release,context.module.get_node("Platform"+str(int(case_data.review040_release.platform_index))),extra)
	var overlay=RELEASE_OVERLAY.new();overlay.configure(committed_release,case_data.review040_release.rect);context.module.add_child(overlay)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and committed_release!=null and not replay_trace.is_empty():
		committed_release.step(int(replay_trace[-1].frame));replay_trace[-1].review040_release=committed_release.snapshot()
