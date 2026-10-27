extends "../../workshop/main.gd"
const OBSERVE=preload("observe_v1.gd")
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OBSERVE.install(self)
	var overlay:=BLOCK_DRAW.new()
	overlay.data=case_data;overlay.z_index=20;world.add_child(overlay);overlay.queue_redraw()
	display.set_process(false)
	display.camera.zoom=Vector2.ONE*.42
	display.camera.position=Vector2(1280,320)
func capture_dynamic_frame() -> void:
	var active: bool=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].n04_seam=OBSERVE.snapshot(self)
