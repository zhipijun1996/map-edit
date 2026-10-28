"""Active lower-cost station attempts on the exact same initialized world."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def alternatives(c):
 out=[];source=c['control_plan'];i=c['interface'];route=c['route_spec']['id'];sign=1 if i==0 else -1
 board=copy.deepcopy(source[:8]);prefix=copy.deepcopy(source[:11]);takeoff=205 if i==0 else 1095;front=410 if i==0 else 890;target=c['exit_port'][0]
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 p=copy.deepcopy(source);p[8]=dict(op='wait',trigger=p[8]['trigger']);add('omit-real-carrier-start',p)
 add('passive-standing-ride-no-departure',prefix+[cmd('axis',value=0),cmd('wait',650)])
 add('initial-entry-ordinary-jump',[cmd('axis',value=sign),wait_x(takeoff,sign),cmd('jump'),cmd('jump_release',32),settle(target,6)])
 for hold in [12,20,28]:
  for dy in [.8660254,1.]:
   direction=[(sign if route=='near'else-sign)*math.sqrt(max(0,1-dy*dy)),dy]
   add(f'initial-entry-one-shot-{hold}-{dy}',[cmd('axis',value=sign),wait_x(takeoff,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=direction),settle(target,6)])
 for dy in [.6,.8660254,1.]:
  direction=[(sign if route=='near'else-sign)*math.sqrt(max(0,1-dy*dy)),dy]
  add('parked-deck-no-motion-one-shot-'+str(dy),board+[cmd('axis',value=sign),wait_x(front,sign),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=direction),settle(target,6)])
 if route=='near':
  p=copy.deepcopy(source);jumps=[j for j,q in enumerate(p)if q['op']=='jump'];p[jumps[-1]]=dict(op='wait',trigger=p[jumps[-1]]['trigger']);add('actual-carrier-no-roof-transfer-jump',p)
  departure=600 if i==0 else 760
  add('earlier-carrier-departure-air-rebound-allowed',prefix+[wait_x(departure,sign),cmd('axis',value=-sign),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[sign*.2,math.sqrt(.96)]),settle(target,6)])
  for launch in ([390,410,425]if i==0 else[910,890,875]):
   add('parked-deck-outer-edge-'+str(launch),board+[cmd('axis',value=sign),wait_x(launch,sign),cmd('jump'),cmd('shoot',22,direction=[sign*.2,math.sqrt(.96)]),cmd('jump_release',20),settle(target,6)])
 else:
  p=copy.deepcopy(source);j=next(j for j,q in enumerate(p)if q.get('aim_cell',{}).get('id')=='station-selector');p[j]=dict(op='wait',trigger=p[j]['trigger']);add('omit-selector-keep-departure',p)
  prep=700 if i==0 else 600;late=820 if i==0 else 470;edge=900 if i==0 else 400
  add('ground-preselect-later-ordinary-departure-allowed',prefix+[wait_x(prep,sign),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),cmd('wait',8),cmd('axis',value=0),wait_x(late,sign),cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',28),settle(target,6)])
  first=850 if i==0 else 450;drop=1016 if i==0 else 284;inside=980 if i==0 else 320
  for launch in ([1000,1018,1025]if i==0 else[300,282,275]):
   add('unselected-far-gate-pillar-staged-'+str(launch),prefix+[wait_x(first,sign),cmd('axis',value=sign),wait_x(drop,sign),*rest(),cmd('axis',value=-sign),wait_x(inside,-sign),*rest(),cmd('axis',value=sign),wait_x(launch,sign),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-sign*.2,math.sqrt(.96)]),settle(target,6)])
 p=copy.deepcopy(source);p[2]=dict(op='wait',trigger=p[2]['trigger']);add('omit-actual-boarding-jump',p)
 assert len(out)==18,len(out)
 return out
