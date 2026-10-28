"""Demand-driven Block-native variants; original actor, mechanisms and Harness."""
import copy,itertools,json,math
from pathlib import Path
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.measure import base
from pcg.prototype.plains.spatial_interchange import target,cases_for
from pcg.map_directed.block_grid.contracts import anchor,declare,validate,raster,regions,connected

def port(c,key,cell,edge,dock,size=128):
    p=anchor(cell,edge,size);normal={'W':[-1,0],'E':[1,0],'N':[0,-1],'S':[0,1]}[edge]
    vertical=edge in ['N','S'];profile='vertical-recoil-128/v1'if vertical else'ground64/v1'
    return dict(id=key,position=p,normal=normal,kind='vertical_ledge'if vertical else'side',
        crossing_offset=[0,0]if vertical else[0,14],
        aperture=[p[0]-48,p[1]-32,96,64]if vertical else[p[0]-32,p[1]-32,64,64],
        grid=dict(cell=list(cell),edge=edge,profile=profile),dock=target(c,dock,key+'/staging'),
        boundary_state='UNKNOWN until actual crossing; staging is NOT the boundary snapshot')

def recoil(c,point,label,direction,vertical=.8):
    from pcg.prototype.workshop.rules import cmd,settle
    plan=[cmd('axis',value=direction),cmd('jump'),cmd('jump_release',8),cmd('shoot',2,direction=[-direction*math.sqrt(1-vertical**2),vertical]),settle(point[0],8)]
    return dict(kind='module',target=target(c,point,label),control_plan=plan,budget_ticks=720)

def hub(size=128):
    if size!=128:raise ValueError('needs_design/block_hub_recipe_only_physically_calibrated_at_128')
    c=base('block-native-rock-interchange-v1');c['family']='block_native_interchange'
    c.update(platforms=[[0,352,256,64],[512,352,256,64],[320,96,256,64],[192,608,208,32],
        [256,480,80,24],[432,480,64,24],[256,224,80,24],[576,224,80,24],
        [0,416,64,80],[704,416,64,80]],one_way_platform_indices=[4,5,6,7],wall_platform_indices=[],
        spawn=[24,334],entry_port=[24,334],exit_port=[744,334],goal=[737,330,14,8],
        world_bounds=[-128,-128,1024,1024],reward_sites=[],shop_sites=[],trace_all=False,max_frames=3600,control_plan=[])
    center=target(c,[376,590],'shared-decision-well')
    ports={k:port(c,k,cell,k,dock,size)for k,cell,dock in [('W',[0,2],[24,334]),('E',[5,2],[744,334]),('N',[3,0],[448,78]),('S',[3,4],[376,590])]}
    def walk(p,label):return dict(kind='walk',target=target(c,p,label),budget_ticks=360)
    inbound={k:[walk([376,590],k+'/choice')]for k in ['W','E','S']}
    inbound['N']=[walk([688,334],'N/east-bank'),walk([376,590],'N/choice')]
    west=[recoil(c,[288,462],'W/lower',-1),recoil(c,[96,334],'W/bank',-1)]
    outbound=dict(W=west+[walk([24,334],'W/staging')],
        E=[recoil(c,[464,462],'E/lower',1),recoil(c,[608,334],'E/bank',1),walk([744,334],'E/staging')],
        N=copy.deepcopy(west)+[recoil(c,[288,206],'N/upper',1),recoil(c,[448,78],'N/cap',1,.65)],
        S=[walk([376,590],'S/staging')])
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ports.items()]
    m=dict(id='block-rock-well',case=c,ports=ports,center=center,core=None,center_to_port=outbound,port_to_center=inbound,
        core_visit_program=[],boundary_gates=[],action_clearance=[],functional_roles=['junction','vertical_traversal','open_space'],
        motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),
        spec=dict(id='map-demand/block-rock-well/v1',node_id='block-rock-well',node=dict(id='block-rock-well',role='hub',label='格状岩井'),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[0,0,768,640]),ports=list(ports.values())),
        source_shape_sha256=digest(c['platforms']),variant_id='block-rock-well/128',source_title='128 Block原生四向岩井',
        adaptation=dict(added_map_geometry=0,exterior_padding=0,physics='new validation required'))
    cells=[(x,y)for y in range(4)for x in range(6)]+[(x,4)for x in [1,2,3]]
    m=declare(m,cells,size);m['content_version']='sha256:'+digest(m);m['source_version']=m['content_version']
    errors=validate(m)
    if errors:raise ValueError(errors)
    return m

def run_probe(name):
    from pcg.map_directed.director import REPO
    from pcg.map_directed.run import write
    from pcg.prototype.workshop.engine import WorkshopEngine
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_block_probe_exists')
    files=[Path(__file__),REPO/'pcg/map_directed/block_grid/contracts.py']+list((REPO/'pcg/map_directed/r2_full/godot').glob('*.gd'))
    engine=WorkshopEngine(out,batch_size=1,extra_sources=files,runner_script=REPO/'pcg/map_directed/r2_full/godot/r2_runner.gd')
    m=hub();cs=cases_for(m);write(out/'module.json',m);write(out/'cases.json',dict(cases=cs))
    write(out/'protocol.json',dict(block_size=128,ordered_routes=12,continuous_tour=1,maximum_local_revisions=4,whole_map=False,production_admitted=False))
    rows=[];clearance=[]
    for c,r,e in engine.run(cs,'block-hub'):
        outside=[];cells=set(map(tuple,m['block_grid']['cells']))
        for f in r['frames'][::2]:
            rect=[f['x']-12,f['y']-18,24,36];clearance.append(rect)
            if not raster(rect)<=cells:outside.append(dict(frame=f['frame'],body=rect))
        row=dict(id=c['id'],ok=r['ok']and not outside,physics_ok=r['ok'],reason=r['reason'],unreserved_body=outside[:3],failure=r.get('pilot',{}).get('failure'),evidence=e)
        rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'measured-clearance.json',clearance);write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),whole_map=False,production_admitted=False));return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run_probe(a.name))
