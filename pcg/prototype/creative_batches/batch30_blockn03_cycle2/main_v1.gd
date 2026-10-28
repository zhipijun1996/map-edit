extends "../batch30_blockn03/main_v1.gd"
const REVERSE_CAPTION=preload("reverse_caption_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	for latch: ShotLatch in cells.latches:
		if not is_instance_valid(latch.motion_target)or not latch.motion_target.has_method("snapshot_reverse"):continue
		var plaque:=REVERSE_CAPTION.new();plaque.latch=latch;plaque.z_index=100;latch.add_child(plaque)
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	status.text="N03 研发见证 · 真实反向与空中接回可执行，但地面反转少一跳达到同奖励 · 设计拒绝/未入库"
