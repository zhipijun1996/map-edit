"""Exact revised196 exterior shortcut stays an uncertified external dependency.

Same rule as existing scope_v8/v9; no nominal, safety or resource refusal waived.
"""
import copy
VERSION='sha256:bec6503ea1cbcf5dcc7d8f6b4ff5d8330443faa65bab42add31b9e7192b894ca'
def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='196'or s.get('designVersion')!=VERSION or not case.get('migration_counter')or case.get('migration_probe'):return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):return judgment
 b=s['rectangle'];outside=[f['frame']for f in raw.get('frames',[])if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05]
 if not outside or outside!=check.get('causal',{}).get('outsideFrames'):return judgment
 r=copy.deepcopy(judgment);r.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',actualOutsideFrames=outside,nominalQualificationUnchanged=True,reason='This exact revised196 counter exits the rectangle away from its selected boundary mouth. Preserve its external-space dependency; no internally certified shortcut and no nominal refusal is waived.')
 return r
