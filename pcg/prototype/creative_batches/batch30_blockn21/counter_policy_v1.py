"""Persistent progress is optional, never a prohibition on a legitimate branch."""
from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
def classify(c,r,check,outcome,baseline=None):
 result=common.counter_classification(c,r,check,outcome,baseline);why=set(check['reasons'])
 safety={'player_harm','world_reset','forbidden_ability','actual_body_outside_ownership'}
 if outcome['ok']and why=={'nominal_west_branch_did_not_leave_stage2_uncommitted'}:
  result.update(invalidates_design=False,accepted_module_solution=True,reason='West does not need stage2, but completing optional stage2 on the way is legitimate; no permanent exclusivity claim.')
 elif outcome['ok']and why=={'actual_body_outside_ownership'}:
  result.update(invalidates_design=False,scope='outside_declared_ownership',accepted_module_solution=False,spatial_certification='UNKNOWN',reason='Entire intended causal chain remains; retain outside-body failure, not an internal Module solution.')
 elif outcome['ok']and not check['ok']and not why&safety:
  base=baseline or dict(shots=4 if c['route_spec']['to_port']=='B'else 3,jumps=3)
  paid=r.get('shots',0)>base['shots']or r.get('jumps',0)>base['jumps']
  if paid:result.update(invalidates_design=False,accepted_module_solution=True,reason='Actual same-goal alternate pays extra real shot/jump actions with original resources; no mandatory named intermediate action.')
 result['nominal_purpose']=check
 return result
