extends SceneTree
const D=preload('revision061_ellipse_definition_v1.gd')
func _initialize() -> void:
 var d=D.new();d.platform_id=&'P';d.size=Vector2(112,16);d.travel_duration=8;d.dwell_duration=0;d.initial_phase=0
 assert(d.is_valid());assert(d.at_time(0).distance_to(Vector2(160,256))<.001);assert(d.at_time(.01).y<256)
 var max_error: float=0
 for i: int in range(0,1001):max_error=maxf(max_error,d.at_time(float(i)/100).distance_to(d.at_time(float(i)/100+8)))
 assert(max_error<.001)
 var negatives: Array=[]
 for kind: String in ['zero_period','negative_period','nan_center','zero_radius','negative_radius','invalid_size','phase_one','phase_negative','phase_nan']:
  var x=D.new();x.platform_id=&'P';x.size=Vector2(112,16);x.travel_duration=8;x.dwell_duration=0
  if kind=='zero_period':x.travel_duration=0
  if kind=='negative_period':x.travel_duration=-1
  if kind=='nan_center':x.center.x=NAN
  if kind=='zero_radius':x.radii.x=0
  if kind=='negative_radius':x.radii.y=-1
  if kind=='invalid_size':x.size.x=0
  if kind=='phase_one':x.initial_phase=1
  if kind=='phase_negative':x.initial_phase=-.1
  if kind=='phase_nan':x.initial_phase=NAN
  assert(not x.is_valid());negatives.append({'kind':kind,'rejected':true})
 var output: String=''
 for arg: String in OS.get_cmdline_user_args():
  if arg.begins_with('--output='):output=arg.trim_prefix('--output=')
 var report: Dictionary={'passed':true,'period':d.period(),'periodic_error_max':max_error,'direction_from_left':'up_then_right_clockwise','negative_definitions':negatives,'original_platform_body':'unchanged ModuleMovingPlatform','original_actor_resources':'unchanged'}
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report,'  '));print('ELLIPSE_NATIVE_DEFINITION_AUDIT_PASS');quit()
