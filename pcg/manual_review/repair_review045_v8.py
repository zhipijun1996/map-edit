"""Last 220 policy; close-range hook casts preserve original resources."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,hook,axis

def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v8-cases.json',dict(cases=cs))
 for c in cs:
  p=c['control_plan'];a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];goal=c['exit_port']
  if n=='220':
   for v in p:
    if v['op']=='shoot'and v.get('trigger',{}).get('state'):v['trigger']['after']=4
   if z=='C':
    i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')==680);p=p[:i]+at(575,562)+p[i:]
  elif n=='55':p=at(108,-42)+[axis(0),cmd('shoot',direction=[-1,0]),cmd('wait',9)]+hook([330,-48],0)+at(380,-42)+end(*goal)
  elif n=='50':
   if a=='C':
    i=next(i for i,v in enumerate(p)if v['op']=='grapple');p[i]['trigger']['after']=4
   elif a=='exit'and z=='entry':p=at(240,-42)+[axis(0)]+hook([200,-40],0)+[cmd('shoot',direction=[1,-.15])]+end(*goal)
  c['control_plan']=p;c['id']=c['id'].replace('review045-v7','review045-v8').replace('review045-v6','review045-v8').replace('review045-v5','review045-v8')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
