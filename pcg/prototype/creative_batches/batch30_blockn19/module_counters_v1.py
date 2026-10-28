import copy
from . import rules_v2 as rules
from .alternatives_v1 import alternatives as normal_alternatives
from pcg.prototype.workshop.rules import cmd
def alternatives(c):
 basis=copy.deepcopy(c);basis['control_plan']=rules.candidate(0)['control_plan']
 out=normal_alternatives(basis)
 if c.get('fixture_kind')=='recovery':
  def add(kind,plan):
   v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
  add('ordinary-supported-M-alternative',copy.deepcopy(basis['control_plan']))
  p=copy.deepcopy(c['control_plan']);air=next(i for i,q in enumerate(p)if q.get('op')=='shoot'and'direction'in q);p[air]=cmd('wait');add('omit-recovery-air-recoil',p)
 return out
