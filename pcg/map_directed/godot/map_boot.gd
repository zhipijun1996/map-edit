extends SceneTree
## Launch this external scene adapter inside the unchanged pinned Godot project.
func _initialize() -> void:
	launch.call_deferred()

func launch() -> void:
	var path := (get_script() as Script).resource_path.get_base_dir().path_join("map_scene.gd")
	var scene: Node = load(path).new()
	root.add_child(scene)
