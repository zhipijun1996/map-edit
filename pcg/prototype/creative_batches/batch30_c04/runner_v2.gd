extends "runner_v1.gd"
const NAMES=preload("stable_support_names_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	NAMES.install(self)
