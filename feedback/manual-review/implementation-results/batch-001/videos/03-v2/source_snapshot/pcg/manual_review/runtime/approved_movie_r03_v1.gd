extends "approved_movie_plain_v1.gd"
const REVIEW_AIR=preload("air_enemy_binding_v1.gd")

func rebuild(new_mode: String) -> void:
	var index:=selection.selected
	var source: Dictionary=cases[index]
	cases[index]=REVIEW_AIR.ordinary(source)
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	REVIEW_AIR.install(source,world,controller,context,cells)
	display.case_data=source
