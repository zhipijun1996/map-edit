extends "visual.gd"
## Presentation-only cleanup for review. Keep all Cells, colliders and input.
var world_labels: Array[Label] = []

func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not setup_error.is_empty(): return
	collect_world_labels(world)
	for label: Label in world_labels: label.visible = false
	(status_label.get_parent().get_child(0) as Label).text = "风铃平原 · 回风崖径 · 程序回放 / 正常速度"

func collect_world_labels(node: Node) -> void:
	if node is Label: world_labels.append(node)
	for child: Node in node.get_children(): collect_world_labels(child)

func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	for label: Label in world_labels:
		if is_instance_valid(label): label.visible = false
