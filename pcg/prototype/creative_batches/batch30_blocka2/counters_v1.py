"""Exact unchanged-world A2 counter policies; same physical version per route."""
import copy,itertools,math
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle

def alternatives(base):
 out=[]
 def add(label,plan):
  c=copy.deepcopy(base);c['id']+='-counter-'+label;c['counterexample_kind']=label;c['control_plan']=plan;out.append(c)
 end=base['exit_port'][0];start=base['moving_platforms'][0]['start'][0]
 if base['route_spec']['from_port']=='A':
  takeoff=base['platforms'][0][0]+base['platforms'][0][2]-12
  # Two ordinary jumps use the parked start dock, then a single paid recoil.
  for hold,dy,last in itertools.product([12,20],[.4,.8660254037844386],[12,24]):
   lead=start+144-24
   plan=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='chase-carrier'),timeout=180)),cmd('axis',value=1),wait_x(lead),cmd('jump'),cmd('jump_release',last),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(end,6)]
   add(f'parked-dock-{hold}-{dy}-{last}',plan)
  for j,q in enumerate(base['control_plan']):
   if q['op']=='shoot':
    plan=copy.deepcopy(base['control_plan']);plan[j]=dict(op='wait',trigger=copy.deepcopy(q.get('trigger',{})));add('omit-shot-'+str(j),plan)
  for hold in [0,8,20,30]:
   for inset in [12,40]:
    add(f'ordinary-direct-{hold}-{inset}',[cmd('axis',value=1),wait_x(takeoff-inset),cmd('jump'),cmd('jump_release',hold),settle(end,6)])
  for receiver in ['primary','access']:
   add('ground-prefire-'+receiver,[cmd('shoot',aim_cell=dict(kind='bell',id='carrier-bell',receiver=receiver))]+copy.deepcopy(base['control_plan']))
  add('passive-wait',[cmd('axis',value=0),cmd('wait',800),settle(end)])
 else:
  left=base['platforms'][1][0]
  for hold,inset in itertools.product([0,8,20,30],[0,24,48]):
   add(f'ordinary-return-{hold}-{inset}',[cmd('axis',value=-1),wait_x(left+inset,-1),cmd('jump'),cmd('jump_release',hold),settle(end,6)])
  for hold,dy in itertools.product([8,20,30],[0,.8]):
   add(f'one-shot-direct-return-{hold}-{dy}',[cmd('axis',value=-1),wait_x(left+24,-1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[math.sqrt(1-dy*dy),dy]),settle(end,6)])
  add('walk-off-no-shot',[cmd('axis',value=-1),settle(end,6)])
  add('early-ground-bell',[cmd('shoot',aim_cell=dict(kind='bell',id='carrier-bell',receiver='access'))]+copy.deepcopy(base['control_plan']))
 return out
