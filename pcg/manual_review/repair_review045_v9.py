"""Seventh 50 candidate: upward recoil across the upper bank gap."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .refresh_review045_v1 import rows

def apply(row):
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v9-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['from_port']=='exit'and c['route_spec']['to_port']=='entry':
   for v in c['control_plan']:
    if v['op']=='shoot':v['direction']=[.98,.199]
  c['id']=c['id'].replace('review045-v8','review045-v9')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':apply(next(r for r in rows()if r['reviewId']=='50'))
