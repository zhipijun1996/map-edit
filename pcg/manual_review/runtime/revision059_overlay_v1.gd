extends "revision053_overlay_v2.gd"
## Optional overlay adapts pre-freeze replay metadata; never changes scene/case data.
func _ready() -> void:
 if data.has('block_ports'):return
 data=data.duplicate(true);data.block_ports={}
 for p: Dictionary in data.ports:
  for mouth: Dictionary in data.get('legal_port_mouths',[]):
   if str(mouth.id)==str(p.id):data.block_ports[str(p.id)]={'position':mouth.position,'stagingPosition':p.position}
