extends "review029_runner_v2.gd"
const DOCK=preload("../../prototype/creative_batches/machinery/dock_binding_v11.gd")
const MOUNT=preload("../../prototype/creative_batches/batch30_d05/mount_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(DOCK.masked(data))
	current_case=data
	DOCK.install(self,data);MOUNT.install(self,data)
func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	value.review029_mounted_bells=MOUNT.snapshot(self)
	return value
