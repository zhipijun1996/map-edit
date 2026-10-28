import copy,math,itertools
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle

def alternatives(base):
 out=[];target=base['route_spec']['to_port'];original=base['control_plan'];end=base['exit_port'][0]
 def add(kind,plan):
  c=copy.deepcopy(base);c['id']+='-counter-'+kind;c['counterexample_kind']=kind;c['control_plan']=plan;out.append(c)
 shots=[i for i,s in enumerate(original)if s['op']=='shoot']
 if target=='C':
  middle=next(i for i,s in enumerate(original)if s['op']=='shoot'and s.get('aim_cell'))
  p=copy.deepcopy(original)
  # Keep the exact original world, but use the same real bell shot on deck.
  # This is a strong lower-cost candidate, never accepted by action wording.
  for j in [middle-2,middle-1]:p[j]=dict(op='wait',trigger=copy.deepcopy(p[j]['trigger']))
  add('ground-on-deck-reverse-same-shot-count',p)
  p=copy.deepcopy(original);p[middle]=dict(op='wait',trigger=copy.deepcopy(p[middle]['trigger']));add('omit-reverse-shot',p)
  p=copy.deepcopy(original);p[middle]=cmd('shoot',direction=[1,0]);add('miss-reverse-receiver-horizontal',p)
  # Actual board and walk to centre, then try skipping both reverse/catch.
  prefix=copy.deepcopy(original[:10])
  add('direct-west-from-first-board',prefix+[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.5,.8660254037844386]),settle(end)])
  p=copy.deepcopy(original);p[shots[0]]=dict(op='wait',trigger=copy.deepcopy(p[shots[0]]['trigger']));add('omit-boarding-shot',p)
  p=copy.deepcopy(original);p[shots[-1]]=dict(op='wait',trigger=copy.deepcopy(p[shots[-1]]['trigger']));add('omit-final-high-shore-shot',p)
  add('ground-prefire-before-boarding',[cmd('shoot',aim_cell=dict(kind='bell',id='reverse-bell'))]+copy.deepcopy(original))
  add('wait-manual-endpoint-no-auto-return',prefix+[cmd('axis',value=0),cmd('wait',540),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.5,.8660254037844386]),settle(end)])
  for hold,dy in itertools.product([8,20,30],[.7,.95]):
   add(f'low-shore-direct-west-{hold}-{dy}',[cmd('axis',value=1),wait_x(732),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[math.sqrt(1-dy*dy),dy]),settle(end)])
  for x in [300,550,730]:
   add('pre-reverse-from-low-shore-'+str(x),[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='reverse-bell'))]+copy.deepcopy(original))
  p=copy.deepcopy(original);p[middle+1]=cmd('axis',value=0);add('no-right-air-correction',p)
 else:
  for j in shots:
   p=copy.deepcopy(original);p[j]=dict(op='wait',trigger=copy.deepcopy(p[j]['trigger']));add('omit-shot-'+str(j),p)
  prefix=copy.deepcopy(original[:10])
  for hold in [8,20,30]:
   add('ordinary-jump-off-carrier-'+str(hold),prefix+[wait_x(1240),cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),settle(end)])
  add('skip-long-carriage-exit-immediately',prefix+[cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,.8660254037844386]),settle(end)])
  add('ground-prefire-before-boarding',[cmd('shoot',aim_cell=dict(kind='bell',id='reverse-bell'))]+copy.deepcopy(original))
  add('passive-endpoint-stand-no-high-action',prefix+[cmd('axis',value=0),cmd('wait',540),settle(end)])
  for hold,dy in itertools.product([8,20,30],[.4,.7,.95]):
   add(f'low-shore-direct-east-{hold}-{dy}',[cmd('axis',value=1),wait_x(732),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),settle(end)])
  for hold in [0,8,20]:
   add('ordinary-low-shore-east-'+str(hold),[cmd('axis',value=1),wait_x(748),cmd('jump'),cmd('jump_release',hold),settle(end)])
 return out
