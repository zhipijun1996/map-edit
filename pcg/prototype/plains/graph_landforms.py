"""Bounded new Macro recipes requested by one exploration graph, original Motor."""
import copy,math
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.plains.block_modules import port,recoil
from pcg.prototype.plains.spatial_interchange import target
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate,connected
from pcg.prototype.factory.core.quality import digest

def walk(c,p,label):return dict(kind='walk',target=target(c,p,label),budget_ticks=360)
def jump(c,p,label,direction,vertical=.8):return recoil(c,p,label,direction,vertical)
def make(family,platforms,oneways,center,ports,paths,reserved_cells=(),estimate_clearance=True):
    c=base('landform-'+family);c.update(family='graph_landform_'+family,platforms=platforms,one_way_platform_indices=oneways,
        wall_platform_indices=[],reward_sites=[],shop_sites=[],control_plan=[],max_frames=2400,trace_all=False)
    ps={k:port(c,k,cell,edge,dock)for k,cell,edge,dock in ports}
    c.update(spawn=list(center),entry_port=list(center),exit_port=list(center),goal=[center[0]-7,center[1]-4,14,8])
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ps.items()]
    outbound={k:paths(c,k,False)for k in ps};inbound={k:paths(c,k,True)for k in ps}
    m=dict(id=family,case=c,ports=ps,center=target(c,center,'choice'),core=None,core_visit_program=[],
        center_to_port=outbound,port_to_center=inbound,boundary_gates=[],action_clearance=[],functional_roles=['traversal'],
        motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),
        spec=dict(id='graph-landform-demand/'+family,node_id=family,node=dict(id=family,role='challenge'),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[0,-512,max(p[0]+p[2]for p in platforms),2304]),ports=list(ps.values())),
        adaptation=dict(added_map_geometry=0,recipe=family,source_physics_inherited=False,explicit_empty_reservations=list(map(list,reserved_cells))),variant_id=family,
        selection_family=family,source_shape_sha256=digest(platforms))
    # Reserve conservative motion envelopes, clipped to own x-span. Actual
    # independent traces later replace these estimates before Map search.
    width=max(p['position'][0]for p in ps.values())
    width=max(width,max(r[0]+r[2]for r in platforms))
    for direction,program in [('in',inbound),('out',outbound)]:
        for key,legs in program.items():
            if not estimate_clearance:continue
            prev=ps[key]['dock']['position']if direction=='in'else center
            for leg in legs:
                p=leg['target']['position'];x=max(0,min(prev[0],p[0])-16);right=min(width,max(prev[0],p[0])+16)
                top=min(prev[1],p[1])-220 if leg['kind']=='module'else min(prev[1],p[1])-32
                m['action_clearance'].append([x,top,right-x,max(prev[1],p[1])+20-top]);prev=p
    cells=set().union(*(raster(r)for r in regions(m)));cells.update(map(tuple,reserved_cells))
    if not connected(cells):raise ValueError('recipe_disconnected_reservation/'+family)
    m=declare(m,cells);errors=validate(m)
    if errors:raise ValueError((family,errors))
    ys=[v[1]for v in cells];m['case']['world_bounds']=[-64,min(ys)*128-64,width+128,(max(ys)-min(ys)+1)*128+128]
    m['content_version']='sha256:'+digest(dict(case=m['case'],ports=ps,inbound=inbound,outbound=outbound));m['source_version']=m['content_version'];return m

def fork():
    platforms=[[48,480,160,96],[0,576,80,192],[384,96,128,96],[384,736,128,96],
        [224,352,128,24],[160,224,128,24],[224,608,128,24]]
    def paths(c,k,inside):
        if k=='upper':
            points=[([448,78],'walk'),([224,206],'walk'),([288,334],'drop'),([128,462],'walk')]if inside else[([288,334],'jump'),([224,206],'jump'),([448,78],'jump'),([488,78],'walk')]
        else:points=[([288,590],'jump'),([128,462],'jump')]if inside else[([288,590],'walk'),([448,718],'walk'),([488,718],'walk')]
        start=[488,78]if k=='upper'else[488,718]
        if not inside:start=[128,462]
        out=[]
        for i,(p,kind)in enumerate(points):out.append(jump(c,p,k+str(i),1 if p[0]>start[0]else-1)if kind=='jump'else dict(walk(c,p,k+str(i)),kind=kind));start=p
        return out
    m=make('split-cliff',platforms,[4,5,6],[128,462],[('upper',[3,0],'E',[488,78]),('lower',[3,5],'E',[488,718])],paths);m['functional_roles']=['junction','fork'];return m

