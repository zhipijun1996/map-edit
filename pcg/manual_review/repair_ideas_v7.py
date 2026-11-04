"""Place the phase-wait dock fully outside the diver's original activation range."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .new_ideas_v1 import rows,label
from .prepare_review045_v1 import at

def main():
 r=next(r for r in rows()if label(r)=='enemies-3');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v7-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['id']=='A-to-B':c['control_plan']=at(284,590)+c['control_plan'][2:]
  c['id']=c['id'].replace('newideas-v9','newideas-v10')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
