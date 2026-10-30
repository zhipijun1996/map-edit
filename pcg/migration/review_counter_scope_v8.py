"""040 approved versions: an exterior counter is not an internal shortcut.

Nominal routes, actual harm, resources and original raw remain strict. This
measurement only leaves an actually exterior alternative uncertified.
"""
import copy
VERSIONS={'202': 'sha256:5a10ddb17798b09d3675e103b30bca0c4a38a0f8f829ce3448ccea2a5f70672d', '204': 'sha256:a0903da04176561e76ff3ef2f67b53c68fa7f2ed43ad9fde2e389e822a3d861c', '220': 'sha256:bb1f45bc51e30af2fde130fb2c554949d8a4eca9f86d8444ee0d4d7362a080d0', '223': 'sha256:aaa672e77981c063008d759f8b7690fae3a8c73e1f9255400d2a20b8b7fdf877', '225': 'sha256:90b832454ab37fcee8c68cbf536eb11d6e790dc03da17a353b18f29d49b7cc89', '115': 'sha256:426f590e3a4132aaa0c5013eb451db3bb4e47d09394e082d73e3a46a33640108', '166': 'sha256:236fe6ecd8e6977fa0bc576b1de948d9bd8d5b1952f91c546746c9401e262359', '167': 'sha256:6a0631569698587b01414753b2c55dea9ce3ca381cfdb93f676efb188fd4abd7'}
def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if VERSIONS.get(s.get('reviewId'))!=s.get('designVersion')or not case.get('migration_counter')or case.get('migration_probe')or case.get('air_port_contracts'):return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
 b=s['rectangle'];outside=[f['frame']for f in raw.get('frames',[])if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05]
 if not outside or outside!=check.get('causal',{}).get('outsideFrames'):return judgment
 result=copy.deepcopy(judgment);result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',actualOutsideFrames=outside,nominalQualificationUnchanged=True,reason='The real counter leaves this exact approved rectangle. Preserve its external-space dependency; it is not an internally certified alternative and does not waive any nominal route refusal.')
 return result
