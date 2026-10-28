extends "../batch30_d03/main_v1.gd"
const OVERVIEW=preload("overview_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OVERVIEW.install(self,Rect2(-760,-165,1980,965))
