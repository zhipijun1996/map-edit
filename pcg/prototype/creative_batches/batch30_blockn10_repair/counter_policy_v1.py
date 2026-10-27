"""Canonical delay demonstrations are not compulsory routes for counter-solutions."""
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
def classify(c,raw,check,outcome,baseline=None):
 core=common.checked_purpose(type('Core',(),{'purpose':staticmethod(rules.core_purpose)}),c,raw)
 decision=common.counter_classification(c,raw,core,outcome,baseline)
 decision.update(canonical_purpose_preserved=check['ok'],actual_core_purpose=core,accepted_module_solution=bool(outcome['ok']and core['ok']),scope='actual_declared_ownership_and_Near_Far_M_body_reward_conditions')
 if outcome['ok']and core['ok']:
  decision.update(invalidates_design=False,reason='Actualnormal/paidNear-Far-Msolutionpreservesoriginalbody/reward/resources/window; artificialdelayandrestorearenotmandatoryforcounter-solutions')
 return decision
