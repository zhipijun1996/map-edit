extends "../../migration/runtime/package_demo_v5.gd"
## Film the actual compiled playable host. Only camera/UI and post-validation tail.
const PORT_OVERLAY=preload("revision053_overlay_v2.gd")
var tailing:=false
var movie_bounds: Rect2
func _ready() -> void:
 var args:=OS.get_cmdline_user_args()
 for i: int in args.size():
  if args[i]=="--native-scene" and i+1<args.size():scene_file_path=args[i+1]
 super._ready()
 if not prepared:return
 var b: Dictionary=case_data.approved_implementation.rectangle
 movie_bounds=Rect2(b.x,b.y,b.w,b.h)
 if case_data.get("legal_port_mouths",[]).any(func(p):return p.face=="TOP"):
  movie_bounds.position.y-=96;movie_bounds.size.y+=96
 var overlay=PORT_OVERLAY.new();overlay.data=case_data;overlay.z_index=86;world.add_child(overlay)
 _frame_camera()
func _frame_camera() -> void:
 camera.position=movie_bounds.get_center()
 var v:=get_viewport_rect().size
 camera.zoom=Vector2.ONE*minf((v.x-180)/movie_bounds.size.x,(v.y-180)/movie_bounds.size.y)
func capture_dynamic_frame() -> void:
 if tailing:return
 super.capture_dynamic_frame()
 if prepared:_frame_camera();label.text+="\n实际编译场景 · 60 FPS · 原始输入 · 结尾冻结1秒 · 人工试玩UNKNOWN"
func _finish() -> void:
 if tailing:return
 tailing=true;context.freeze();world.process_mode=Node.PROCESS_MODE_DISABLED
 await get_tree().create_timer(1.0).timeout
 super._finish()
