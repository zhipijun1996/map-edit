extends "first30_movie_v1.gd"
## Original fixture initialization is performed exactly once before frame zero.
const EXACT_FIXTURE=preload("../../migration/runtime/native_profile_v5.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	if not prepared:return
	if case_data.get("original_fixture_profile") is Dictionary:
		var result: Dictionary=EXACT_FIXTURE.new().initialize_once(controller,case_data.original_tuning_profile,case_data.original_fixture_profile)
		if not result.ok:
			push_error(str(result));get_tree().quit(2);return
	ability_label.text="已审核设计 · 原始能力/资源 · 原生输入回放 · 人工试玩待评"
