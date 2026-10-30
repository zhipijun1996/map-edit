extends "revision060_runner_v2.gd"
var last_native_drop: int=-1000
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 if plan_index<plan.size()and current_case.get('approved_implementation',{}).get('reviewId','')=='idea-interface-s12-001'and motor.is_on_floor()and frame-last_native_drop>=12:
  var c: Dictionary=plan[plan_index];var support: String=str(context.snapshot().get('support_id',''));var target: Array=c.get('trigger',{}).get('migration_goal',[])
  if support in ['P','Q']and((c.get('trigger',{}).get('state','')=='carrier_supported'and c.get('carrier','')=='Q'and support=='P')or target.size()==4 and target[1]>450):
   controller.router.request_action(&'drop_through',Vector2.ZERO);requests.append({'type':'drop_through','direction':[0,0],'plan_index':plan_index});last_native_drop=frame
 return requests
