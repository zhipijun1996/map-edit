if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core
from .continue_revision059_v1 import rows,label
from .revise_revision059_v2 import save
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump
from .prepare_review045_v1 import at,end,axis
from pcg.prototype.workshop.rules import cmd

def main():
 r=next(r for r in rows()if label(r)=='s12');cs=core.read(core.REPO/r['outputDirectory']/'cases.json')['cases']
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision059_s12_author_v1.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
  if z=='B' or a=='T'and z=='L' or a=='B'and z=='L':continue
  cut=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='revision_clear');prefix=p[:cut+1]
  if a in ['L','T']:
   prefix+=at(90,334)+[axis(0),dict(op='wait',trigger=dict(after=1,state='repair_s12_left_q',timeout=1800)),dict(op='settle',target_x=270,revision_follow='Q',deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',8),cmd('shoot',4,direction=[-.6,.8]),dict(op='wait',carrier='Q',trigger=dict(after=1,state='carrier_supported',timeout=360))]
  elif a=='R':
   prefix+=at(560,78)+[settle(368),dict(op='wait',observed_y=dict(direction='gte',value=110),trigger=dict(after=1,state='observed_height',timeout=180)),cmd('shoot',1,direction=[1,0]),dict(op='settle',target_x=270,revision_follow='Q',deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',carrier='Q',trigger=dict(after=1,state='carrier_supported',timeout=600))]
  else:
   k=next(i for i,v in enumerate(p)if v.get('carrier')=='Q');prefix=p[:k+1]
  prefix+=[dict(op='settle',target_x=270,revision_follow='Q',deadband=.6,source_native_gain=5.5,trigger=dict(after=0))]
  if z=='T':prefix+=[dict(op='wait',windows=[dict(id='Q',ymax=160,xmax=210)],trigger=dict(after=1,state='revision_window',timeout=1800))]+jump(192,24)
  elif z=='R':prefix+=[dict(op='wait',windows=[dict(id='Q',ymax=200,ymin=185,up=True)],trigger=dict(after=1,state='revision_window',timeout=1800))]+jump(580,24,[-1,0])+at(580,78)
  else:prefix+=[dict(op='wait',windows=[dict(id='Q',ymax=205,ymin=185,up=True)],trigger=dict(after=1,state='revision_window',timeout=1800))]+jump(24,24)
  c['control_plan']=prefix+end(*c['exit_port'])
 save(r,cs,'v1-repair')
if __name__=='__main__':main()
