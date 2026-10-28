extends "../batch30_blockn14/main_v1.gd"
const TARGET_LINKS=preload("n14_target_links_v1.gd")

func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	var links:=TARGET_LINKS.new()
	links.data=case_data
	links.z_index=90
	world.add_child(links)
