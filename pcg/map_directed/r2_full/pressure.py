"""Original dynamic Cells placed by corridor role, with finite input policies.

These are candidate timing relations, not inherited Module passes or a claim
that waiting is necessary. Whole-world execution must validate each direction.
"""
from __future__ import annotations
import copy
from pcg.prototype.plains.synthesis import command
from pcg.prototype.factory.core.quality import digest


def enrich(compiled, edge_ids=('e14','e15','e22','e29','e35')):
    out=copy.deepcopy(compiled); placements=[]
    room_cells={tuple(p) for n in out['nodes'].values() for p in n['room_cells']}
    gated={s['edge_id'] for s in out['gate_specs']}
    for eid in edge_ids:
        if eid in gated: raise ValueError('timing_cell_cannot_share_state_gate/'+eid)
        edge=out['edges'][eid]
        cells=[tuple(p) for p in edge['planning_cells']]
        options=[]
        for i,(a,b) in enumerate(zip(cells,cells[1:])):
            if a in room_cells or b in room_cells or a[1]!=b[1]: continue
            # Reserve a straight passage: no corner walls or vertical crossflow.
            if i<1 or i+2>=len(cells):continue
            if cells[i-1][1]!=a[1] or cells[i+2][1]!=a[1]:continue
            options.append((abs(i-len(cells)/2),i,a,b))
        if not options: raise ValueError('no_straight_timing_aperture/'+eid)
        _,_,a,b=min(options)
        first=out['lower_targets'][str(a)];last=out['lower_targets'][str(b)]
        pa,pb=first['position'],last['position']
        saw_id='timing/'+eid
        saw=dict(source_id=saw_id,origin=[(pa[0]+pb[0])/2,pa[1]-2],
                 travel=[0,-42],radius=8,period=3.,initial_phase=0.)
        out['case']['saws'].append(saw)
        matched=[]
        for direction in ['forward_waypoints','reverse_waypoints']:
            path=edge[direction]
            for i in range(1,len(path)):
                source,target=path[i-1]['target'],path[i]['target']
                if {tuple(source['position']),tuple(target['position'])}!={tuple(pa),tuple(pb)}:continue
                replacement=copy.deepcopy(path[i]);replacement['kind']='module'
                replacement['timing_relation_id']=saw_id
                replacement['control_plan']=[
                    command('settle',target_x=source['position'][0],deadband=3),
                    dict(op='wait',trigger=dict(state='grounded',timeout=120)),
                    dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=saw_id,window=[.60,.65]),timeout=200)),
                    command('settle',target_x=target['position'][0],deadband=3),
                    command('jump'),command('jump_release',4),
                    command('settle',target_x=target['position'][0],deadband=3)]
                path[i]=replacement;matched.append(direction)
        if len(matched)!=(2 if edge['bidirectional']else 1):raise ValueError('missing_concrete_timing_transfer/'+eid)
        placements.append(dict(id=saw_id,edge_id=eid,cells=[list(a),list(b)],saw=saw,
            directions=matched,content_version='sha256:'+digest(saw),
            technical='unverified_new_whole_map_cell_relation',human_fun='unverified',
            necessity='not_proven; finite safe timing policy only'))
    out['timing_placements']=placements
    out['coverage']['new_timing_relations']=len(placements)
    out['status']='full_R2_with_original_dynamic_cells_pending_whole_map_validation'
    return out
