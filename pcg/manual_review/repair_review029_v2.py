"""Bounded second control revision; keep geometry and previous raw intact."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review029_v1 import AUTH,at,end
from .prepare_review_refresh_v1 import leap

def phase(id,window,timeout=900):return dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=id,window=window),timeout=timeout))
def axis(v):return dict(op='axis',value=v,cancel_settle=True,trigger=dict(after=0))
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];doc=core.read(f/'module.mapnote.json');cases=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cases));core.write(f/'history/pre-repair-v2-module.json',doc)
 for c in cases:
  for v in c['control_plan']:
   if v['op']=='axis':v['cancel_settle']=True
  if n in ('161','163'):
   port=next(p for p in doc['generationContract']['ports']if p['id']=='exit');port['stagingPosition']=[496,282]
   c['exit_port']=[496,282];c['goal']=[489,278,14,8];next(p for p in c['ports']if p['id']=='exit')['position']=[496,282]
   for v in c['control_plan']:
    if v['op']=='settle'and v['target_x']==488:v['target_x']=496
    if v.get('trigger',{}).get('migration_goal')==[483,278,10,8]:v['trigger']['migration_goal']=[491,278,10,8]
  if n=='175':
   for v in c['control_plan'][:2]:
    if v['op']=='settle':v['target_x']=700
    else:v['trigger']['migration_goal']=[695,416,10,8]
  if n=='193'and c['route_spec']['from_port']=='exit':
   c['control_plan']=at(1450,420)+phase('carrier',[.42,.44])+leap(1050,420,release=320,shot=[.97,.243])+at(1030,420)+leap(730,227,shot=[.5,.8660254])+at(730,227)+phase('carrier',[.8,.82])+[axis(-1),cmd('jump'),cmd('jump_release',8),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='carrier'),timeout=240)),axis(0),cmd('wait',12),axis(-1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[.97,.243])]+end(152,420)
  c['id']=c['id'].replace('review029-v1','review029-v2')
 doc=godot_package.bind_case_behavior(doc,cases);core.write(f/'cases.json',dict(cases=cases));core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 import sys
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
