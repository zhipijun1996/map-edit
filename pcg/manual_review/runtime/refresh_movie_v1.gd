extends "first40_movie_v1.gd"
const REFRESH=preload("refresh_cells_v1.gd")
const BOOTSTRAP=preload("refresh_carrier_bootstrap_v1.gd")
var refresh_consumers: Array=[]
func rebuild(new_mode: String) -> void:
	refresh_consumers=[]
	var index:=selection.selected;var source: Dictionary=cases[index]
	cases[index]=REFRESH.ordinary(source)
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	if not prepared:return
	refresh_consumers=REFRESH.install(source,world,controller,context,cells)
	if not refresh_consumers.is_empty():
		var bootstrap=BOOTSTRAP.new();bootstrap.observed=refresh_consumers;world.add_child(bootstrap)
	ability_label.text="已审核设计 · 原始能力/资源 · 原生输入回放 · 人工试玩待评"
