extends "revision059_native_movie_v1.gd"
## Camera margin only: keep right-side native Port labels inside the frame.
func _frame_camera() -> void:
 if movie_bounds.size.x<=0:return
 var shown:=movie_bounds;shown.position.x-=32;shown.size.x+=192
 camera.position=shown.get_center();var viewport:=get_viewport_rect().size
 camera.zoom=Vector2.ONE*minf((viewport.x-180)/shown.size.x,(viewport.y-180)/shown.size.y)
