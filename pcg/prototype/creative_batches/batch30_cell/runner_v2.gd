extends "../../workshop/runner.gd"
const PAIR_RUNTIME=preload("runtime_v2.gd")
var pair_runtime

func make_fixture(data: Dictionary) -> void:
	await super.make_fixture(PAIR_RUNTIME.ordinary_case(data))
	pair_runtime=PAIR_RUNTIME.new();world.add_child(pair_runtime)
	pair_runtime.setup(data,world,controller,context,cells)

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:captured[-1].workshop.paired_gates=pair_runtime.snapshot()

func run_case(data: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(data)
	if not result.get("rejected",false):result.workshop.paired_gates=pair_runtime.snapshot()
	return result
