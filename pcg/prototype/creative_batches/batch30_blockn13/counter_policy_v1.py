from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
def classify(c,r,check,outcome,baseline=None):
 core=common.checked_purpose(type('Core',(),{'purpose':staticmethod(rules.core_purpose)}),c,r)
 result=common.counter_classification(c,r,core,outcome,baseline)
 result.update(nominal_parking_purpose=check,actual_general_traversal_core=core,accepted_module_solution=bool(outcome['ok']and core['ok']),actual_exit_dock=core['causal']['final_dock'])
 if outcome['ok']and core['ok']:
  result.update(invalidates_design=False,reason='ActualsameB/rewardcarriedrouteislegal;parkingoptionalforoutbound. RetainrealexitDockstate/costdifference, no artificialpark/waitwordrequirement.')
 return result
