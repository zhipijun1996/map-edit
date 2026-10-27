"""Keep strict nominal loop checks, permit real optional reward on fresh return."""
from . import rules_v2 as rules

def purpose(c,r):
 q=rules.purpose(c,r)
 if c['route_spec']['from_port']=='B':
  claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')and e.get('id')=='upper-cache']
  bonus=len(claims)==1 and r.get('workshop',{}).get('coins')==16
  if bonus:
   q['reasons']=[x for x in q['reasons']if x!='actual_one_reward_transaction_missing_or_wrong']
  q['causal']['fresh_B_optional_actual_reward']=dict(initial_claim_not_assumed=True,actual_bonus_claim=bonus,nominal_lower_path_coins=0,old_upper_may_collect_unclaimed_box=True)
 q['ok']=not q['reasons'];return q
