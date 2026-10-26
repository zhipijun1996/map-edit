extends "../../workshop/main.gd"
const MOUNT=preload("mount_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	MOUNT.install(self,case_data)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].workshop.mounted_bells=MOUNT.snapshot(self)
