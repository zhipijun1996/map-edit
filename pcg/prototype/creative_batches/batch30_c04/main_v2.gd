extends "main_v1.gd"
const NAMES=preload("stable_support_names_v1.gd")
func rebuild(new_mode: String) -> void:
	await super.rebuild(new_mode)
	NAMES.install(self)
