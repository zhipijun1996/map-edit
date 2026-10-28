"""Project workshop input into the existing Map Block contract, without physics."""
import copy
import json
from pathlib import Path
from pcg.map_directed.block_grid.contracts import validate
from pcg.prototype.workshop.evidence import geometry_key

REPO=Path(__file__).resolve().parents[4]
POLICY=REPO/'pcg/map_directed/block_grid/plains-policy.json'


def inspect_case(case):
    size=json.loads(POLICY.read_text())['block_size']
    conflicts=[]
    def reject(field,reason,**facts):conflicts.append(dict(field=field,reason=reason,**facts))
    grid=case.get('block_grid')
    ports=case.get('block_ports')
    if not isinstance(grid,dict):reject('block_grid','missing Map Block ownership; historical physics does not grant Block compatibility')
    if not isinstance(ports,dict)or not ports:reject('block_ports','explicit anchors, profiles and internal staging positions required')
    if conflicts:return dict(status='needs_design',conflicts=conflicts,physics_cases=0)
    if grid.get('size')!=size:reject('block_grid.size','outside current physically supported Map policy',requested=grid.get('size'),supported=[size])
    actual={p['id']:p for p in case.get('ports',[])}
    if set(actual)!=set(ports):reject('block_ports','must cover every actual port exactly',actual=sorted(actual),declared=sorted(ports))
    reservations=copy.deepcopy(case.get('block_reservations',[]))
    for key,port in ports.items():
        stage=port.get('grid',{}).get('stagingPosition')
        if key not in actual:continue
        if stage!=actual[key]['position']:reject('ports.'+key+'.grid.stagingPosition','must bind the real Harness body checkpoint')
        if port.get('normal')!=actual[key].get('normal'):reject('ports.'+key+'.normal','cannot change a physical opening direction in metadata')
        if not isinstance(stage,list)or len(stage)!=2:
            reject('ports.'+key+'.grid.stagingPosition','explicit two-coordinate checkpoint required');continue
        reservations.append([stage[0]-12,stage[1]-18,24,36])
        if port.get('grid',{}).get('profile')=='ground64/v1':
            anchor=port.get('position',[]);normal=port.get('normal',[])
            if len(anchor)!=2 or normal not in [[-1,0],[1,0]]:
                reject('ports.'+key+'.grid.profile','ground64 is a horizontal interface, not a rotated vertical one');continue
            if abs(stage[1]-anchor[1]-14)>1e-6:reject('ports.'+key+'.grid.stagingPosition','ground64 standing centre must be anchorY+14')
            if (stage[0]-anchor[0])*normal[0]>-12:reject('ports.'+key+'.grid.stagingPosition','complete body must stage inside its module')
            if port.get('crossing_offset',[0,14])!=[0,14]:reject('ports.'+key+'.crossing_offset','ground64 requires the original +14 crossing offset')
    if not conflicts:
        projection=dict(case=case,ports=ports,block_grid=grid,action_clearance=reservations,
                        enemy_envelopes_verified=False)
        try:errors=validate(projection)
        except (KeyError,TypeError,ValueError)as error:errors=['invalid_block_projection/'+str(error)]
        for error in errors:reject('block_grid',error)
    return dict(status='unsatisfied'if conflicts else'requires_physics',conflicts=conflicts,
                physics_cases=0,scope='Original Map Python contract; exported objects, gate B, mounted-bell envelopes and actual sweeps are also checked by the original JS validator.')


def inspect_sources(cases):
    rows=[dict(case_id=c['id'],**inspect_case(c))for c in cases]
    return dict(status='requires_physics'if rows and all(r['status']=='requires_physics'for r in rows)else'needs_design',
                cases=rows,searched=dict(case_count=len(cases),block_size=json.loads(POLICY.read_text())['block_size']),
                negotiable=['new Block-native geometry/control version','bounded terminal-bank adaptation with fresh physics','explicitly supported port/profile/state'],
                may_add_map_terrain=False,may_reset_resources=False,production_admitted=False)


def inspect_counter_bindings(cases,alternatives,minimum=18):
    """Reuse the original evidence keys before paying for real experiments."""
    rows=[];seen=set();conflicts=[]
    for case in cases:
        proposed=alternatives(case);bound=[]
        for counter in proposed:
            identity=counter['id']
            if identity in seen:conflicts.append(dict(field='counter.id',reason='duplicate_counter_identity',id=identity))
            seen.add(identity)
            same_blocks=all(counter.get(k)==case.get(k)for k in ['block_grid','block_ports','block_reservations'])
            if identity.split('-counter-')[0]==case['id']and geometry_key(counter)==geometry_key(case)and same_blocks:bound.append(identity)
        if len(bound)<minimum:conflicts.append(dict(field='counter.source_binding',reason='original_evidence_base_id_or_exact_geometry_coverage_missing',case_id=case['id'],required=minimum,actual=len(bound),proposed=len(proposed)))
        rows.append(dict(case_id=case['id'],proposed=len(proposed),exact_identity_geometry_bindings=len(bound)))
    return dict(status='needs_design'if conflicts else'requires_physics',conflicts=conflicts,cases=rows,physics_cases=0,
                scope='Original evidence identity/geometry keys plus exact Block ownership/port/reservation binding; no physical or design success inferred.')
