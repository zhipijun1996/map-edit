"""Bind corrected read-only driver; retain every earlier diagnostic."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from .prepare_review029_v1 import AUTH

def apply(row):
 f=core.REPO/row['outputDirectory'];cases=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v4-cases.json',dict(cases=cases))
 for c in cases:c['generation_rule']['registration_source']='pcg/manual_review/review029_author_v3.py'
 core.write(f/'cases.json',dict(cases=cases));doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cases);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
