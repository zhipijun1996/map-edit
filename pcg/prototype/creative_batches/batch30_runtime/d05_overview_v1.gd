extends "../batch30_d05/main_v1.gd"
const OVERVIEW=preload("overview_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OVERVIEW.install(self,Rect2(-260,140,1870,740))
	status.text="先跳离平台，向左下击中台上风铃 · 同一枪启动追接与反冲 · 首次落脚必须是移动台"
