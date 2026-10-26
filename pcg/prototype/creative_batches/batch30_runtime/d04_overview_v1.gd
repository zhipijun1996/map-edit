extends "../../workshop/main.gd"
const OVERVIEW=preload("overview_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OVERVIEW.install(self,Rect2(-215,235,1530,690))
	status.text="同一枪跨岸并停台 · 中停位用于直接返回，东停位用于下层宝箱 · 程序回放，观感待评"
