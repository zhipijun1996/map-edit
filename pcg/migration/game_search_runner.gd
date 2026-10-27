extends "game_runner.gd"
# Reuse the authored Foundry's original initialization; profile is a fixed
# actor configuration, never a resource refill on crossing a Module seam.
func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	if case.has("original_tuning_profile"):
		var profile: Dictionary=case.original_tuning_profile
		if not FoundryCatalog.apply_profile(controller,str(profile.id)):
			setup_error="original_foundry_profile_rejected";return
		capability_snapshot=ADAPTER.snapshot(controller,current_caps)
