extends "../../workshop/main.gd"
const OCC=preload("binding_v1.gd")
func rebuild(new_mode:String)->void:
	var original:Dictionary=cases[selection.selected];cases[selection.selected]=OCC.masked(original)
	await super.rebuild(new_mode)
	cases[selection.selected]=original;case_data=original;OCC.install(self,original)
