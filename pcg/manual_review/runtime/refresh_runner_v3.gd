extends "refresh_runner_v2.gd"
const BOOTSTRAP=preload("refresh_carrier_bootstrap_v1.gd")
func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(data)
	if not refresh_consumers.is_empty():
		var bootstrap=BOOTSTRAP.new();bootstrap.observed=refresh_consumers;world.add_child(bootstrap)
