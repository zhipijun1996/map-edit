"""Exact-world active-transfer falsifiers; goal/cost precedes causal words."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle

def alternatives(c):
 out=[];source=c['control_plan'];board=copy.deepcopy(source[:14]);high=c['route_spec']['id']=='high'
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 shots=[i for i,q in enumerate(source)if q['op']=='shoot']
 for j in shots:
  p=copy.deepcopy(source);p[j]=dict(op='wait',trigger=p[j]['trigger']);add('omit-shot-'+str(j),p)
 if high:
  for hold in [12,24]:
   # Deliberately start to the RIGHT of parkedP2, fire right-down so the
   # original recoil goes left-up onto a staticP2, renew, then launch east.
   p=board+[wait_x(700),cmd('axis',value=1),wait_x(828),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[.7,math.sqrt(.51)]),settle(760),ground(),cmd('wait',8),settle(790),ground(),cmd('wait',8),settle(1256),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.8,.6]),settle(1256,6)]
   add('static-P2-rightside-leftup-recoil-'+str(hold),p)
  for hold in [12,24]:
   p=board+[wait_x(600),cmd('axis',value=0),cmd('jump'),cmd('jump_release',hold),settle(760),ground(),cmd('wait',8),settle(790),ground(),cmd('wait',8),settle(1256),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.8,.6]),settle(1256,6)]
   add('early-ordinary-jump-static-P2-'+str(hold),p)
  for hold in [8,16,24]:
   for dy in [.6,.8]:
    p=board+[wait_x(700),cmd('axis',value=1),wait_x(864),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(1256,6)]
    add(f'P1-direct-high-skip-P2-{hold}-{dy}',p)
 else:
  add('passive-P1-ride-no-exit',board+[cmd('axis',value=0),cmd('wait',650)])
  for hold in [8,20,32]:
   p=board+[wait_x(700),cmd('axis',value=1),wait_x(864),cmd('jump'),cmd('jump_release',hold),settle(1256,6)]
   add('P1-low-no-recoil-jump-'+str(hold),p)
  for delay in [0,6,12]:
   p=[cmd('axis',value=1),wait_x(192),cmd('jump'),cmd('jump_release',20),cmd('shoot',delay,direction=[-.98,.1989974874]),settle(1256,6)]
   add('A-direct-low-skip-P1-'+str(delay),p)
 for hold in [12,24]:
  p=[cmd('axis',value=1),wait_x(192),cmd('shoot',aim_cell=dict(kind='bell',id='intercept-start')),cmd('wait',45),cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-.8,.6]),settle(1256,6)]
  add('ground-prestart-direct-skip-P1-'+str(hold),p)
 for dy in [.6,.8,1.]:
  p=[cmd('axis',value=1),wait_x(1000),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(1256,6)]
  add('internal-floor-single-jump-recoil-'+str(dy),p)
 # Preserve bothactualworld andcomplementary controls; add no props/resources.
 if high:
  p=copy.deepcopy(source);j=shots[0];p[j].pop('aim_cell',None);p[j]['direction']=[-.6,.8];add('keep-first-recoil-miss-P2-start',p)
 else:
  p=copy.deepcopy(source);p[7]=dict(op='wait',trigger=p[7]['trigger']);add('omit-boarding-groundjump',p)
  for edge in [820,840]:
   for hold in [12,24]:
    add(f'P1-earlier-ordinary-low-{edge}-{hold}',board+[wait_x(700),cmd('axis',value=1),wait_x(edge),cmd('jump'),cmd('jump_release',hold),settle(1256,6)])
 assert len(out)>=18,len(out)
 return out
