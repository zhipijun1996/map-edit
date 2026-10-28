extends Node2D
## Read-only native presentation overlay: inherited ShotLatch caption describes
## original start/pause; cover that plaque with truthful NEW reverse wording.
var latch: ShotLatch
func _process(_delta: float) -> void:queue_redraw()
func _draw() -> void:
	if not is_instance_valid(latch):return
	var at: Vector2=latch.bell_position+Vector2(-45,-100)
	draw_rect(Rect2(at,Vector2(430,32)),Color(.08,.15,.13,1.0))
	var west: bool=int(latch.motion_target.get("signed_direction"))<0
	var caption: String="WEST / HIT TO REVERSE EAST" if west else "EAST / HIT TO REVERSE WEST"
	draw_string(ThemeDB.fallback_font,at+Vector2(8,22),caption,HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("e8bd65"))
