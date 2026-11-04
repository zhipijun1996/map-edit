"""Aim inside real lower bell receiver below shield corner; preserve high-shore body margin."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from .continue_revision058_v1 import rows,label

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-v9.json',dict(cases=cs))
 for c in cs:
  if n=='s07':
   for v in c['control_plan']:
    if v.get('native_aim_point'):v['native_aim_point']=[340,280]
  elif n=='s12'and c['route_spec']['from_port']=='R':
   c['control_plan'][0]['target_x']=540;c['control_plan'][1]['trigger']['migration_goal']=[536,75,8,6];c['control_plan'][2]['guard_x']=540
  c['id']+='-v9'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
