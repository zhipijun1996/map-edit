"""Twelve directed controls using actual P/Q support and original motion forecasts."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_revision058_v2 import jump
from .prepare_ideas_v1 import settle

def follow(p,offset=0):return dict(op='settle',target_x=320,revision_follow=p,carrier_offset=offset,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def win(*q):return dict(op='wait',windows=list(q),trigger=dict(after=1,state='revision_window',timeout=1200))
def on(p):return dict(op='wait',carrier=p,trigger=dict(after=1,state='carrier_supported',timeout=300))
def actor(**kw):return dict(op='wait',**kw,trigger=dict(after=1,state='revision_actor',timeout=180))
def boardL():return at(90,334)+[axis(0),win(dict(id='P',ahead=.6,ymin=330,xmax=240,up=True)),follow('P'),cmd('jump'),cmd('jump_release',8),on('P')]
def boardB():return at(500,462)+[axis(0),win(dict(id='Q',ymin=414),dict(id='Q',ahead=.5,ymin=380,up=True)),cmd('jump'),actor(ymax=380),follow('Q'),cmd('jump_release',16),on('Q')]
def boardR():return at(560,78)+[axis(0),win(dict(id='P',ymax=160),dict(id='P',ahead=.5,ymax=175)),cmd('shoot',direction=[.98,.1989974874]),follow('P'),on('P')]
def QtoP():return[follow('Q'),win(dict(id='Q',ymax=160),dict(id='P',ahead=.6,ymin=240,ymax=340)),follow('P'),on('P')]
def PtoQ():return[follow('P'),win(dict(id='P',ymin=370,ymax=390,up=True),dict(id='Q',ahead=.9,xmax=240,ymax=200)),settle(110),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[0,1]),cmd('wait',12),follow('Q'),on('Q')]
def apply():
 r=next(r for r in rows()if label(r)=='s12');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-s12-v1.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=[]
  if a=='T':p=[cmd('drop_through',1),settle(90)]+at(90,334);a='L'
  if z=='B':p+=(at(90,334)+jump(448,24,[-1,0])if a=='L'else[settle(448)])
  elif a=='L'and z=='L':pass
  else:
   if a=='L':p+=boardL();support='P'
   elif a=='R':p+=boardR();support='P'
   else:p+=boardB();support='Q'
   if z=='T':
    if support=='P':p+=PtoQ()
    p+=[follow('Q'),win(dict(id='Q',ymax=160,xmax=210))]+jump(192,24)
   else:
    if support=='Q':p+=QtoP()
    if z=='R':p+=[follow('P',24),win(dict(id='P',ymax=145))]+jump(616,1)
    else:p+=[follow('P',-24),win(dict(id='P',ymin=390,xmax=200))]+jump(24,8)
  c.update(control_plan=p+end(*g),id=c['id']+'-s12-v1');c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v4.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':apply()
