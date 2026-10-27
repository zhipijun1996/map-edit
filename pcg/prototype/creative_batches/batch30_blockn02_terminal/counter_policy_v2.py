"""A full-body-invalid policy preserving the core is not a P2 bypass proof.

This never changes purpose acceptance or supplies spatial proof. It only stops
an out-of-contract policy with all original causal stages from being reported
as a counterexample to those stages. Actual in-contract bypasses still refute.
"""
from pcg.map_directed.block_grid.contracts import raster
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common


def moving_support(frames,pid):
    supported=[f for f in frames if f.get('grounded')and f.get('support_id')==pid]
    poses=[next((p.get('position')for p in f.get('moving_platforms',[])if p.get('id')==pid),None)for f in supported]
    valid=bool(poses)and all(isinstance(p,list)and len(p)==2 for p in poses)
    span=max(max(p[i]for p in poses)-min(p[i]for p in poses)for i in [0,1])if valid else 0
    return supported,span


def classify(case,raw,check,outcome,baseline=None):
    result=common.counter_classification(case,raw,check,outcome,baseline)
    if not result['invalidates_design']or not outcome.get('ok'):return result
    if set(check.get('reasons',[]))!={'actual_complete_body_outside_frozen_block_ownership'}:return result
    grid=case.get('block_grid',{});owned=set(map(tuple,grid.get('cells',[])))
    frames=raw.get('frames',[])
    if not owned or not frames:return result
    outside=[dict(frame=f['frame'],body=[f['x']-12,f['y']-18,24,36],outside_cells=sorted(map(list,raster([f['x']-12,f['y']-18,24,36])-owned)))for f in frames if not raster([f['x']-12,f['y']-18,24,36])<=owned]
    if not outside:return result
    first,first_span=moving_support(frames,'approach-carrier')
    shots=[f for f in frames if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
    toggles=[e for e in raw.get('workshop',{}).get('events',[])if e.get('type')=='carrier_toggle'and e.get('id')=='intercept-start']
    if len(first)<6 or first_span<8 or not shots or not toggles:return result
    shot=shots[0];start=toggles[0]
    if shot.get('grounded')or start.get('airborne')is not True or start.get('running')is not True or start['frame']<shot['frame']:return result
    # A real projectile impact/open commit belongs to the shot which actually
    # starts the original carrier, rather than to a requested command label.
    opens=[e for e in raw.get('plains',{}).get('events',[])if e.get('type')=='bell_open'and e.get('id')=='intercept-start'and e.get('frame')==start['frame']]
    if not opens:return result
    after=[f for f in frames if f['frame']>start['frame']]
    second,second_span=moving_support(after,'intercept-carrier')
    if len(second)<6 or second_span<8:return result
    running=all(next((p.get('running')for p in f.get('workshop',{}).get('carriers',[])if p.get('id')=='intercept-carrier'),False)is True for f in second)
    renewal=[f for f in second if f.get('shot_charges')==1]
    spent=any(f['frame']>=shot['frame']and f['frame']<second[0]['frame']and f.get('shot_charges')==0 for f in frames)
    onward=[f for f in frames if f['frame']>second[0]['frame']and any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))]
    safety=raw.get('hp')==5 and not raw.get('returns')and not raw.get('plains',{}).get('player_damage')and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
    if not running or not renewal or not spent or not onward or not safety:return result
    result.update(invalidates_design=False,scope='outside_declared_ownership',accepted_module_solution=False,spatial_certification='UNKNOWN',
        purpose_failure_preserved=True,body_contract_waived=False,
        reason='Actual activeP2 interception and real landingrenewal remain; this full-body-invalid terminalpolicy is not an in-contract Module solution or a bypass ofthatcore. External continuation requires separateMap evidence.',
        preserved_core=dict(P1_supported_frames=len(first),actual_P1_motion_span=first_span,first_air_shot_frame=shot['frame'],P2_start=start,actual_P2_supported_frames=len(second),actual_P2_motion_span=second_span,P2_running_during_support=running,real_spent_then_renewed=spent and bool(renewal),renewal_frames=len(renewal),onward_ground_jump_frames=[f['frame']for f in onward]),
        actual_body_scope_failure=dict(count=len(outside),frames=outside,may_add_owned_cells=False),
        actual_cost=dict(shots=raw.get('shots'),jumps=raw.get('jumps'),ticks=raw.get('ticks')))
    return result
