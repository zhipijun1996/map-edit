extends SceneTree
func _initialize() -> void:
 var motor:=PlayerMotor.new()
 print('NATIVE_MOTOR_MARGIN '+JSON.stringify({'safe_margin':motor.safe_margin,'class':'PlayerMotor','physics_frames':0,'scope':'Original constructor property only; not gameplay validation'}))
 motor.free();quit()
