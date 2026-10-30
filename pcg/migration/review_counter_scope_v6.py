"""191: an exterior ground-preopen path is not an internal certified bypass.

Narrow measurement correction only. Original raw, nominal gates and every
unrelated refusal remain unchanged; no inferred resource-cost exemption.
"""
import copy
DESIGN='sha256:f64e14e3c9dce30981a1b4d7b10eea09278e613b2d8556e36945c2a7d529728d'
def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='191'or s.get('designVersion')!=DESIGN:return judgment
 if case.get('migration_counter',{}).get('kind')!='ground-preopen-lift_bell':return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
 result=copy.deepcopy(judgment);result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',nominalBodyQualificationUnchanged=True,reason='Exact approved 191: the ground-preopen alternative reaches the goal only after its real body leaves the approved rectangle. Exterior clearance remains unproved; this rejected exterior path cannot establish an internal bypass.')
 return result
