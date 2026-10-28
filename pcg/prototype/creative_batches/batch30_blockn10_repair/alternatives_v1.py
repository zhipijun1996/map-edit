import copy
from pcg.prototype.creative_batches.batch30_blockn10.alternatives_v2 import alternatives as old
from pcg.prototype.workshop.rules import cmd
from . import rules_v1 as rules
def alternatives(c):
 base=copy.deepcopy(c);normal=rules.candidate(c['rule_parameters']['control'],'normal');base['control_plan']=copy.deepcopy(normal['control_plan'])
 out=old(base)
 for v in out:
  if v['counterexample_kind']=='late-M-receiver-reset':
   p=copy.deepcopy(base['control_plan']);j=max(i for i,q in enumerate(p)if q['op']=='jump');assert p[j-1]['op']=='axis'and p[j-1]['value']==-1
   p.insert(j-1,cmd('wait',160));v['control_plan']=p
 if c['route_spec']['id']=='A-to-B-delayed-Near-retry':
  def add(kind,p):
   v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=p;out.append(v)
  add('omit-deliberate-delay-nominal-route',copy.deepcopy(normal['control_plan']))
  p=copy.deepcopy(c['control_plan']);shoots=[i for i,q in enumerate(p)if q['op']=='shoot'];j=shoots[1];p[j]=dict(op='wait',trigger=p[j]['trigger']);add('omit-restore-receiver-shot',p)
  p=copy.deepcopy(c['control_plan']);j=shoots[1];g=next(i for i in range(j+1,len(p))if p[i]['op']=='wait'and p[i].get('trigger',{}).get('state')=='grounded');p[g]=cmd('wait');add('omit-explicit-M-recatch-wait',p)
 return out
