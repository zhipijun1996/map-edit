"""Stay fully outside Q's solid side before real upward recoil; direct TOP approach at172."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .continue_revision058_v1 import rows,label

def apply():
 r=next(r for r in rows()if label(r)=='s12');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-s12-v11.json',dict(cases=cs))
 for c in cs:
  for v in c['control_plan']:
   if v.get('route_mode')=='via'and v['op']=='shoot':v['direction']=[0,1];v['trigger']['state']='revision_transfer_shot'
   if v.get('route_mode')=='direct'and v['op']=='settle':v['target_x']=172
  c['id']+='-v11';c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v11.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':apply()
