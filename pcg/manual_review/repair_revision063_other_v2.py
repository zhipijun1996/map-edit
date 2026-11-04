"""Repair the concrete calibration failures; no holdout conditions observed."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from .continue_revision063_v1 import rows,label
from .prepare_ideas_v1 import settle
from .prepare_review045_v1 import at
from .prepare_revision060_v1 import follow,supported
def main():
 for r in rows():
  n=label(r)
  if n not in ['s04','s06','s09','lift']:continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
  for c in cs:
   p=c['control_plan'];a=c['route_spec']['from_port']
   if n=='s04':
    if a=='B':
     clear=copy.deepcopy(p[3]);clear['guard_x']=240
     p=at(280,846)+p[4:19]+[follow('P',-32),supported('P'),clear]+p[19:]
    else:
     clear=dict(op='wait',enemy='lower-air-enemy',guard_x=240,trigger=dict(after=1,state='revision_clear',timeout=1800))
     p=p[:20]+[follow('P',-32),supported('P'),clear]+p[20:]
   if n=='s06':
    c['generation_rule']['registration_source']='pcg/manual_review/revision063_s06_author_v1.py'
    j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r062_mount_corner_shot')
    assert p[j-1].get('trigger',{}).get('state')=='observed_height'
    p.pop(j-1);j-=1;p[j]['trigger']=dict(after=0,state='r063_mount_shot',timeout=180)
    state=dict(op='wait',r063_shot_index=j,r063_restart_index=j-1,trigger=dict(after=1,state='r063_mount_started',timeout=1800));p.insert(j+3,state)
   if n=='s09':
    c['generation_rule']['registration_source']='pcg/manual_review/revision063_s09_author_v1.py'
    if a=='L':
     j=next(i for i,v in enumerate(p)if v['op']=='drop_through');p=p[:j]+[settle(320),dict(op='wait',enemy='middle-air-enemy',guard_x=320,trigger=dict(after=1,state='revision_clear',timeout=1200))]+p[j:]
   if n=='lift':c['generation_rule']['registration_source']='pcg/manual_review/revision063_lift_author_v1.py'
   c['control_plan']=p
  core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True);print(n,'REVISED',flush=True)
if __name__=='__main__':main()
