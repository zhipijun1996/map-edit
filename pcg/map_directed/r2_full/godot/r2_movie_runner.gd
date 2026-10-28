extends "r2_visual_runner.gd"
## Movie-only presentation: the inherited concrete fixture and policy are intact.
const MINIMAP = preload("r2_minimap.gd")
var minimap_layer: CanvasLayer
var minimap

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if not setup_error.is_empty(): return
	minimap_layer = CanvasLayer.new()
	minimap_layer.layer = 50
	root.add_child(minimap_layer)
	minimap = MINIMAP.new()
	minimap_layer.add_child(minimap)
	minimap.setup(case, motor)

func dispose_visual(code: int) -> void:
	if minimap != null:
		print("R2_MINIMAP_RECEIPT ", JSON.stringify(minimap.receipt()))
	if is_instance_valid(minimap_layer):
		minimap_layer.queue_free()
	await super.dispose_visual(code)
