extends "../../workshop/main.gd"
const DOCK=preload("dock_binding_v11.gd")
func rebuild(new_mode:String)->void:
	var original:Dictionary=cases[selection.selected];cases[selection.selected]=DOCK.masked(original)
	await super.rebuild(new_mode)
	cases[selection.selected]=original;case_data=original;DOCK.install(self,original)
