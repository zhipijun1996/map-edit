extends "../batch30_c07/main_v2.gd"
const BLOCK_DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
 await super.rebuild(new_mode)
 if not prepared:return
 var overlay:=BLOCK_DRAW.new();overlay.data=case_data;overlay.z_index=85;world.add_child(overlay)
