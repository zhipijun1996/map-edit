extends "approved_movie_plain_v1.gd"
func capture_dynamic_frame() -> void:
	super.capture_dynamic_frame()
	if not finished:status.text="向左下击铃，同枪反冲登高岸；起跳越过守岸怪，取8币后到B。 · 金币 "+str(extra.wallet.balance)
