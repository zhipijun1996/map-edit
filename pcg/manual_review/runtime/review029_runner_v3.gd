extends "refresh_runner_v4.gd"
const WAVE=preload("review029_ambush_v2.gd")
var wave
func make_fixture(data: Dictionary) -> void:
	var ordinary:=data.duplicate(true)
	if data.has("review029_wave"):ordinary.enemies=[]
	await super.make_fixture(ordinary)
	current_case=data
	if data.has("review029_wave"):
		wave=WAVE.new();world.add_child(wave);wave.setup(data,world,controller,context,cells,self)
func snapshot(index: int, axis: float, actions: Array) -> Dictionary:
	var value:=super.snapshot(index,axis,actions)
	if is_instance_valid(wave):value.review029_wave=wave.snapshot()
	return value
