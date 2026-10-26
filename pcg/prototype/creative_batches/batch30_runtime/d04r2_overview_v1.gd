extends "../../workshop/main.gd"
const OVERVIEW=preload("overview_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	OVERVIEW.install(self,Rect2(-215,235,1760,690))
	status.text="去程同枪跨岸/停台 · 中位供直接返回，东位供远岸奖励接力 · 原生程序回放，观感待评"
