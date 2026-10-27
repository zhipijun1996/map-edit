extends RefCounted
static func docks(owner) -> Array:
 var rows: Array=[]
 for latch: ShotLatch in owner.cells.latches:
  if not latch.has_method("configure_dock"):continue
  var actual: Array=[]
  for body: Node2D in latch.sensor.get_overlapping_bodies():
   if body is ModuleMovingPlatform:actual.append(str(body.definition.platform_id))
  rows.append({"id":latch.link_id,"open":latch.is_open,"gate_layer":latch.gate_body.collision_layer,"gate_disabled":latch.gate_shape.disabled,"occupied":latch.last_occupied,"actual_Area2D_platform_bodies":actual,"clock":latch._clock,"opened_at":latch._opened_at})
 return rows
