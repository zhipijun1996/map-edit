extends "res://runner_plains.gd"
const EXTRA=preload("mechanics.gd")
var extra

func _cell_aim(query: Dictionary, fallback: Vector2) -> Vector2:
	if query.get("receiver","")!="access":return super._cell_aim(query,fallback)
	for latch: ShotLatch in cells.latches:
		if str(latch.link_id)!=str(query.id) or latch.access_positions.is_empty():continue
		var target:=latch.to_global(latch.access_positions[0])
		var aim:=(target-motor.global_position).normalized()
		var visual: CourierVisual=motor.get_node("CourierVisual")
		for _iteration: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
		return aim
	return fallback

func make_fixture(case: Dictionary) -> void:
	await super.make_fixture(case)
	extra=EXTRA.new();extra.owner_runner=self;world.add_child(extra)
	extra.setup(case,world,controller,context,cells)

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if active:
		extra.capture();captured[-1].workshop=extra.snapshot()

func run_case(case: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(case)
	if not result.get("rejected",false):result.workshop=extra.snapshot()
	return result
