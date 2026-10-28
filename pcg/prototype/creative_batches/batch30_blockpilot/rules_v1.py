"""Block128 terminal-profile adaptation over the measured C02 airlock.

The original recovery floor/stairs remain physical objects. No map, actor,
projectile or alternative simulation is introduced here.
"""
import copy
from pathlib import Path

from pcg.map_directed.block_grid.contracts import anchor,declare,raster,regions,validate
from pcg.prototype.creative_batches.batch30_c02 import api_v1 as source
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=('block128-serial-airlock',)
RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,
    HERE/'protocol-v1.json',HERE.parents[2]/'map_directed/block_grid/contracts.py']
DX,DY=82,-68


def shifted(old):
    """Translate every original Cell position, including the new paired door."""
    c=copy.deepcopy(old)
    def point(p):return[p[0]+DX,p[1]+DY]
    def rect(r):return[*point(r),*r[2:]]
    for key in ['platforms','hazards']:c[key]=[rect(r)for r in c.get(key,[])]
    for key in ['spawn','entry_port','exit_port']:c[key]=point(c[key])
    c['goal']=rect(c['goal'])
    for p in c.get('ports',[]):p['position']=point(p['position'])
    for l in c.get('latches',[]):
        l['bell']=point(l['bell']);l['gate']=rect(l['gate'])
        if l.get('paired_gate'):l['paired_gate']=rect(l['paired_gate'])
        if l.get('return_access'):l['return_access']=point(l['return_access'])
    for m in c.get('moving_platforms',[]):m['start']=point(m['start']);m['finish']=point(m['finish'])
    for s in c.get('saws',[]):s['origin']=point(s['origin'])
    for e in c.get('enemies',[]):e['position']=point(e['position'])
    for h in c.get('hooks',[]):h['x']+=DX;h['y']+=DY
    for r in c.get('reward_sites',[]):
        r['position']=point(r['position'])
        if r.get('region'):r['region']=rect(r['region'])
    for q in c['control_plan']:
        if 'target_x'in q:q['target_x']+=DX
        d=q.get('trigger',{}).get('dynamic',{})
        if d.get('kind')=='actor_x':d['value']+=DX
    return c


def block_port(key,cell,edge,dock):
    """Use upstream ground64/v1 anchor/profile/staging semantics."""
    p=anchor(cell,edge);normal=[-1,0]if edge=='W'else[1,0]
    return dict(id=key,position=p,normal=normal,
        grid=dict(cell=list(cell),edge=edge,profile='ground64/v1',stagingPosition=list(dock)),
        stagingPosition=list(dock),crossing_offset=[0,14],
        aperture=[p[0]-32,p[1]-32,64,64])


def adapted(old):
    c=shifted(old);interface=c['interface'];edits=[]
    for index in [0,7]:
        r=c['platforms'][index];before=r[:];bottom=r[1]+r[3]
        r[1]=352;r[3]=bottom-r[1]
        edits.append(dict(kind='entry_terminal_top',index=index,before=before,after=r[:],delta=r[1]-before[1]))
    r=c['platforms'][1];before=r[:];bottom=r[1]+r[3]
    r[1]=480 if interface==0 else 352;r[3]=bottom-r[1];r[2]=896-r[0]
    edits.append(dict(kind='exit_terminal_top_and_right_cut',index=1,before=before,after=r[:],delta=r[1]-before[1],extension=0))
    assert max(abs(e['delta'])for e in edits)<=32
    start=[-104,334];end=[872,r[1]-18]
    c['spawn']=start[:];c['entry_port']=start[:];c['exit_port']=end[:]
    c['goal']=[end[0]-25,end[1]-4,50,8]
    c['ports']=[dict(id='A',position=start,normal=[-1,0],support_index=7),dict(id='B',position=end,normal=[1,0],support_index=1)]
    for site in c['reward_sites']:
        site['position'][1]=end[1];site['region'][1]=end[1]-6
    for q in c['control_plan']:
        if q.get('op')=='settle':q['target_x']=end[0]
    block_ports={'A':block_port('A',[-1,2],'W',start),
                 'B':block_port('B',[6,3 if interface==0 else 2],'E',end)}
    # Conservative authored action reservations, not collision entities.
    reserves=[[-116,316,435,36],[288,32,448,576],
              [r[0],end[1]-18,896-r[0],36]]
    module=dict(case=c,ports=block_ports,action_clearance=reserves,functional_roles=['traversal'])
    physical=regions(module)
    physical += [l['paired_gate']for l in c.get('latches',[])if l.get('paired_gate')]
    physical += [[s['position'][0]-21,s['position'][1]-18,42,36]for s in c.get('reward_sites',[])]
    cells=set().union(*(raster(rect)for rect in physical))
    module=declare(module,cells);errors=validate(module)
    if errors:raise ValueError('block_pilot_static/'+','.join(errors))
    c['block_grid']=module['block_grid'];c['block_ports']=block_ports;c['block_reservations']=reserves
    c['block_adaptation']=dict(source_case_id=old['id'],source_layout_uid=old['layout_uid'],source_physics_inherited=False,
        translation=[DX,DY],terminal_edits=edits,entry_rebound_to_original_support=7,
        retained_recovery_platform_indices=[3,4,5,6,7],deleted_platform_indices=[],map_added_platforms=0)
    c['id']='b30-block-c02-v1-i'+str(interface)+'-c'+str(old['rule_parameters']['control'])
    if old.get('counterexample_kind'):c['id']+='-counter-'+old['counterexample_kind']
    c['production_recipe']=RECIPES[0];c['family']=RECIPES[0]
    c['layout_title']='Block128 空中换门 / '+('下沉一格接收岸'if interface==0 else'同高接收岸')
    c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
    c['generation_rule']=dict(id='batch30/block-native-C02',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
    s=c['map_specification'];s['id']='batch30/block-C02/'+str(interface);s['required_family']=RECIPES[0]
    s['objective'].update(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],source_relationship='serial-airlock-recoil',block_contract='map-notes/block-grid/v1')
    s['space'].update(max_width=1536,max_height=1024,max_port_span_x=1280,block_size=128,port_profiles=['ground64/v1'])
    s['resource_state']['entry']='Original supported body at interior W staging; true boundary crossing is separate fixture, no reset'
    s['return_conditions']='Original recovery geometry retained; new continuous recovery and reverse remain UNKNOWN until exact verification'
    return c


def candidate(interface=0,control=0):
    if interface not in [0,1]or control not in [0,1]:raise ValueError('outside registered Block pilot domain')
    return adapted(source.rules.materialize(interface,control))


def layouts(recipe,interface):
    if recipe!=RECIPES[0]:raise ValueError('unsupported Block recipe')
    return[candidate(interface,0)]


def purpose(c,r):
    q=source.purpose(c,r);outside=[];owned=set(map(tuple,c['block_grid']['cells']))
    for f in r.get('frames',[]):
        if not raster([f['x']-12,f['y']-18,24,36])<=owned:outside.append(f['frame'])
    q['causal']['unreserved_body_frames']=outside[:12]
    if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
    q['ok']=not q['reasons'];return q


def alternatives(c):
    interface=c['interface'];old=source.rules.materialize(interface,0)
    return[adapted(v)for v in source.alternatives(old)]
