"""Exact new-idea exterior counters remain uncertified external alternatives."""
import copy
from .revision058_boundary_v1 import VERSIONS

def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if VERSIONS.get(s.get('reviewId'))!=s.get('designVersion')or not case.get('migration_counter')or case.get('migration_probe'):return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):return judgment
 b=s['rectangle'];outside=[]
 for f in raw.get('frames',[]):
  inside=b['x']-.05<=f['x']-12 and f['x']+12<=b['x']+b['w']+.05 and b['y']-.05<=f['y']-18 and f['y']+18<=b['y']+b['h']+.05
  mouth=any(p['id']in [case['route_spec']['from_port'],case['route_spec']['to_port']]and p['face']=='TOP'and p['surface']=='ONE_WAY_PLATFORM'and abs(f['x']-p['position'][0])+12<=32.05 and b['y']-128<=f['y']-18 and f['y']+18<=b['y']+b['h']for p in case.get('legal_port_mouths',[]))
  if not inside and not mouth:outside.append(f['frame'])

 if not outside or outside!=check.get('causal',{}).get('outsideFrames'):return judgment
 r=copy.deepcopy(judgment);r.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',actualOutsideFrames=outside,nominalQualificationUnchanged=True,reason='The real counter travels outside this exact approved Module beyond its selected legal TOP mouth. Preserve the external-space dependency; this is not an internally certified shortcut, and no nominal refusal is waived.')
 return r
