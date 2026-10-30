"""Two pinned reviewed designs: paid exterior excursions are outside the claim.

This does not accept a route, waive body containment, or alter quality gates.
Nominal demonstrations, real harms and actual cheaper internal bypasses remain.
"""
import copy

DESIGNS={
    '07':'sha256:5bd449804b5a095fb2e78187623cf918262f5ba21f1881494adbf72159d449dd',
    '12':'sha256:bfaa7f2430ed82ecb0111ac4b8a1e7b5e1f33729b278200afaa180e8d14c676c',
    '23':'sha256:a9d7019bc4d157ae1ccb157e32ad51ed7b4e153f7a8e3e42128a6b2e7c8528ad',
}

def classify(case,raw,check,outcome,judgment,baseline):
    spec=case.get('approved_first30',{});n=spec.get('reviewId');route=case.get('route_spec',{})
    if n not in DESIGNS or spec.get('designVersion')!=DESIGNS[n]:return judgment
    kind=case.get('migration_counter',{}).get('kind')
    if kind!=('ordinary-jump'if n=='23'else'ground-preopen-airlock-pair'if n=='07'else'ground-preopen-return-catch'):return judgment
    if n=='23'and(route.get('from_port'),route.get('to_port'))!=('A','C'):return judgment
    if set(check.get('reasons',[]))!={'actual_body_outside_approved_rectangle'}:return judgment
    if not judgment.get('invalidates_design')or not outcome.get('ok')or not baseline or not baseline.get('ok'):return judgment
    if raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
    if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
    if n=='23':
        if raw.get('shots')!=baseline.get('shots')or raw.get('jumps')!=baseline.get('jumps',0)+1 or raw.get('ticks',0)<baseline.get('ticks',0):return judgment
    elif raw.get('shots',0)<=baseline.get('shots',0)or any(raw.get(k,-1)<baseline.get(k,0)for k in ('jumps','ticks')):return judgment
    frames=raw.get('frames',[]);normal=baseline.get('frames',[])
    if not frames or not normal:return judgment
    for key in ('hp','energy','shot_charges'):
        if frames[-1].get(key,-1)<normal[-1].get(key,0):return judgment
    if n!='23'and frames[-1].get('jumps_used',99)>normal[-1].get('jumps_used',0):return judgment
    b=spec['rectangle'];outside=[f for f in frames if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05]
    if not outside:return judgment
    side='TOP'if n=='23'or n=='12'and route.get('from_port')=='E'else'LEFT'if route.get('from_port')in('A','B')else'RIGHT'
    for f in outside:
        if n=='23'and abs(f['x']+320)+12<=32 and f['y']-18>=b['y'] and f['y']<=488+128 and f['vy']>0:continue
        if side=='LEFT'and not(f['x']-12<b['x'] and b['y']<=f['y']-18 and f['y']+18<=b['y']+b['h']):return judgment
        if side=='RIGHT'and not(f['x']+12>b['x']+b['w'] and b['y']<=f['y']-18 and f['y']+18<=b['y']+b['h']):return judgment
        if side=='TOP'and not(f['y']-18<b['y'] and b['x']<=f['x']-12 and f['x']+12<=b['x']+b['w']):return judgment
    result=copy.deepcopy(judgment)
    result.update(invalidates_design=False,originalJudgment=judgment,scope='outside_contract_alternative',accepted_module_solution=False,certified_internal_alternative=False,spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',outsideFace=side,outsideBodyFrames=[f['frame']for f in outside],nominalBodyQualificationUnchanged=True,reason='This exact paid pre-open counter leaves the approved footprint before returning. Exterior space is an unproved dependency; it neither certifies an internal solution nor refutes the unchanged nominal mechanism.')
    return result
