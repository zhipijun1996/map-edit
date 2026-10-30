extends "revision063_lift_runner_v7.gd"
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 # Multiple commands can execute in one frame. The following settle must not
 # hide the actual jump's recorded takeoff height from the height trigger.
 for command: Dictionary in fired_commands:
  if int(command.index)==16 and command.op=='jump' and int(command.frame)==frame:
   r063_transfer_takeoff=float(command.position[1]);break
 return requests
