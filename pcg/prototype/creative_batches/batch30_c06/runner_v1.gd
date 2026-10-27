extends "../batch30_cell/runner_v3.gd"
const NAMES=preload("../batch30_c04/stable_support_names_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	NAMES.install(self)
