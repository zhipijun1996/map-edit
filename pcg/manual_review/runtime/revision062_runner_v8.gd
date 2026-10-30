extends "revision062_runner_v7.gd"
var r062_retry_serial:=0
var r062_retry_ready:=-1
func control_plan(frame: int) -> Array:
 var requests:=super.control_plan(frame)
 if plan_index<=0 or plan_index>=plan.size():return requests
 var c: Dictionary=plan[plan_index];var previous: Dictionary=plan[plan_index-1]
 if c.get('trigger',{}).get('state','')!='r062_running'or previous.op!='shoot'or previous.get('group_id','')!=c.get('group_id','')or condition_met('r062_running'):return requests
 if condition_met('r062_ring'):
  var key: int=62000+r062_retry_serial
  if r062_retry_ready<0:r062_retry_ready=frame+maxi(0,1+timing_error(key))
  if frame>=r062_retry_ready:
   var d:=disturbed_direction(Vector2(c.direction[0],c.direction[1]),key);controller.router.request_action(&'shoot_release',d);requests.append({'type':'shoot_release','direction':[d.x,d.y],'plan_index':plan_index,'noise_key':key});r062_retry_serial+=1;r062_retry_ready=-1
 return requests
