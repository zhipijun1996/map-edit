"""Physical outcomes/costs, never counter-name exemption lists."""
from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
def classify(c,r,check,outcome,baseline=None):
 result=common.counter_classification(c,r,check,outcome,baseline)
 physical=rules.outcome(c,r);why=set(check['reasons']);causal=check['causal']
 if outcome['ok']and not check['ok']and why=={'actual_body_outside_ownership'}:
  result.update(invalidates_design=False,scope='outside_declared_ownership',accepted_module_solution=False,spatial_certification='UNKNOWN',reason='Entire original causal chain remains, but outside body route is not an internal Module solution; retain body failure.')
 elif outcome['ok']and physical['ok']and not check['ok']and 'actual_pair_collision_invariant_failed'not in why:
  costs=baseline or dict(shots=2,jumps=1)
  paid=r.get('shots',0)>costs.get('shots',2)or r.get('jumps',0)>costs.get('jumps',1)
  fs=r.get('frames',[]);floor=next((f for f in fs if f.get('grounded')and f.get('support_id')=='Platform4'),None)
  recoil=next((f for f in fs if floor and f['frame']>floor['frame']and not f.get('grounded')and any(e.get('type')=='shot'for e in f.get('accepted',[]))),None)
  staged=bool(causal.get('bridge_support_before_withdraw')and floor and recoil and r.get('shots',0)>=2 and r.get('jumps',0)>=1)
  if paid or staged:result.update(invalidates_design=False,accepted_module_solution=True,reason='Safe actual same-goal alternative pays extra real actions or replaces side switching with an actual lower recovery landing/air-recoil climb; nominal two-swap purpose remains independently required.',actual_lower_stage=({k:floor.get(k)for k in ['frame','x','y','support_id']}if floor else None),actual_paid_recovery_climb=staged)
 result['actual_physical_outcome']=physical
 return result
