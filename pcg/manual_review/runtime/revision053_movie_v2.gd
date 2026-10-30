extends "ideas_movie_v1.gd"
## Presentation-only Port permission readback. Physical ports and inputs unchanged.
const VERIFIED_PORT_OVERLAY=preload("revision053_overlay_v2.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	for node: Node in world.get_children():
		if node.get_script()!=null and node.get_script().resource_path.ends_with("clarified_three_overlay_v3.gd"):node.visible=false
	var overlay=VERIFIED_PORT_OVERLAY.new();overlay.data=case_data;overlay.z_index=86;world.add_child(overlay)
