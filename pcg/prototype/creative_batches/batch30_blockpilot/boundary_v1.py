"""One exact boundary specimen, never a Map generator or new simulator."""
import copy
from pathlib import Path
from . import api_v2 as module
from pcg.map_directed.block_grid.contracts import raster
from pcg.prototype.creative_batches.batch30_seams.fixtures_v1 import geometry_audit
from pcg.prototype.workshop.rules import cmd,settle,wait_x
from pcg.prototype.factory.core.quality import digest,module_hash

HERE=Path(__file__).parent
RUNNER_SCRIPT=module.RUNNER_SCRIPT
NATIVE_SCENE=module.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(module.__file__),*module.SOURCE_DEPENDENCIES,HERE/'boundary-protocol-v1.json',HERE.parent/'batch30_seams/fixtures_v1.py']


def mirror_receiver(source):
    c=copy.deepcopy(source)
    def point(p):return[1792-p[0],p[1]]
    def rect(r):return[1792-r[0]-r[2],r[1],r[2],r[3]]
    c['platforms']=[rect(r)for r in source['platforms']]
    for l in c['latches']:
        for field in ['bell','return_access']:
            if field in l:l[field]=point(l[field])
        for field in ['gate','paired_gate']:
            if field in l:l[field]=rect(l[field])
    c['control_plan']=[]
    cells=sorted([[13-x,y]for x,y in source['block_grid']['cells']])
    c['block_grid']['cells']=cells
    return c


def prefixed(case,label):
    c=copy.deepcopy(case);mapping={l['id']:label+'/'+l['id']for l in c['latches']}
    for l in c['latches']:l['id']=mapping[l['id']]
    for q in c['control_plan']:
        a=q.get('aim_cell')
        if a and a.get('kind')=='bell':a['id']=mapping[a['id']]
    return c


def case():
    left=module.layouts(module.RECIPES[0],0)[0];right=mirror_receiver(left)
    left_cells=set(map(tuple,left['block_grid']['cells']));right_cells=set(map(tuple,right['block_grid']['cells']))
    if left_cells&right_cells:raise ValueError('owned_blocks_overlap')
    audit=geometry_audit(left,right)
    if not audit['accepted']:raise ValueError(audit)
    a=prefixed(left,'left');b=prefixed(right,'receiver');c=copy.deepcopy(a)
    c['platforms']=copy.deepcopy(a['platforms']+b['platforms']);c['latches']=copy.deepcopy(a['latches']+b['latches'])
    c['reward_sites']=[]
    c['control_plan']=copy.deepcopy(a['control_plan'])+[wait_x(870),cmd('wait',20),settle(920,0),wait_x(918),cmd('wait',20),settle(840,0),wait_x(842,-1),cmd('wait',20)]
    c['id']='b30-block-boundary-v1-c0';c['family']='block128-exact-boundary-fixture'
    c['exit_port']=[840,462];c['goal']=[838,458,4,8];c['max_frames']=1800
    c['ports']=[copy.deepcopy(a['ports'][0]),dict(id='B',position=[840,462],normal=[1,0],support_index=1)]
    c['route_spec']=dict(id='exact-ground64-boundary-and-back',from_port='A',to_port='B',role='fixture',via_ports=[])
    c['required_rewards']=[];c['expected_reward']=0
    c['boundary_fixture']=dict(source_left_case=left,source_input_sha256=module_hash(left),
        source_receiver_geometry_sha256=digest(dict(platforms=right['platforms'],latches=right['latches'])),
        mirror_about_x=384,right_translation=[1024,0],actual_anchor=[896,448],body_crossing_y=462,
        source_union_preserved=True,added_solid_area=0,removed_solid_area=0,owned_block_overlap=[],
        union_cells=sorted(map(list,left_cells|right_cells)),geometry_audit=audit,
        scope='New mirrored receiving geometry version, boundary-only proof; no mirror challenge/reverse/map admission')
    c['boundary_fixture']['fixture_version']='sha256:'+digest(dict(platforms=c['platforms'],latches=c['latches'],control_plan=c['control_plan'],left_input=module_hash(left)))
    for key in ['block_grid','block_ports','block_reservations','map_specification','source_map_request','map_request_response']:c.pop(key,None)
    return c


def purpose(c,r):
    fs=r.get('frames',[]);meta=c['boundary_fixture'];why=[];plane=meta['actual_anchor'][0];height=meta['body_crossing_y']
    left=meta['source_left_case'];source_check=module.rules.geometry.source.purpose(left,r)
    why += ['left/'+x for x in source_check['reasons']if x!='required_reward_not_claimed']
    at=lambda f,x:bool(f.get('grounded'))and abs(f['y']-height)<=.3 and abs(f['x']-x)<=2 and abs(f.get('vx',99))<=1
    dock_left=[f for f in fs if at(f,872)]
    dock_right=[f for f in fs if at(f,920)]
    right_full=[f for f in fs if f.get('grounded')and abs(f['y']-height)<=.3 and f['x']-12>=plane+1]
    right_first=right_full[0]['frame']if right_full else 10**9
    returned=[f for f in fs if f['frame']>right_first and f.get('grounded')and abs(f['y']-height)<=.3 and f['x']+12<=plane-1]
    forward=[b for a,b in zip(fs,fs[1:])if a.get('grounded')and b.get('grounded')and a['x']<plane<=b['x']and abs(b['y']-height)<=.3]
    backward=[b for a,b in zip(fs,fs[1:])if a.get('grounded')and b.get('grounded')and a['x']>plane>=b['x']and abs(b['y']-height)<=.3]
    owned=set(map(tuple,meta['union_cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
    if len(dock_left)<6 or len(dock_right)<6:why.append('both_original_docks_not_stable')
    if not(forward and backward and right_full and returned):why.append('complete_body_two_boundary_directions_missing')
    if outside:why.append('body_outside_two_source_owned_union')
    if not r.get('ok'):why.append(r.get('reason','not_stable'))
    if r.get('hp')!=5 or r.get('returns'):why.append('harm_or_world_reset')
    if r.get('workshop',{}).get('coins',0)!=0:why.append('unrequested_reward')
    if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
    receiver=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id'].startswith('receiver/')),None)
    if not receiver or receiver.get('switch_count')!=0:why.append('untouched_receiver_initial_state_not_preserved')
    crossing=lambda f:{k:f.get(k)for k in ['frame','x','y','grounded','vx','shot_charges','shot_cooldown','energy','support_id']}
    return dict(ok=not why,reasons=why,causal=dict(original_airlock=source_check['causal'],left_dock_stable_frames=len(dock_left),right_dock_stable_frames=len(dock_right),forward_crossings=[crossing(f)for f in forward],backward_crossings=[crossing(f)for f in backward],complete_body_right_frames=len(right_full),complete_body_left_after_return=len(returned),outside_union_frames=outside[:8],untouched_receiver=receiver,added_solid_area=0,removed_solid_area=0),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
