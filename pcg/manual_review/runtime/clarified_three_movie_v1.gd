extends "refresh_movie_v1.gd"
const CLARIFIED_WAVE=preload("review029_ambush_v2.gd")
const CLARIFIED_DOCK=preload("../../prototype/creative_batches/machinery/dock_binding_v11.gd")
const CLARIFIED_MOUNT=preload("../../prototype/creative_batches/batch30_d05/mount_v1.gd")
var clarified_wave
func rebuild(new_mode: String) -> void:
	var index:=selection.selected;var source: Dictionary=cases[index]
	var ordinary: Dictionary=CLARIFIED_DOCK.masked(source)
	if source.has("review029_wave"):ordinary.enemies=[];ordinary.erase("review029_wave")
	cases[index]=ordinary
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	if not prepared:return
	CLARIFIED_DOCK.install(self,source);CLARIFIED_MOUNT.install(self,source)
	if source.has("review029_wave"):
		clarified_wave=CLARIFIED_WAVE.new();world.add_child(clarified_wave);clarified_wave.setup(source,world,controller,context,cells,self)
		ability_label.text="低顶狭道 · 左右交替射击 · 不跳跃 · 原生输入回放"
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():
		if is_instance_valid(clarified_wave):replay_trace[-1].review029_wave=clarified_wave.snapshot()
		replay_trace[-1].review029_mounted_bells=CLARIFIED_MOUNT.snapshot(self)
