extends "../r2_full/godot/r2_manual_scene.gd"
const DIRECT_BOUNDS = preload("module_bounds.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared: return
	var bounds = DIRECT_BOUNDS.new()
	bounds.frames = case_data.get("module_frames", [])
	world.add_child(bounds)