def ascent(width=640,rise=256):
    end_y=334-rise;mid_y=334-rise/2;mid_x=width/2
    platforms=[[0,352,256,96],[0,448,96,128],[width-256,end_y+18,256,96],[width-128,end_y+114,128,128],[mid_x-64,mid_y+18,128,24],[256,352,128,128],[384,224,128,256]]
    center=[176,334];end=[width-24,end_y]
    def paths(c,k,inside):
        if k=='in':return [walk(c,center,'in-choice')]if inside else[walk(c,[24,334],'in-exit')]
        if inside:return [walk(c,[width-128,end_y],'upper-rim'),walk(c,[mid_x,mid_y],'slope-return'),walk(c,center,'choice-return')]
        return [jump(c,[mid_x,mid_y],'rise-step',1),jump(c,[width-128,end_y],'rise-rim',1),walk(c,end,'upper-exit')]
    return make(f'rising-shoulder-{width}-{rise}',platforms,[4],center,[('in',[0,2],'W',[24,334]),('out',[width//128-1,int((end_y-78)/128)],'E',end)],paths)

def descent(width=640):
    p=[[0,352,256,64],[0,416,64,192],[96,608,128,64],[width-192,608,192,128],[288,608,96,24],[256,480,128,24],
       [0,736,96,24],[128,864,96,24],[0,992,96,24],[128,1120,96,24],[0,1248,96,96]]
    center=[96,334];pocket=[144,590]
    def to_pocket(c):
        plan=[cmd('axis',value=1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=304),timeout=180)),cmd('shoot',12,direction=[1,0]),cmd('axis',1,value=-1),settle(144,8)]
        return [dict(kind='module',target=target(c,pocket,'under-cliff-brake'),control_plan=plan,budget_ticks=900)]
    def climb(c,pts,label):
        out=[];last=pts[0]
        for i,pt in enumerate(pts[1:]):out.append(jump(c,pt,label+str(i),1 if pt[0]>last[0]else-1,.15 if pt[1]==last[1]else .8));last=pt
        return out
    def paths(c,k,inside):
        if k=='in':return [walk(c,center,'cliff-entry')]if inside else[walk(c,[24,334],'cliff-back')]
        if k=='out':
            if not inside:return to_pocket(c)+climb(c,[pocket,[336,590],[width-96,590]],'low-gap')+[walk(c,[width-24,590],'lower-exit')]
            return [walk(c,[width-160,590],'back-bank')]+climb(c,[[width-160,590],[336,590],pocket,[304,462],[176,334]],'cliff-return')+[walk(c,center,'choice')]
        if inside:return climb(c,[[24,1230],[176,1102],[48,974],[176,846],[48,718],pocket,[304,462],[176,334]],'reward-climb')+[walk(c,center,'choice')]
        return to_pocket(c)+[walk(c,pt,'reward-drop'+str(i))for i,pt in enumerate([[48,718],[176,846],[48,974],[176,1102],[24,1230]])]
    m=make(f'braking-cliff-{width}',p,[4,5,6,7,8,9],center,[('in',[0,2],'W',[24,334]),('out',[width//128-1,4],'E',[width-24,590]),('reward',[0,9],'W',[24,1230])],paths);m['functional_roles']=['traversal','junction','reward_detour'];return m

def switchback(rise=512,width=768):
    # Four/fewer distinct elevation changes, no moving-platform waiting.
    n=rise//128;points=[[64,334]]+[[240 if i%2 else 320,334-i*128]for i in range(1,n+1)]
    end_y=334-rise;points[-1]=[432,end_y]
    p=[[0,352,160,96],[0,448,80,128],[384,end_y+18,width-384,96]]
    for i,pt in enumerate(points[1:-1]):p.append([pt[0]-64,pt[1]+18,128,24])
    def paths(c,k,inside):
        if k=='in':return [walk(c,points[0],'switch-entry')]if inside else[walk(c,[24,334],'switch-back')]
        if inside:return [walk(c,pt,'switch-return'+str(i))for i,pt in enumerate(reversed(points))]
        return [jump(c,pt,'switch-rise'+str(i),1 if pt[0]>points[i][0]else-1)for i,pt in enumerate(points[1:])]+[walk(c,[width-24,end_y],'switch-exit')]
    return make('switchback-'+str(rise),p,list(range(3,len(p))),points[0],[('in',[0,2],'W',[24,334]),('out',[width//128-1,int((end_y-78)/128)],'E',[width-24,end_y])],paths)

def merge():
    p=[[0,96,160,96],[0,192,80,128],[320,352,320,96],[512,448,128,128],[0,736,128,128],[176,224,128,24],[112,608,128,24],[192,480,128,24]]
    center=[384,334]
    def paths(c,k,inside):
        if k=='upper':pts=[[240,206],center]if inside else[[240,206],[64,78],[24,78]];last=[24,78]if inside else center
        else:pts=[[176,590],[256,462],center]if inside else[[256,462],[176,590],[24,718]];last=[24,718]if inside else center
        out=[]
        for i,pt in enumerate(pts):out.append(jump(c,pt,k+str(i),1 if pt[0]>last[0]else-1)if pt[1]<last[1]else walk(c,pt,k+str(i)));last=pt
        return out
    m=make('landmark-bowl',p,[5,6,7],center,[('upper',[0,0],'W',[24,78]),('lower',[0,5],'W',[24,718])],paths);m['functional_roles']=['merge','open_space'];return m

def reward(source):
    # New explicit reverse strategy on the SAME physical needle corridor.
    m=copy.deepcopy(source);c=m['case'];left=m['center']['position'];right=c['reward_sites'][0]['position'];port0=copy.deepcopy(m['ports']['in'])
    m['ports']={'in':port0};m['center']=target(c,right,'needle-cache');m['port_to_center']={'in':copy.deepcopy(m['port_to_center']['in']+m['center_to_port']['out'][:-1])}
    front=c['platforms'][1][0]+35
    plan=[cmd('axis',value=-1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='lte',value=front),timeout=180)),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,direction=[.9886859966642595,.15]),settle(left[0],6)]
    m['center_to_port']={'in':[dict(kind='module',target=target(c,left,'needle-return'),control_plan=plan,budget_ticks=900),walk(c,port0['dock']['position'],'exit-cache')]}
    c['reward_sites'][0]['amount']=18;c['ports']=[dict(id='in',position=port0['dock']['position'],normal=port0['normal'],support_index=port0['dock']['support_indices'][0])]
    m['functional_roles']=['reward'];m['variant_id']='needle-cache-foldback';m['selection_family']='needle-cache-foldback';m['adaptation']['reverse_relation']='NEW explicit same-world strategy; fresh proof required';return m
