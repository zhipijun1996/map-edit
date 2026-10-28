"""Boss-foyer sky probes that leave the footprint do not certify internal routes."""
import copy

def classify(case,raw,check,outcome,judgment,baseline):
    spec=case.get('approved_implementation',{})
    if spec.get('reviewId')!='34'or spec.get('designVersion')!='sha256:e3990c52ab60a6d4095694b2db6ea39642e62cfcb3f73bac8f0d05a9f76f1adf':return judgment
    r=case.get('route_spec',{})
    if (r.get('from_port'),r.get('to_port'))not in (('C','entry'),('D','exit'))or case.get('migration_counter',{}).get('kind')!='ordinary-jump':return judgment
    if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
    if raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
    if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
    result=copy.deepcopy(judgment);result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',nominalBodyQualificationUnchanged=True,reason='The sky-axis probe exits the footprint before returning to the dock. This requires unproved exterior clearance; it is neither an internal solution nor an intrinsic design bypass.')
    return result
