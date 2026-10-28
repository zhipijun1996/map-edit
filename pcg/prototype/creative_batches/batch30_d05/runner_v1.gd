extends "../../workshop/runner.gd"
const MOUNT=preload("mount_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	MOUNT.install(self,data)
func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.mounted_bells=MOUNT.snapshot(self)
func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false):result.workshop.mounted_bells=MOUNT.snapshot(self)
	return result
