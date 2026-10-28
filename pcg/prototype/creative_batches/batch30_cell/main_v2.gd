extends "../../workshop/main.gd"
const PAIR_RUNTIME=preload("runtime_v2.gd")
var pair_runtime

func rebuild(new_mode: String) -> void:
	var index:=selection.selected
	var source: Dictionary=cases[index]
	cases[index]=PAIR_RUNTIME.ordinary_case(source)
	await super.rebuild(new_mode)
	cases[index]=source;case_data=source
	pair_runtime=PAIR_RUNTIME.new();world.add_child(pair_runtime)
	pair_runtime.setup(source,world,controller,context,cells)
	display.case_data=source

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active and not replay_trace.is_empty():replay_trace[-1].workshop.paired_gates=pair_runtime.snapshot()
