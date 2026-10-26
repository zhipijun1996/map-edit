extends "../../workshop/runner.gd"
const SLIDE=preload("sliding_support_v1.gd")
func make_fixture(case:Dictionary)->void:
	var masked:=case.duplicate(true);masked.latches=[]
	for l:Dictionary in case.get("latches",[]):
		if not l.has("sliding_support"):masked.latches.append(l)
	await super.make_fixture(masked)
	for l:Dictionary in case.get("latches",[]):
		if not l.has("sliding_support"):continue
		var latch:=SLIDE.new();latch.link_id=str(l.id);latch.formal_presentation=true;latch.stop_clock=float(l.sliding_support.stop_clock)
		world.add_child(latch);var b:Array=l.bell;var g:Array=l.gate
		latch.setup(controller,context.lifetime,Vector2(b[0],b[1]),Rect2(g[0],g[1],g[2],g[3]))
		for platform:ModuleMovingPlatform in context.module.moving_platforms:
			if str(platform.definition.platform_id)==str(l.ferry_id):latch.bind_motion(platform)
		latch.opened.connect(cells._bell_open.bind(latch,str(l.id)));cells.latches.append(latch)
