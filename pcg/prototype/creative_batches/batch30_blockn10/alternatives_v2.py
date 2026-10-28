"""All variants retain the repaired world; original ray/cost checks remain."""
from .alternatives_v1 import alternatives as old
def alternatives(c):
 out=old(c)
 for v in out:
  for q in v['control_plan']:
   if 'aim_target'in q and q['aim_target'][0]==800:q['aim_target'][0]=832
   d=q.get('trigger',{}).get('dynamic',{})
   if v['counterexample_kind'].startswith('enter-body-into-receiver-alcove')and d.get('kind')=='actor_x'and d.get('value')==810:d['value']=842
 return out
