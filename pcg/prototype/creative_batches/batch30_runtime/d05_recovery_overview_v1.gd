extends "../batch30_d05/main_v1.gd"
const OVERVIEW=preload("overview_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OVERVIEW.install(self,Rect2(-710,120,2340,760))
	status.text="真实失误恢复试件 · 下层回入口，观察/停台后重新追接 · 不重置人物、机关或资源"
