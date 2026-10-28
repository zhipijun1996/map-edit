extends "package_demo_v3.gd"
var air_exit_complete_frames:=0

func _ready() -> void:
	super._ready()
	if not prepared:return
	for port: Dictionary in case_data.get("air_port_contracts",[]):
		if port.id==case_data.get("route_spec",{}).get("from_port","") and port.permission=="INPUT":context.anchor_ready=true

func capture_dynamic_frame() -> void:
	var active:=warmup_left==0
	super.capture_dynamic_frame()
	if not active or captured.is_empty():return
	for port: Dictionary in case_data.get("air_port_contracts",[]):
		if port.id!=case_data.get("route_spec",{}).get("to_port","") or port.permission!="OUTPUT":continue
		var crossed:=motor.position.y-18>=float(port.position[1]) and motor.position.y<=float(port.position[1])+128 and absf(motor.position.x-float(port.position[0]))+12<=32 and motor.velocity.y>0
		air_exit_complete_frames=air_exit_complete_frames+1 if crossed else 0
		stable=air_exit_complete_frames
		captured[-1].air_exit_complete_frames=air_exit_complete_frames
		captured[-1].goal_contract="downward AIR crossing; not grounded stability"
