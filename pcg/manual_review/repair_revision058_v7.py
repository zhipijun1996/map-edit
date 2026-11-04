"""Correct muzzle-origin aiming and original any-side access; real optional enemy clearing."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];d=core.read(f/'module.mapnote.json');core.write(f/'history/pre-v7.json',dict(module=d,cases=cs))
 for c in cs:
  p=c['control_plan'];a=c['route_spec']['from_port']
  if n=='s07':
   for v in p:
    if v.get('aim_point'):v['native_aim_point']=v.pop('aim_point')
  if n=='s12':
   x,y=(548,78)if a=='R'else(448,462)if a=='B'else(108,334)
   clear=at(x,y)+[dict(op='wait',enemy='transfer-air-enemy',guard_x=x,high_shore=a=='R',trigger=dict(after=1,state='revision_clear',timeout=1200))]
   if a=='T':i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')==[86,331,8,6]);p=p[:i+1]+clear+p[i+1:]
   else:p=clear+p
  c['control_plan']=p;c['id']+='-v7';c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v5.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
