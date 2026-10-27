extends RefCounted
static func snapshot(owner) -> Array:
 var out: Array=[]
 for latch in owner.cells.latches:
  if latch.sequence_offset.is_zero_approx():continue
  out.append({"id":latch.link_id,"sequence_step":latch.sequence_step,"open":latch.is_open,"first_gate_layer":latch.sequence_gate_body.collision_layer,"first_gate_disabled":latch.sequence_gate_shape.disabled,"final_gate_layer":latch.gate_body.collision_layer,"final_gate_disabled":latch.gate_shape.disabled,"primary_receiver_layer":latch.bell_body.collision_layer,"second_receiver_layer":latch._second_body.collision_layer})
 return out
