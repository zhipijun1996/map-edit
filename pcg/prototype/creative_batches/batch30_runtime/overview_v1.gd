extends RefCounted
## Presentation-only framing. No actor, collision, input or resource writes.
static func install(owner, region: Rect2) -> void:
	if not owner.prepared or not is_instance_valid(owner.display):return
	owner.display.set_process(false)
	var viewport: Vector2=owner.get_viewport_rect().size
	var factor: float=minf((viewport.x-70)/region.size.x,(viewport.y-215)/region.size.y)
	owner.display.camera.zoom=Vector2.ONE*factor
	owner.display.camera.position=region.get_center()-Vector2(0,78/factor)
	owner.display.queue_redraw()
