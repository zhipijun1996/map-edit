"""Concrete lowering of a small R2 cycle into versioned measured Module geometry.

This first consumer supports a three-port fork and a following ascent. It refuses
other motifs; it is not a general embedding solver or an inferred port adapter.
"""
import copy
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
from pcg.prototype.factory.core.quality import digest


def rect_bounds(case):
    rs=case['platforms'][:]+case.get('hazards',[])[:]
    for saw in case.get('saws',[]):
        x,y=saw['origin'];dx,dy=map(abs,saw['travel']);r=saw['radius']
        rs.append([x-dx-r,y-dy-r,2*(dx+r),2*(dy+r)])
    for latch in case.get('latches',[]):rs.append(latch['gate'])
    return [min(r[0] for r in rs),min(r[1] for r in rs),
        max(r[0]+r[2] for r in rs)-min(r[0] for r in rs),max(r[1]+r[3] for r in rs)-min(r[1] for r in rs)]


def overlap(a,b):
    return a[0]<b[0]+b[2]-1e-6 and a[0]+a[2]>b[0]+1e-6 and a[1]<b[1]+b[3]-1e-6 and a[1]+a[3]>b[1]+1e-6


def translated(raw,dx,dy,prefix):
    c=copy.deepcopy(raw)
    for key in ['factory_evidence','module_sha256','recorded_frames','validation_summary','factory_id','noise','route_spec']:
        c.pop(key,None)
    c['noise']={}
    def pt(p):return [p[0]+dx,p[1]+dy]
    for k in ['platforms','hazards']:
        c[k]=[[r[0]+dx,r[1]+dy,*r[2:]] for r in c.get(k,[])]
    for k in ['spawn','entry_port','exit_port']:c[k]=pt(c[k])
    c['goal']=[c['goal'][0]+dx,c['goal'][1]+dy,*c['goal'][2:]]
    for p in c.get('ports',[]):p['position']=pt(p['position'])
    for saw in c.get('saws',[]):saw['origin']=pt(saw['origin']);saw['source_id']=prefix+'/'+saw['source_id']
    for thorn in c.get('thorns',[]):thorn['surface_id']=prefix+'/'+thorn['surface_id']
    for latch in c.get('latches',[]):
        latch['id']=prefix+'/'+latch['id'];latch['bell']=pt(latch['bell']);latch['gate']=[latch['gate'][0]+dx,latch['gate'][1]+dy,*latch['gate'][2:]]
    for p in c['control_plan']:
        if 'target_x'in p:p['target_x']+=dx
        if 'aim_target'in p:p['aim_target']=pt(p['aim_target'])
        if 'aim_cell'in p:p['aim_cell']['id']=prefix+'/'+p['aim_cell']['id']
        q=p.get('trigger',{}).get('dynamic',{})
        if q.get('kind')=='actor_x':q['value']+=dx
        elif 'id'in q:q['id']=prefix+'/'+q['id']
    return c


