extends Node
static func read(cells) -> Array:
 var rows: Array=[]
 for latch: ShotLatch in cells.latches:
  var access: Array=[]
  for i: int in latch.access_bodies.size():access.append({"position":[latch.to_global(latch.access_positions[i]).x,latch.to_global(latch.access_positions[i]).y],"layer":latch.access_bodies[i].collision_layer})
  rows.append({"id":latch.link_id,"bell_layer":latch.bell_body.collision_layer,"gate_layer":latch.gate_body.collision_layer,"gate_disabled":latch.gate_shape.disabled,"open":latch.is_open,"count":latch.open_count,"clock":latch._clock,"opened_at":latch._opened_at,"access":access})
 return rows
