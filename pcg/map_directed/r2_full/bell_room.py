"""Adapt one existing action Module into a full-map optional room loop.

Only this measured Plains seed0 room is supported. Old evidence is not carried
over: the compacted Module and every map splice need new physics witnesses.
"""
import copy
from pathlib import Path
import json
from pcg.map_directed.composition import translated
from pcg.prototype.factory.core.quality import digest


def install(compiled, module_path=None, library_match=None):
    out=copy.deepcopy(compiled)
    path=Path(module_path or Path(__file__).resolve().parents[2]/'results/r2-compact-bell-v1/summary.json')
    record=json.loads(path.read_text());raw=record['case']
    library_reference=None
    if library_match is not None:
        raw=library_match['case']
        library_reference={k:library_match['record'][k]for k in ['id','contentVersion','technical_status','production_admitted']}
        library_reference['record_path']=library_match['path']
    if raw['entry_port']!=[80,420] or abs(raw['exit_port'][1]-320)>1e-6:
        raise ValueError('unmatched_compact_module')
    room=out['nodes']['r12'];room_cells={tuple(c) for c in room['room_cells']}
    # Room bounds: [-2880,-2304,672,640]. Leave real 48wu side shafts
    # and a bottom bypass; no scaling/teleports or removal of a map edge.
    module=translated(raw,-2688,-2428,'r12/bell')
    remove={int(i) for i,cell in out['support_cells'].items() if tuple(cell) in room_cells}
    keep_ports={int(i) for p in room['ports'].values() for i in p['support_indices']}
    remove-=keep_ports
    platforms=out['case']['platforms'];mapping={};kept=[]
    for i,p in enumerate(platforms):
        if i in remove:continue
        mapping[i]=len(kept);kept.append(p)
    def remap(value):
        if isinstance(value,list):return [remap(v) for v in value]
        if not isinstance(value,dict):return value
        result={}
        for key,item in value.items():
            if key in ['support_indices','allowed_transit_support_indices']:
                # Room paths are replaced below; outside paths may refer to
                # the preserved port supports but no removed interior support.
                result[key]=[mapping[int(i)] for i in item if int(i) in mapping]
            elif key=='platform_index':result[key]=mapping[int(item)]
            else:result[key]=remap(item)
        return result
    out=remap(out);case=out['case'];room=out['nodes']['r12']
    case['platforms']=kept
    case['one_way_platform_indices']=[mapping[i] for i in compiled['case']['one_way_platform_indices'] if i in mapping]
    out['support_cells']={mapping[int(i)]:cell for i,cell in compiled['support_cells'].items() if int(i) in mapping}
    offset=len(kept)
    for key in ['platforms','hazards','saws','latches','enemies','moving_platforms','hooks']:
        case[key]+=copy.deepcopy(module.get(key,[]))
    for thorn in module.get('thorns',[]):
        thorn=copy.deepcopy(thorn);thorn['platform_index']+=offset;case['thorns'].append(thorn)
    def target(x,y,indices,label,width=32):
        return dict(id=label,position=[x,y],region=[x-12,y-5,24,10],support_indices=indices,
                    support_width=width,grounded=True,validation_status='new_splice_unverified')
    def pad(x,y,label,width=32):
        index=len(case['platforms']);case['platforms'].append([x-width/2,y+18,width,8])
        case['one_way_platform_indices'].append(index)
        return target(x,y,[index],label,width)
    # Under the pit substrate there is walking clearance, not jump clearance.
    # A short 496wu recovery floor joins the two existing bottom Port docks.
    band=len(case['platforms']);case['platforms'].append([-2792,-1696,496,8])
    bottom={x:target(x,-1714,[band],'r12/bypass/'+str(x),496) for x in [-2736,-2640,-2544,-2448,-2352]}
    bottom[-2832]=target(-2832,-1714,room['ports']['e23']['support_indices'],'r12/bypass/left-dock',80)
    right=copy.deepcopy(room['ports']['e4']['target']);bottom[-2256]=right
    room['center']=copy.deepcopy(bottom[-2544])
    def legs(targets,kind='jump',hold=4):
        return [dict(kind=kind,target=copy.deepcopy(t),hold_ticks=hold) for t in targets]
    for eid,port in room['ports'].items():
        if eid=='e23':xs=[-2640,-2736,-2832];dock=port['target']
        else:xs=[-2448,-2352,-2256];dock=port['target']
        room['center_to_port'][eid]=[dict(kind='walk',target=room['center'])]+legs([bottom[x]for x in xs],kind='walk')+[dict(kind='walk',target=dock)]
        room['port_to_center'][eid]=[dict(kind='walk',target=dock)]+legs([bottom[x]for x in xs[::-1]],kind='walk')+[dict(kind='walk',target=room['center'])]
    # Original left entry-port support is wide enough for x=-2856. This
    # optional branch rises through the narrow side shaft, then joins the
    # unchanged solid takeoff platform. The lower map route stays available.
    left=room['ports']['e23']['target']
    shaft=[pad(-2856,y,'r12/shaft/'+str(y)) for y in [-1778,-1842,-1906,-1970]]
    entry=target(module['entry_port'][0],module['entry_port'][1],[offset],'r12/bell/entry',360)
    takeoff_left=target(-2776,entry['position'][1],[offset],'r12/bell/approach',360)
    exit_target=target(module['exit_port'][0],module['exit_port'][1],[offset+1],'r12/bell/exit',192)
    safe_right=target(-2232,-1714,right['support_indices'],'r12/return/right-shaft',80)
    approach=room['center_to_port']['e23']+legs(shaft,hold=8)+[dict(kind='jump',hold_ticks=8,target=takeoff_left),dict(kind='walk',target=entry)]
    action=dict(kind='module',target=exit_target,control_plan=module['control_plan'],budget_ticks=900,
                entry=dict(grounded=True,region=entry['region'],support_indices=entry['support_indices'],required_air_shots=1,maximum_shot_cooldown=0))
    # Input-only walk off the receiver into the separately reserved right
    # shaft; target completion still requires its real original lower support.
    return_path=[dict(kind='walk',target=safe_right),dict(kind='walk',target=right)]+room['port_to_center']['e4']
    out['optional_challenges']=[dict(id='r12-bell-cache',node_id='r12',label='风铃侧室 / +8',reward=8,
        target=exit_target,required_bell='r12/bell/lift_bell',program=approach+[action]+return_path,
        source_module_sha256=digest(raw),candidate_status=library_reference['technical_status']if library_reference else record['candidate_status'],
        module_library_reference=library_reference,
        geometry_adaptation='versioned compact pit; unchanged action platforms/bell/gate; translation only after compaction',
        return_status='unverified_in_continuous_whole_world')]
    out['coverage']['adapted_existing_challenge_modules_inserted']=1
    out['coverage']['distinct_existing_challenge_modules_inserted']=1
    out['status']='full_R2_with_timing_cells_and_compact_bell_pending_whole_map_validation'
    return out
