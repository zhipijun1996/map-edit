"""Rejected exterior excursions cannot establish an internal Module bypass.

Only the exact approved designs and the sole whole-body footprint rejection
qualify. Raw success, thresholds and every nominal observation stay unchanged.
"""
import copy
from .review_counter_scope_v4 import DESIGNS

def classify(case,raw,check,outcome,judgment,baseline):
 spec=case.get('approved_implementation',{})
 if DESIGNS.get(spec.get('reviewId'))!=spec.get('designVersion'):return judgment
 if case.get('migration_counter',{}).get('kind')not in ('ordinary-jump','omit-all-shots','omit-first-shot'):return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
 result=copy.deepcopy(judgment);result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',nominalBodyQualificationUnchanged=True,reason='The alternative reaches the endpoint only after its real body leaves the approved rectangle. Exterior clearance is unproved; this rejected exterior path cannot certify an internal bypass.')
 return result
