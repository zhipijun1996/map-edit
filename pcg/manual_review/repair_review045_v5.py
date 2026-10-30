"""Fifth bounded controls; preserve the real single airborne shot capacity."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,wait_x
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,hook,height,axis
from .repair_review040_v5 import safe_kill
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v5-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='50'and a=='C':p=at(385,342)+jump(300,332,hold=4)+[cmd('jump'),cmd('grapple',1,aim_target=[120,155]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),axis(-1),wait_x(180,-1),axis(0)]+hook([188,-40],0)+[cmd('shoot',direction=[-.98 if z=='exit'else .98,.199])]+end(*goal)
  elif n=='55':p=at(130,-42)+[dict(op='settle',target_x=380,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),cmd('grapple',0,aim_target=[330,-28]),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+at(380,-42)+end(*goal)
  elif n in {'51','52'}:
   if a=='entry':
    p=at(-368,-318)+[axis(0),cmd('shoot',direction=[-1,0]),cmd('wait',9),dict(op='settle',target_x=110,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',5),cmd('wait',2),axis(0)]+hook([-35,-350],0)+[cmd('shoot',direction=[-1,0])]+at(110,-294)
    if n=='51':p+=[cmd('jump'),cmd('grapple',1,aim_target=[330,-350]),cmd('jump_release',4),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]
    else:p+=hook([310,-260],0)
    p+=[cmd('shoot',direction=[-1,0])]+end(*goal);c['expected_hook_sequence']=['cavity_ring_a','cavity_ring_b']
   else:
    # Last experimental reverse approach: get to the left of the anchor before
    # the real cast, retaining the sole shot for the final departure.
    from .repair_review045_v4 import falling
    p=at(466,-318 if n=='51'else-190)+hook([330,-350]if n=='51'else[310,-260],0)
    if n=='51':p+=[axis(-1),falling(-345),cmd('shoot',direction=[.9797958971,.2])]
    else:p+=[cmd('shoot',direction=[.9367496998,.35])]
    p+=at(110,-294)+at(52.7,-294)+[axis(-1),cmd('jump'),cmd('jump_release',9),wait_x(-48,-1),axis(0)]+hook([-35,-350],0)+[cmd('shoot',direction=[1,0])]+end(*goal);c['expected_hook_sequence']=['cavity_ring_b','cavity_ring_a']
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v4','review045-v5').replace('review045-v3','review045-v5')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
