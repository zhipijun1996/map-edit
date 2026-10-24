extends SceneTree
## Native convenience launcher; Web exports use r2_manual_scene.tscn directly.
func _initialize() -> void:
	launch.call_deferred()

func launch() -> void:
	var path := (get_script() as Script).resource_path.get_base_dir().path_join("r2_manual_scene.tscn")
	var scene: PackedScene = load(path)
	if scene == null: push_error("R2 manual scene failed to load"); quit(2); return
	root.add_child(scene.instantiate())
