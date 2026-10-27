extends "foundry_feedback_runner_v5.gd"
const SOURCE_PROFILE=preload("runtime/native_profile_v5.gd")
var exact_profile_initializer
func make_fixture(case: Dictionary) -> void:
	var routed:=case.duplicate(true)
	routed.erase("original_tuning_profile")
	routed.erase("original_fixture_profile")
	await super.make_fixture(routed)
	exact_profile_initializer=SOURCE_PROFILE.new()
	var initialized: Dictionary=exact_profile_initializer.initialize_once(controller,case.original_tuning_profile,case.original_fixture_profile)
	if not initialized.get("ok",false):setup_error="original_fixture_initialization_failed/"+str(initialized);return
	capability_snapshot=ADAPTER.snapshot(controller,current_caps)
