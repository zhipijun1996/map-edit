extends Node
## Read-only original receiver and gate collision state.
static func read(cells) -> Array:
 var rows: Array=[]
 for latch: ShotLatch in cells.latches:
  rows.append({"id":latch.link_id,"bell_layer":latch.bell_body.collision_layer,"gate_layer":latch.gate_body.collision_layer,"gate_disabled":latch.gate_shape.disabled,"open":latch.is_open,"count":latch.open_count,"clock":latch._clock,"opened_at":latch._opened_at})
 return rows
