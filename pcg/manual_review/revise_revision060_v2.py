if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .continue_revision060_v1 import rows,label
from .prepare_revision060_v1 import wait,follow,supported,aim
from .prepare_revision058_v2 import jump
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from pcg.prototype.workshop.rules import cmd

def save(r,cs,v):
 f=core.REPO/r['outputDirectory'];core.write(f/'control-history'/('before-'+v+'.json'),core.read(f/'cases.json'));doc=core.read(f/'module.mapnote.json');core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
def main():
 for r in rows():
  n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases']
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v2.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];g=c['exit_port']
   if n=='hq01':
    for v in p:
     if v.get('trigger',{}).get('state')=='r060_carrier_height'and v.get('carrier')=='Q'and v.get('supported'):v['trigger']['state']='r060_q_park_ready'
   if n=='hq02':
    if a=='B':
     p=[wait('r060_carrier_height',carrier='P',ymax=250)]+at(300,462)+jump(144,24)+at(144,338)+at(100,334)
     for i in range(6):
      loop=[wait('r060_lure_window'),settle(144),wait('r060_seed',timeout=600),settle(100),cmd('wait',60)]+at(100,334)
      for v in loop:v['interception_loop']=True
      loop[0]['interception_loop_start']=True;p+=loop
     p +=[wait('r060_intercepted',timeout=60)]
    else:p=[axis(0),cmd('drop_through',1),settle(144)]+at(144,338)+at(100,334)
    p +=[wait('revision_clear',enemy='sentry',guard_x=100,high_shore=False,timeout=1200)]+at(144,338)+[wait('r060_carrier_height',carrier='P',ymin=385),follow('P',-24),cmd('jump'),cmd('jump_release',8),supported('P'),follow('P',-24)]
    if z=='T':p +=[wait('r060_carrier_height',carrier='P',supported=True,ymax=165)]+jump(64,24)+end(*g)
    else:p +=[wait('r060_carrier_height',carrier='P',supported=True,ymin=405),settle(300),wait('observed_height',observed_y=dict(direction='gte',value=365),timeout=180),settle(320)]+end(*g)
   if n=='hq03':
    if a=='L':p=at(84,206)+[settle(180)]+at(180,270)
    elif a=='R':p=at(460,206)+[settle(364)]+at(364,270)+jump(332,8)+at(332,238)
    else:p=[axis(0),cmd('drop_through',1),settle(332)]+at(332,238)
    if a=='L':p +=[wait('revision_clear',enemy='charger',guard_x=180,high_shore=False,allow_partial=True,timeout=1200)]+jump(332,8)+at(332,238)
    p +=[wait('revision_clear',enemy='charger',guard_x=332,high_shore=False,timeout=1200)]
    if z=='T':p+=at(320,238)+jump(320,8,[0,1])
    elif z=='L':p+=[settle(180)]+at(180,270)+at(132,270)+jump(24,8)
    else:p+=[settle(420)]+at(420,270)+jump(488,8)
    p+=end(*g)
   if n=='hq07'and a=='R':
    for v in p:
     if v.get('direction')==[-1,0]:v['direction']=[1,0]
   if n=='hq08':
    if a=='L':p=at(90,334)+jump(320,8,[-.9539392014,.3])+[supported('P'),follow('P'),wait('r060_08_exit')]+jump(320,24,[0,1])+end(*g)
    else:p=[axis(0),wait('r060_08_drop_clear'),cmd('drop_through',1),supported('P')]+jump(100,1,[1,0])+end(*g)
   if n=='hq09'and a=='L':p=at(72,334)+[aim(72,288),wait('r060_barrier_clear')]+at(100,334)+[aim(176,352),wait('r060_bell_open',bell_id='target-bell',timeout=180)]+at(100,334)+jump(184,8)+at(184,270)+jump(176,24)+at(176,142)+jump(192,24)+end(*g)
   c['control_plan']=p
  save(r,cs,'v2')
if __name__=='__main__':main()
