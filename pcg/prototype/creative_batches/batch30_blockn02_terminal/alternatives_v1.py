"""Extend exact-world counters with strong ordinary final-hop variants."""
import copy
from pcg.prototype.creative_batches.batch30_blockn02_repair.alternatives_v1 import alternatives as prior

def alternatives(c):
 out=prior(c)
 if c['route_spec']['id']=='high':
  shots=[j for j,q in enumerate(c['control_plan'])if q['op']=='shoot'];last=shots[-1]
  for hold in [24,32]:
   v=copy.deepcopy(c);v['id']+='-counter-long-ordinary-onward-P2-hop-'+str(hold)
   v['counterexample_kind']='long-ordinary-onward-P2-hop-'+str(hold)
   v['control_plan'][last-1]['trigger']['after']=hold
   v['control_plan'][last]=dict(op='wait',trigger=v['control_plan'][last]['trigger'])
   out.append(v)
 return out
