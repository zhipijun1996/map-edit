extends "revision063_lift_runner_v8.gd"
## The transfer boost crosses G3 before landing. Check that earlier crossing,
## then the FIRST upcoming upward launch window, including a downward ferry.
func upper_choice(after: float) -> String:
 var early_left:=true;var early_right:=true
 for extra: float in [-.65,-.55,-.45,-.35,-.25]:
  var x:=gear_x('G3',maxf(0,after+extra))
  early_left=early_left and x<112;early_right=early_right and x>272
 if not early_left and not early_right:return ''
 for id: String in ['L2','R2']:
  var p=carrier(id)
  if p.definition.at_time(context.module.clock+after).y<380:continue
  var window_seen:=false
  for step: int in range(0,180):
   var dt:=after+float(step)/20
   var y: float=p.definition.at_time(context.module.clock+dt).y
   var up: bool=p.definition.at_time(context.module.clock+dt+.05).y<y
   if window_seen and y<330:break
   if not up or y<335 or y>375:continue
   window_seen=true
   var safe:=true
   for padding: float in [.15,.25,.35,.45,.55]:
    var x:=gear_x('G3',dt+padding)
    if (id=='L2' and x<260) or (id=='R2' and x>124):safe=false
   if safe:return id
 return ''
