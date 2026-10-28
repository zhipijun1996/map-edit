extends "../machinery/dock_runner_v11.gd"
const MOUNT=preload("../batch30_d05/mount_v1.gd")
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(data)
 MOUNT.install(self,data)
func observed() -> Dictionary:
 var rows: Array=[]
 for p: ModuleMovingPlatform in context.module.moving_platforms:
  rows.append({"id":str(p.definition.platform_id),"position":[p.position.x,p.position.y],"running":p.motion_running,"motion_clock":p.motion_clock,"relative_actor":[motor.position.x-p.position.x,motor.position.y-p.position.y]})
 return {"carriers":rows,"mounted_bells":MOUNT.snapshot(self)}
func capture_dynamic_frame() -> void:
 var active:=warmup_left==0
 super.capture_dynamic_frame()
 if active:captured[-1].n13=observed()
func run_case(data: Dictionary) -> Dictionary:
 var result: Dictionary=await super.run_case(data)
 if not result.get("rejected",false):result.n13=observed()
 return result
