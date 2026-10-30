extends "review029_runner_v4.gd"
const CLARIFIED_WAVE=preload("review029_ambush_v2.gd")
var clarified_wave
func make_fixture(data: Dictionary) -> void:
	var ordinary:=data.duplicate(true)
	if data.has("review029_wave"):ordinary.enemies=[]
	await super.make_fixture(ordinary)
	current_case=data
	if data.has("review029_wave"):
		clarified_wave=CLARIFIED_WAVE.new();world.add_child(clarified_wave);clarified_wave.setup(data,world,controller,context,cells,self)
func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	if is_instance_valid(clarified_wave):value.review029_wave=clarified_wave.snapshot()
	return value
