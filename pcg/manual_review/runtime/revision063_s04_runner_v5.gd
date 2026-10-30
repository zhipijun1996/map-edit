extends "revision063_s04_runner_v4.gd"
func condition_met(state: String) -> bool:
 if state=='r062_ring':
  var id: String=str(context.snapshot().get('support_id',''))
  if id in ['P','Q'] and settle_options.has('carrier_follow'):
   var p=carrier(str(settle_options.carrier_follow))
   if absf(motor.position.x-p.position.x-float(settle_options.get('carrier_offset',0)))>3:return false
 return super.condition_met(state)
