"""Isolated four-direction rock-well Macro rule requested by the Map Director.

No new physics, rewards, entry resets or inferred reverse relations. Every
ordered direction and the continuous excursion are separate real test cases.
This prototype is NOT registered as a production/regular-qualified family.
"""
import copy,itertools,json,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.factory.core.quality import digest

def target(c,point,label):
    x,y=point
    support=[i for i,r in enumerate(c['platforms'])if abs(r[1]-y-18)<.1 and r[0]<=x-12 and x+12<=r[0]+r[2]]
    if not support:raise ValueError('unsupported_junction_target/'+label)
    return dict(id=label,position=list(point),region=[x-7,y-4,14,8],support_indices=support,grounded=True,stable_ticks=6)

def generate(terrain='legacy'):
    c=base('rock-well-four-direction-prototype-v1');c['family']='spatial_interchange_prototype'
    c.update(platforms=[[0,420,240,180],[560,420,240,180],[240,180,320,200],[240,660,320,200],
        [240,540,80,24],[480,540,80,24],[160,300,80,24],[560,300,80,24]],
        one_way_platform_indices=[4,5,6,7],wall_platform_indices=[],world_bounds=[-80,0,960,960],
        reward_sites=[],shop_sites=[],control_plan=[],max_frames=2400,trace_all=False,
        spawn=[24,402],entry_port=[24,402],exit_port=[776,402],goal=[769,398,14,8])
    if terrain=='rooted':
        # Extend the west bank into an asymmetric rock root, leaving the
        # measured neighboring movement well open. These are collision Cells, not cosmetic
        # silhouettes or Map-created filler. Boundary docks stay unchanged.
        c['platforms'][0][3]=64
        c['platforms'] += [[0,484,80,216],[80,484,80,136]]
    elif terrain!='legacy':raise ValueError('unknown_rock_well_terrain')
    center=target(c,[400,642],'shared-decision-well')
    points={'W':([0,402],[-1,0],[24,402],0),'E':([800,402],[1,0],[776,402],1),
        'N':([400,162],[0,-1],[400,162],2),'S':([400,642],[0,1],[400,642],3)}
    ports={}
    for key,(plane,normal,dock,index)in points.items():
        p=dict(id=key,position=plane,normal=normal,kind='vertical'if key in ['N','S']else'side',aperture=[plane[0]-48,plane[1]-64,96,128],dock=target(c,dock,key+'/dock'))
        if key in ['N','S']:p['shared_landing_index']=index
        ports[key]=p
    def step(kind,pt,label):return dict(kind=kind,target=target(c,pt,label),budget_ticks=360)
    def recoil(pt,label,direction):
        # Real single-jump + diagonal downward shot. The horizontal component
        # has physical recoil; settle only steers, never sets actor position.
        from pcg.prototype.workshop.rules import cmd,settle
        plan=[cmd('axis',value=direction),cmd('jump'),cmd('jump_release',8),cmd('shoot',2,direction=[-direction*.6,.8]),settle(pt[0],8)]
        return dict(kind='module',target=target(c,pt,label),control_plan=plan,budget_ticks=720)
    to_center={
        'W':[step('walk',[400,642],'W/drop-to-choice')],
        'E':[step('walk',[400,642],'E/drop-to-choice')],
        'N':[step('walk',[720,402],'N/east-gallery'),step('walk',[400,642],'N/drop-to-choice')],
        'S':[step('walk',[400,642],'S/choice')]}
    from_center={
        'W':[recoil([280,522],'W/lower-ledge',-1),recoil([80,402],'W/gallery',-1),step('walk',[24,402],'W/exit')],
        'E':[recoil([520,522],'E/lower-ledge',1),recoil([720,402],'E/gallery',1),step('walk',[776,402],'E/exit')],
        'N':[recoil([280,522],'N/lower-ledge',-1),recoil([80,402],'N/gallery',-1),recoil([200,282],'N/upper-ledge',1),recoil([400,162],'N/exit',1)],
        'S':[step('walk',[400,642],'S/exit')]}
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ports.items()]
    m=dict(id='rock-well',case=c,ports=ports,center=center,core=None,center_to_port=from_center,port_to_center=to_center,
        core_visit_program=[],boundary_gates=[],action_clearance=[],source_shape_sha256=digest(c['platforms']),
        motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=0,maximum_entry_speed=1),
        spec=dict(id='map-demand/rock-well-four-direction/v1',node_id='rock-well',node=dict(id='rock-well',role='junction',label='断桥岩井 · 四向选择'),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[0,0,880,900]),ports=list(ports.values())),
        adaptation=dict(added_map_geometry=0,reward_budget=0,exterior_padding=0),variant_id='rock-well/'+terrain)
    m['content_version']='sha256:'+digest(dict(case=c,ports=ports,inbound=to_center,outbound=from_center));m['source_version']=m['content_version'];return m

def cases_for(m):
    routes=[([a,b],a+'-to-'+b)for a,b in itertools.permutations(m['ports'],2)]
    routes.append((['W','N','E','S','W','E'],'continuous-choice-return-then-exit'))
    out=[]
    for route,name in routes:
        c=copy.deepcopy(m['case']);program=[]
        for a,b in zip(route,route[1:]):program+=copy.deepcopy(m['port_to_center'][a]+m['center_to_port'][b])
        for i,leg in enumerate(program):leg.update(id=f'{i:03d}-'+leg['target']['id'],edge_id=name)
        start=m['ports'][route[0]]['dock'];end=m['ports'][route[-1]]['dock']
        c.update(id='rock-well-'+name,spawn=start['position'],entry_port=start['position'],exit_port=end['position'],goal=end['region'],
            pilot_program=program,map_budget_ticks=min(12000,max(3600,len(program)*360)),noise={},extra_required=False,
            route_spec=dict(id=name,from_port=route[0],to_port=route[-1],role='regional_transfer',via_ports=route[1:-1],require_bell=False))
        out.append(c)
    return out

def run(name,terrain='legacy'):
    from pcg.map_directed.director import REPO
    from pcg.map_directed.run import write
    from pcg.prototype.workshop.engine import WorkshopEngine
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_prototype_run_exists')
    files=[Path(__file__)]+list((REPO/'pcg/map_directed/r2_full/godot').glob('*.gd'))
    engine=WorkshopEngine(out,batch_size=1,extra_sources=files,runner_script=REPO/'pcg/map_directed/r2_full/godot/r2_runner.gd')
    m=generate(terrain);cs=cases_for(m);write(out/'module.json',m);write(out/'cases.json',dict(cases=cs));write(out/'protocol.json',dict(terrain=terrain,geometry_revisions=7,policy_revisions=4,ordered_routes=12,continuous_tours=1,rewards=0,scope='Unqualified rule prototype; no regular/production admission; never counted as whole Map'))
    rows=[]
    for c,r,e in engine.run(cs,'four-direction-prototype'):
        rows.append(dict(id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=r.get('pilot',{}).get('failure'),evidence=e))
        write(out/'rows.json',rows);print(json.dumps(dict(id=c['id'],ok=r['ok'],reason=r['reason'])),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),rows=rows,whole_map=False,production_admitted=False,regular_qualified=False));return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--terrain',choices=['legacy','rooted'],default='legacy');a=p.parse_args();print(run(a.name,a.terrain))
