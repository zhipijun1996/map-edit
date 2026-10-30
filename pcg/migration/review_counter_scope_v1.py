"""N06's paid C-apron excursion is an external dependency, not an internal route.

No purpose assertion, body test, outcome, quality gate or old report is changed.
Only this exact approved design and ground-preopen probe are eligible.
"""
import copy

DESIGN='sha256:e8599a815628efc8bb4bd87bb050f6d3939293ce0d6e824087cc181c94196ffc'
SPATIAL={'actual_body_outside_frozen_ownership','actual_body_sweep_outside_frozen_ownership','actual_body_outside_approved_rectangle'}


def classify(case,raw,check,outcome,judgment,baseline):
    spec=case.get('approved_implementation',{})
    if spec.get('reviewId')!='01' or spec.get('designVersion')!=DESIGN:return judgment
    if case.get('route_spec',{}).get('from_port')!='C' or case.get('route_spec',{}).get('to_port')not in ('A','B','D'):return judgment
    if 'ground-preopen-wing-pair'not in case.get('id',''):return judgment
    if not judgment.get('invalidates_design')or not outcome.get('ok')or not baseline or not baseline.get('ok'):return judgment
    reasons=set(check.get('reasons',[]))
    if not reasons or not reasons<=SPATIAL:return judgment
    if raw.get('hp')!=5 or raw.get('returns')or raw.get('plains',{}).get('player_damage'):return judgment
    if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):return judgment
    if raw.get('shots',0)<=baseline.get('shots',0) or raw.get('jumps',0)<baseline.get('jumps',0)or raw.get('ticks',0)<baseline.get('ticks',0):return judgment
    fs=raw.get('frames',[]);bs=baseline.get('frames',[])
    if not fs or not bs:return judgment
    for key in ('shot_charges','energy','hp'):
        if fs[-1].get(key,-1)<bs[-1].get(key,0):return judgment
    if fs[-1].get('jumps_used',99)>bs[-1].get('jumps_used',0)or fs[-1].get('shot_cooldown',99)>bs[-1].get('shot_cooldown',0)+1e-6:return judgment
    rect=spec['rectangle'];right=rect['x']+rect['w']
    outside=[f for f in fs if f['x']-12<rect['x']-.05 or f['x']+12>right+.05 or f['y']-18<rect['y']-.05 or f['y']+18>rect['y']+rect['h']+.05]
    if not outside or any(f['x']+12<=right+.05 or f['y']<rect['y']-.05 or f['y']+18>rect['y']+rect['h']+.05 for f in outside):return judgment
    result=copy.deepcopy(judgment)
    result.update(invalidates_design=False,originalJudgment=judgment,
        reason='Exact approved N06 C-apron probe needs external right-side air and an extra real shot; it does not certify an internal alternative or invalidate the unchanged nominal body contract.',
        scope='outside_contract_alternative',accepted_module_solution=False,certified_internal_alternative=False,
        outsideBodyFrames=[f['frame']for f in outside],maximumRightBodyOverrun=max(f['x']+12-right for f in outside),
        maximumTopBodyOverrun=max(0,max(rect['y']-(f['y']-18)for f in outside)),
        actualCost=dict(nominal={k:baseline[k]for k in ('shots','jumps','ticks')},alternative={k:raw[k]for k in ('shots','jumps','ticks')}),
        spatialCertification='UNKNOWN',mapSpaceDependency='UNKNOWN',nominalBodyQualificationUnchanged=True)
    return result
