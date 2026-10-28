extends "../../workshop/main.gd"
const DOCK=preload("../machinery/dock_binding_v11.gd")
const MOUNT=preload("../batch30_d05/mount_v1.gd")
const OBS=preload("observe_v1.gd")
const DRAW=preload("../batch30_runtime/block_draw_v1.gd")
func rebuild(new_mode: String) -> void:
 var i:=selection.selected
 var source: Dictionary=cases[i]
 cases[i]=DOCK.masked(source)
 await super.rebuild(new_mode)
 cases[i]=source;case_data=source
 DOCK.install(self,source);MOUNT.install(self,source);display.case_data=source
 var overlay:=DRAW.new();overlay.data=source;world.add_child(overlay);overlay.z_index=85
 display.set_process(false)
 var viewport:=get_viewport_rect().size
 var factor: float=minf((viewport.x-60)/1664.0,(viewport.y-205)/1152.0)
 display.camera.zoom=Vector2.ONE*factor;display.camera.position=Vector2(832,576-76/factor)
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0
 super.capture_dynamic_frame()
 if active and not replay_trace.is_empty():
  replay_trace[-1].workshop.mounted_bells=MOUNT.snapshot(self)
  replay_trace[-1].n13={"docks":OBS.docks(self)}