def assemble(plan,fork_routes,ascent):
    from pcg.prototype.plains.three_port import geometry_hash
    if any(c.get(k) for c in list(fork_routes.values())+[ascent] for k in ['hooks','enemies','moving_platforms']):
        raise ValueError('unsupported_component_geometry_requires_adapter')
    if len({geometry_hash(c) for c in fork_routes.values()})!=1:raise ValueError('fork_routes_must_share_one_geometry_and_initial_state')
    if ascent['family']!='bell_lift' or fork_routes['main']['family']!='plains_three_port_fork':raise ValueError('unsupported_lowering_motif')
    # Choose full-geometry nonoverlap, never squeeze the 1600-wide pit substrate
    # into a 900-wide sketch or stretch an already validated challenge.
    first=fork_routes['main'];a=rect_bounds(first);b=rect_bounds(ascent)
    dx=a[0]+a[2]-b[0]
    fork={k:translated(v,0,0,'fork') for k,v in fork_routes.items()}
    tail=translated(ascent,dx,0,'ascent')
    platform_offset=len(first['platforms'])
    common=copy.deepcopy(fork['main'])
    for key in ['platforms','hazards','saws','latches','thorns','hooks','enemies','moving_platforms']:
        extra=copy.deepcopy(tail.get(key,[]))
        if key=='thorns':
            for t in extra:t['platform_index']+=platform_offset
        common[key]=common.get(key,[])+extra
    for key in ['one_way_platform_indices','wall_platform_indices']:
        common[key]=common.get(key,[])+[i+platform_offset for i in tail.get(key,[])]
    left_end=first['platforms'][0][0]+first['platforms'][0][2]
    right_begin=tail['platforms'][0][0]
    if right_begin<=left_end:raise ValueError('unsupported_connector_geometry')
    connector=[left_end,438,right_begin-left_end,60]
    if any(overlap(connector,r) for r in common['platforms']):raise ValueError('connector_overlaps_component_solid')
    if any(overlap(x,y) for x in first['platforms'] for y in tail['platforms']):raise ValueError('component_solid_overlap')
    connector_index=len(common['platforms']);common['platforms'].append(connector)
    common.update(world_bounds=[-500,-350,dx+1900,1400],ports=[],exit_port=tail['exit_port'],goal=tail['goal'],
        max_frames=2100,trace_all=False,capabilities=['move','jump','shot_recoil'])
    ca,cb,cc=[p['position']for p in first['ports']]
    def point_region(p):return [p[0]-26,p[1]-24,52,48]
    checkpoints=[dict(id=k,region=point_region(p),grounded=True,kind=kind,label=label) for k,p,kind,label in [
        ('entry',ca,'fork','溪谷入口'),('reward',cc,'reward','可选高台 / +12'),
        ('return_entry',ca,'fork','回到入口'),('rejoin',cb,'rejoin','汇合休整岸'),
        ('ascent_entry',tail['entry_port'],'rejoin','钟台接缝'),('exit',tail['exit_port'],'exit','钟台出口')]]
    seams=[{'id':'fork_to_connector','region':[left_end-18,380,36,70],'from':'fork.B','to':'connector'},
        {'id':'connector_to_ascent','region':[right_begin-18,380,36,70],'from':'connector','to':'ascent.entry'}]
    # Observation point is a landmark on the main arm, not an invented new Port.
    checkpoints.append(dict(id='observation',region=[first['saws'][0]['origin'][0]-100,396,70,48],grounded=True,kind='fork',label='下层观察岸'))
    tail_program=copy.deepcopy(tail['control_plan'])
    # The original controller's settle policy persists. Its goal must be moved
    # forward when beginning the next action, rather than issuing an axis that
    # an old settle-to-entry immediately overrides.
    if tail_program[0]['op']!='axis':raise ValueError('unsupported_ascent_start_program')
    tail_program[0]=dict(op='settle',target_x=tail['exit_port'][0]+600,deadband=4,trigger={'after':0})
    finish=[dict(op='settle',target_x=tail['entry_port'][0],deadband=4,trigger={'after':0}),
        dict(op='wait',trigger={'dynamic':{'kind':'actor_x','direction':'gte','value':tail['entry_port'][0]-5},'timeout':600}),
        dict(op='wait',trigger={'state':'grounded','timeout':180}),dict(op='wait',trigger={'after':8})]+tail_program
    # Rejoin and return movements use the existing measured programs. Clock,
    # resources, latches and actor persist through every section.
    route_plans={'main':fork['main']['control_plan'],
        'reward_rejoin':fork['upper_rejoin']['control_plan'],
        'reward_return':fork['upper']['control_plan']+[
            dict(op='wait',trigger={'state':'grounded','timeout':180})]+fork['return_upper']['control_plan']+[
            dict(op='wait',trigger={'dynamic':{'kind':'actor_x','direction':'lte','value':ca[0]+5},'timeout':180}),
            dict(op='wait',trigger={'after':8})]+fork['main']['control_plan']}
    required={'main':['entry','observation','rejoin','ascent_entry','exit'],
        'reward_rejoin':['entry','reward','rejoin','ascent_entry','exit'],
        'reward_return':['entry','reward','return_entry','observation','rejoin','ascent_entry','exit']}
    cases=[]
    for route,program in route_plans.items():
        c=copy.deepcopy(common);c.update(id='map-directed-'+route,family='map_directed_plains',control_plan=program+finish,
            map_semantics=dict(checkpoints=checkpoints,required_checkpoints=required[route],seams=seams,required_seams=[s['id'] for s in seams],
                rewards=[dict(id='high-cache',region=point_region(cc),amount=12)],required_rewards=[] if route=='main' else ['high-cache'],
                required_bells=['ascent/lift_bell']+([] if route=='main' else ['fork/lift_bell']),
                map_seed=plan['seed'],route_id=route))
        c['map_semantics']['geometry_sha256']=digest({k:c.get(k)for k in ['platforms','thorns','saws','latches','capabilities']})
        cases.append(c)
    record=dict(schema='map-notes/concrete-map-composition/v1',seed=plan['seed'],
        motif='one R2 regional cycle lowered through a three-port fork and single ascent',
        components=[dict(id='fork',translation=[0,0],raw_case_sha256=digest(first)),
            dict(id='ascent',translation=[dx,0],raw_case_sha256=digest(ascent))],
        cells=[dict(id='supported-connector',geometry=connector,contentVersion='sha256:'+digest(connector),platform_index=connector_index)],
        geometry_check={'component_solids_overlap':False,'connector_solids_overlap':False,
            'dynamic_and_action_clearance':'must be checked by concrete whole-map execution; not universally certified'},
        lowering_limit='This consumer supports this small cycle motif only; no general irregular-Macro graph embedding claim.')
    return cases,record
