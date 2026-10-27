"""Exact standard direction counters; continuous reward comparisons are separate."""
import copy,math,itertools
from . import rules_v2 as rules,comparisons_v1 as comp
from pcg.prototype.workshop.rules import cmd,ground

def alternatives(c):
 p=c['control_plan'];out=[];back=c['route_spec']['from_port']=='B';end=24 if back else 1512
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind
  v['control_plan']=comp.normal_timeout(plan+[rules.old.seek(end),rules.old.reach(end,-1 if back else 1),ground(),cmd('wait',20)])
  out.append(v)
 if not back:
  shots=[i for i,s in enumerate(p)if s['op']=='shoot']
  for i in shots:
   q=copy.deepcopy(p);q[i]=dict(op='wait',trigger=copy.deepcopy(q[i]['trigger']));add('omit-upper-stage-shot-'+str(i),q)
  for hold in [8,20,30]:
   q=copy.deepcopy(p);j=shots[0];q[j]=dict(op='wait',trigger=copy.deepcopy(q[j]['trigger']));q[j-1]['trigger']['after']=hold;add('ordinary-first-upper-stage-'+str(hold),q)
  for hold,dy in itertools.product([20,30],[.5,.8,1.0]):
   add(f'direct-low-to-B-{hold}-{dy}',[rules.old.seek(580),rules.old.reach(580,1),ground(),rules.old.seek(1512),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy])])
  for x in [280,400,580]:
   add('low-ground-prefire-'+str(x),[rules.old.seek(x),rules.old.reach(x,1),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='fold-pair')),cmd('wait',12)]+copy.deepcopy(p))
  for hold,dy in itertools.product([12,20,30],[.7,.95]):
   # Keep actual upperbridge/reward prelude, then try a cheaper pillar crossing.
   third=shots[2];q=copy.deepcopy(p[:third-3]);q+=[rules.old.seek(1512),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy])];add(f'direct-reward-island-to-B-{hold}-{dy}',q)
 else:
  add('old-upper-return-0866',comp.old_upper_return())
  add('old-upper-return-0800',comp.old_upper_return(.8))
  add('old-upper-return-ordinary',comp.old_upper_return(shot=False))
  add('walk-left-no-switch',[rules.old.seek(24)])
  drop=[rules.old.seek(1216),rules.old.reach(1216,-1),ground()]
  for hold,dy in [(20,.15),(30,.35),(20,.6),(30,.85)]:
   add(f'lowerbank-skip-R-{hold}-{dy}',copy.deepcopy(drop)+[rules.old.seek(1208),rules.old.reach(1208,-1),ground(),rules.old.seek(24),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[math.sqrt(1-dy*dy),dy])])
  add('late-primary-cut-then-R',copy.deepcopy(drop)+[cmd('shoot',aim_cell=dict(kind='bell',id='fold-pair')),cmd('wait',60),rules.old.seek(24),cmd('jump'),cmd('jump_release',20)])
  j=next(i for i,s in enumerate(p)if s['op']=='shoot')
  q=copy.deepcopy(p);q[j]=dict(op='wait',trigger=copy.deepcopy(q[j]['trigger']));add('omit-access-shot',q)
  q=copy.deepcopy(p);q[j]=cmd('shoot',direction=[0,-1]);add('miss-access-receiver',q)
  j=next(i for i,s in enumerate(p)if s['op']=='jump');q=copy.deepcopy(p);q[j]=dict(op='wait',trigger=copy.deepcopy(q[j]['trigger']));add('omit-lower-ordinary-jump',q)
  for x in [1300,1360,1440,1512]:
   q=copy.deepcopy(p);q[0]=rules.old.seek(x);q[1]=rules.old.reach(x,-1);add('different-B-access-position-'+str(x),q)
  for hold in [8,20,30]:
   q=copy.deepcopy(p);j=next(i for i,s in enumerate(q)if s['op']=='jump_release');q[j]['trigger']['after']=hold;add('different-lower-ordinary-hold-'+str(hold),q)
  for dy in [.2,.6,1.0]:
   add('one-shot-direct-B-left-'+str(dy),[rules.old.seek(1304),rules.old.reach(1304,-1),ground(),rules.old.seek(24),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[math.sqrt(1-dy*dy),dy])])
 return out
