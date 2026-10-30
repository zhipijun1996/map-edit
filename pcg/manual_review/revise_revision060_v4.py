if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core
from .continue_revision060_v1 import rows,label
from .revise_revision060_v2 import save
from .prepare_revision060_v1 import wait,follow,supported,group_wait,ring
from .prepare_revision058_v2 import jump
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from pcg.prototype.workshop.rules import cmd

def branch(p,mode):
 for c in p:c['route_mode']=mode
 return p

def main():
 for r in rows():
  n=label(r)
  if n=='hq09':continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases']
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v4.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];g=c['exit_port']
   if n=='hq01':
    if z=='R':
     for i,v in enumerate(p):
      if v.get('op')=='settle'and v.get('target_x')==580 and i+2<len(p)and p[i+2]['op']=='jump_release':p[i+2]['trigger']['after']=12
    if z=='L':
     k=next(i for i,v in enumerate(p)if v.get('target_x')==256 and v['op']=='settle');suffix=p[next(i for i in range(k,len(p))if p[i].get('ring_follow')):]
     close=[dict(op='settle',target_x=288,group_transfer_out=True,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),wait('r060_below_q',timeout=180),follow('P'),supported('P')]
     far=[follow('P'),cmd('jump'),cmd('jump_release',24),supported('P')]
     p=p[:k]+[wait('r060_group_transfer',timeout=90)]+branch(close,'close')+branch(far,'far')+suffix
   if n=='hq02':
    for v in p:
     if v.get('target_x')==100:v['target_x']=80
     if v.get('trigger',{}).get('migration_goal')==[96,331,8,6]:v['trigger']['migration_goal']=[76,335,8,6]
    k=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='revision_clear');p=p[:k]+at(148,338)+[wait('revision_clear',enemy='sentry',guard_x=148,high_shore=False,timeout=1200)]+p[k+1:]
   if n=='hq03':
    if a=='L':p=at(84,206)+[settle(180)]+at(180,270)
    elif a=='R':p=at(460,206)+[settle(364)]+at(364,270)
    else:p=[axis(0),cmd('drop_through',1),settle(320)]+at(320,94)+[axis(0),cmd('drop_through',1),settle(272)]
    p +=[settle(272),wait('r060_fight',enemy='charger',timeout=1800),settle(272),wait('r060_perch',timeout=600)]
    if z=='T':p+=at(320,238)+jump(320,8,[0,1])
    elif z=='L':p+=[settle(180)]+at(180,270)+at(132,270)+jump(24,8)
    else:p+=[settle(420)]+at(420,270)+jump(488,8)
    p+=end(*g)
   if n=='hq07'and a=='R':
    k=next(i for i,v in enumerate(p)if v.get('target_x')==110 and v.get('op')=='settle');p=p[:k]+at(452,334)+p[k:]
   if n=='s12'and z=='L':
    for v in p:
     if v.get('direction')==[.9,.435889894]:v['ensure_airborne']=True;v['trigger'].update(state='r060_air_shot',timeout=180)
   c['control_plan']=p
  save(r,cs,'v4')
if __name__=='__main__':main()
