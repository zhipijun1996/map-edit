extends "../../workshop/runner.gd"
const OCC=preload("binding_v1.gd")
func make_fixture(case:Dictionary)->void:
	await super.make_fixture(OCC.masked(case));OCC.install(self,case)
