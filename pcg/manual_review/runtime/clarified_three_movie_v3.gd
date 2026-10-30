extends "clarified_three_movie_v1.gd"
const ACTUAL_PORT_OVERLAY=preload("clarified_three_overlay_v3.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	for node: Node in world.get_children():
		if node.get_script()!=null and node.get_script().resource_path.ends_with("first30_overlay_v1.gd"):node.visible=false
	var overlay=ACTUAL_PORT_OVERLAY.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
	if case_data.approved_implementation.reviewId=="171":case_data.play_hint="保持低顶，左右交替开枪，用移动抵消反冲"
