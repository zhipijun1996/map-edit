"""197: an actual exterior preopen is not proof of an interior shortcut.

This exact-version measurement correction preserves the rejected counter, all
native inputs, all nominal trials and every unrelated quality refusal.
"""
import copy
DESIGN='sha256:55a825da88c0cea19a212cd39562c09f374297b3911cf6df687d698070f9b677'
def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='197'or s.get('designVersion')!=DESIGN:return judgment
 if case.get('migration_counter',{}).get('kind')!='ground-preopen-low-return-key':return judgment
 if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}or not outcome.get('ok')or not judgment.get('invalidates_design'):return judgment
 if not baseline or not baseline.get('ok')or raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
 if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
 b=s['rectangle'];outside=[f['frame']for f in raw.get('frames',[])if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05]
 if not outside or outside!=check.get('causal',{}).get('outsideFrames'):return judgment
 result=copy.deepcopy(judgment);result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',nominalBodyQualificationUnchanged=True,actualOutsideFrames=outside,reason='Exact approved 197: the ground-preopen counter leaves the approved rectangle with its real body. Preserve the exterior alternative; its unproved neighboring space cannot establish an internal bypass.')
 return result
