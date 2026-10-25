extends "../../workshop/runner.gd"
const DOCK=preload("dock_binding_v11.gd")
func make_fixture(case:Dictionary)->void:
	await super.make_fixture(DOCK.masked(case));DOCK.install(self,case)
