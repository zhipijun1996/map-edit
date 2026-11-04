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
 for r in rows():
  n=label(r)
  if n not in ['hq01','hq02','hq05']:continue
  cs=core.read(core.REPO/r['outputDirectory']/'cases.json')['cases']
  for c in cs:
   a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=c['control_plan']
   if n=='hq01':
    k=next(i for i,v in enumerate(p)if v.get('carrier')=='Q');p=p[:k+1]
    if a=='T':p.insert(5,dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='gte',value=240),timeout=120)))
    if z=='R':p+=jump(580,8,[-.98,.1989974874])+at(580,78)+end(*g)
    elif z=='T':p+=jump(192,24)+[dict(op='shoot',direction=[0,1],trigger=dict(after=1,state='hq_top_aligned',timeout=120))]+end(*g)
    else:p+=[dict(op='settle',target_x=256,revision_follow='P',deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',carrier='P',trigger=dict(after=1,state='carrier_supported',timeout=360)),settle(24),dict(op='wait',observed_y=dict(direction='gte',value=290),trigger=dict(after=1,state='observed_height',timeout=180)),cmd('shoot',1,direction=[1,0])]+end(*g)
   if n=='hq02'and a=='T':p=[axis(0),cmd('drop_through',1),settle(96)]+at(96,338)+jump(256,24)+at(256,462)+end(*g)
   if n=='hq05'and a=='T':p=[axis(0),cmd('shoot',1,direction=[0,1])]+at(448,14)+[cmd('drop_through',1),dict(op='wait',observed_y=dict(direction='gte',value=92),trigger=dict(after=1,state='observed_height',timeout=180)),settle(448)]+at(448,94)+[cmd('drop_through',1),dict(op='wait',observed_y=dict(direction='gte',value=150),trigger=dict(after=1,state='observed_height',timeout=180)),settle(336)]+at(336,270)+at(270,270)+jump(24)+end(*g)
   c['control_plan']=p
  save(r,cs,'v4')
if __name__=='__main__':main()
