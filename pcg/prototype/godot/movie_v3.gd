extends "res://main_v3.gd"
## Three representative research input witnesses, with real original dynamics.
var movie_cases: Array[int]=[]
var movie_cursor:=0
var movie_hold:=0
var movie_logged:=false
var movie_transitioning:=false
var movie_results: Array=[]
func _ready() -> void:
	super._ready()
	if cases.is_empty():get_tree().quit(2);return
	for family: String in ["thorns","saw","carrier","sky"]:
		for i: int in cases.size():
			var detected:="sky" if cases[i].has("region_profile") and str(cases[i].get("id","")).begins_with("sky-mixed") else ("carrier" if not cases[i].get("moving_platforms",[]).is_empty() else ("saw" if not cases[i].get("saws",[]).is_empty() else "thorns"))
			if detected==family:movie_cases.append(i);break
	if movie_cases.is_empty():push_error("No dynamic representative candidates");get_tree().quit(2);return
	selection.select(movie_cases[0]);selection.disabled=true
	var rows:=ui.get_child(0).get_child(0)
	(rows.get_child(0) as Label).text="失序之钟 · 真实动态候选研究录像 / 预生成输入见证 · 趣味性待人工验证"
	for button: Node in rows.get_child(1).get_children():
		if button is BaseButton:button.disabled=true
	set_process_unhandled_input(false)
	print("MOVIE_V3_START ",JSON.stringify({"segments":movie_cases.size(),"physics_hz":60,"policy":"recorded real Router inputs; original dynamic components"}))
func rebuild(_new_mode: String) -> void:
	movie_hold=0;movie_logged=false
	super.rebuild("replay")
func _physics_process(_delta: float) -> void:
	if movie_transitioning or not prepared or not finished:return
	if not movie_logged:
		var result:={"id":case_data.get("id",""),"region_profile":case_data.get("region_profile",{}),"hazard_source_counts":{"saws":case_data.get("saws",[]).size(),"thorns":case_data.get("thorns",[]).size(),"static":case_data.get("hazards",[]).size()},"safe":safe,"stable_frames":stable_frames,"settled_goal":stable_frames>=maxi(6,int(case_data.get("settle_frames",6))),"frame":frame,"events":event_counts.duplicate(true),"capabilities":capabilities.duplicate(),"hp":controller.actor_resources.health.current,"damage_submissions":context.policy.records.duplicate(true),"damage_commits":context.damage.duplicate(true),"returns":context.returns.duplicate(true),"contact_frames":context.contact_history.size(),"dynamic":last_snapshot.duplicate(true),"status":status.text,"replay":"recorded real Router inputs","fun_approval":"unverified"}
		movie_results.append(result);print("MOVIE_V3_SEGMENT ",JSON.stringify(result));movie_logged=true
	movie_hold+=1
	if movie_hold>=30:movie_transitioning=true;next_segment.call_deferred()
func next_segment() -> void:
	movie_cursor+=1
	if movie_cursor>=movie_cases.size():
		print("MOVIE_V3_COMPLETE ",JSON.stringify({"segments":movie_results,"all_safe_and_stable":movie_results.all(func(value: Dictionary):return value.safe and value.settled_goal)}));get_tree().quit(0);return
	selection.select(movie_cases[movie_cursor]);rebuild("replay");movie_transitioning=false
