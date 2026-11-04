"""Wait for the complete real recoil before taking the second hook from its right."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .continue_revision053_v1 import rows,label

def main():
 r=next(r for r in rows()if label(r)=='51');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v8-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['from_port']=='entry':
   wait=next(v for v in c['control_plan']if v.get('height_threshold')==-390);wait['trigger']['after']=14;c['id']+='-complete-burst'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
