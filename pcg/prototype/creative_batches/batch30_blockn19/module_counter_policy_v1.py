from . import rules_v2 as rules
from .counter_policy_v1 import classify as structural
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
def classify(c,r,check,outcome,baseline=None):
 ordinary=common.checked_purpose(rules,c,r)
 result=structural(c,r,ordinary,outcome,baseline)
 result.update(nominal_witness_purpose=check,ordinary_two_swap_purpose=ordinary,accepted_recovery_witness=bool(check['ok']and c.get('fixture_kind')=='recovery'))
 if outcome['ok']and ordinary['ok']:
  result.update(invalidates_design=False,accepted_module_solution=True,reason='Actual original withdrawal/Mground/side-swap route is a legitimate solution; avoiding an intentionally missed-M failure does not refute independently required recovery witness.')
 return result
