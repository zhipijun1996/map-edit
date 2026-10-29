import sys
from pcg.migration import core,godot_package,physics
from .continue_revision059_v1 import rows,label,AUTH
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump
from pcg.prototype.workshop.rules import cmd

def save(r,cs,version):
 f=core.REPO/r['outputDirectory'];d=core.read(f/'module.mapnote.json');core.write(f/'control-history'/('before-'+version+'.json'),dict(cases=core.read(f/'cases.json')['cases']));core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
def main():
 for r in rows():
  n=label(r)
  if n not in sys.argv[1:]:continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases']
  for c in cs:
   a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=c['control_plan']
   if n=='s02':
    c['generation_rule']['registration_source']='pcg/manual_review/revision059_repair_author_v2.py'
    if a=='B':
     i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='repair_takeoff');p=p[:i+1]+jump(64,24,[0,1])+end(*g)
   if n=='hq01':
    if a=='L':p=p[:next(i for i,v in enumerate(p)if v.get('carrier')=='Q')+1]
    elif a=='R':p=at(550,78)+[settle(368),dict(op='wait',carrier='Q',trigger=dict(after=1,state='carrier_supported',timeout=360))]
    else:p=[settle(368),cmd('jump'),cmd('jump_release',1),dict(op='wait',carrier='Q',trigger=dict(after=1,state='carrier_supported',timeout=360))]
    if z=='R':p+=jump(580,24,[-1,0])+end(*g)
    elif z=='T':p+=jump(192,24)+[dict(op='shoot',direction=[0,1],trigger=dict(after=1,state='hq_top_aligned',timeout=120))]+end(*g)
    else:p+=jump(24,8)+end(*g)
   if n=='hq02':
    if a=='B':p=[dict(op='wait',trigger=dict(after=1,state='hq_board',timeout=1800)),settle(200),cmd('jump'),cmd('jump_release',24),dict(op='wait',carrier='P',trigger=dict(after=1,state='carrier_supported',timeout=360)),dict(op='settle',target_x=120,revision_follow='P',carrier_offset=-24,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(after=1,state='hq_upper',timeout=1800))]+jump(64,24)+end(*g)
    else:p=[cmd('drop_through',1),settle(160),dict(op='wait',height_threshold=370,trigger=dict(after=1,state='descending_height',timeout=240)),settle(260)]+end(*g)
   c['control_plan']=p
  save(r,cs,'v2')
if __name__=='__main__':main()
