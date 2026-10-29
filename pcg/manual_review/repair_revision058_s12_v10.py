"""Leave P before its solid crossing, use direct native jumps and two observed TOP approaches."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_revision058_v2 import jump
from .prepare_ideas_v1 import settle
from .repair_revision058_s12_v1 import follow,win,on,boardL,boardB,boardR,actor

def group(p,mode):
 for v in p:v['route_mode']=mode;v.setdefault('trigger',{}).setdefault('state','revision_always')
 return p

def clear(a):
 x,y=(540,78)if a=='R'else(448,462)if a=='B'else(108,334)
 return at(x,y)+[dict(op='wait',enemy='transfer-air-enemy',guard_x=x,high_shore=a=='R',trigger=dict(after=1,state='revision_clear',timeout=1200))]
def toR(p):return[follow(p,30),win(dict(id=p,ymin=300,ymax=320,up=True))]+jump(616,24,[-.8,.6])
def toL():return[follow('P',-30),win(dict(id='P',ymin=230,ymax=250))]+jump(24,24)
def toT():
 choose=dict(op='wait',trigger=dict(after=1,state='revision_select_top',timeout=1200))
 direct=jump(192,24,[0,1])+at(192,14)
 via=[settle(120),cmd('jump'),cmd('jump_release',24),dict(op='shoot',direction=[-.5,.866025404],height_threshold=190,trigger=dict(after=1,state='descending_shot_height',timeout=180)),cmd('wait',8),follow('Q'),on('Q'),win(dict(id='Q',ymax=160,xmax=210))]+jump(192,24)+at(192,14)
 return[follow('P',-30),choose]+group(direct,'direct')+group(via,'via')
def apply():
 r=next(r for r in rows()if label(r)=='s12');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-s12-v10.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=[]
  if a=='T':p=[cmd('drop_through',1),settle(90)]+at(90,334);a='L'
  p+=clear(a)
  if z=='B':p+=(at(90,334)+jump(448,24,[-1,0])if a=='L'else[settle(448)])
  elif a=='L'and z=='L':pass
  elif a=='B'and z=='L':p+=at(400,462)+[axis(0),cmd('jump'),actor(ymax=390),settle(24),cmd('jump_release',16),cmd('shoot',4,direction=[.9,.435889894])]
  else:
   if a=='L':p+=boardL();support='P'
   elif a=='R':p+=boardR();support='P'
   else:p+=boardB();support='Q'
   if z=='T':
    if support=='P':p+=toT()
    else:p+=[follow('Q'),win(dict(id='Q',ymax=160,xmax=210))]+jump(192,24)
   elif z=='R':p+=toR(support)
   else:p+=toL()
  c.update(control_plan=p+end(*g),id=c['id']+'-v10');c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v10.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':apply()
