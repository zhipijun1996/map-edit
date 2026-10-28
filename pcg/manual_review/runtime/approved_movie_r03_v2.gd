extends "approved_movie_r03_v1.gd"
## Text only; all inputs, world state and frame comparisons stay unchanged.
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	if not finished:status.text="命中空中怪物恢复弹量；落40px小平台回充，再选择高岸宝箱或低岸。 · 金币 "+str(extra.wallet.balance)
