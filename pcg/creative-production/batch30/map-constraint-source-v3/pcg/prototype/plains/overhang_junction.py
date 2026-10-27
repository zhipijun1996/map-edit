"""A concave rock junction with independently staggered east-facing mouths.

A high outer ridge and a tucked undercut mouth do not share a rectangle edge.
The lower return uses a vertical shot before steering under the overhang.
"""
import copy
from .branch_terraces import terrace,merge_rock_rows
from .graph_landforms import make,walk
from pcg.map_directed.content_domains.junctions import shelf_rise
from pcg.map_directed.catalog_feed.adapt import target
from pcg.map_directed.block_grid.contracts import declare,regions,raster,validate
from pcg.prototype.workshop.rules import cmd,settle


def generate(upper_span=640):
    if upper_span not in [640,768]:raise ValueError('overhang_upper_span_requires_640_or_768')
    old=terrace(640,256,256);center=[128,334]
    rocks=[[0,352,192,64],[320,96,upper_span-320,64],[0,608,128,96],[160,224,128,64],[128,480,128,32]]
    def paths(c,key,inside):
        if key in ['W','upper']:
            program=copy.deepcopy(old['port_to_center'][key]if inside else old['center_to_port'][key])
            if key=='upper'and inside and upper_span>640:program=[walk(c,[616,78],'ridge-return-launch')]+program
            if key=='upper'and not inside:program[-1]=walk(c,[upper_span-24,78],'outer-ridge-mouth')
            for leg in program:leg['target']=target(c,leg['target']['position'],leg['target']['id'])
            return program
        if not inside:return [walk(c,[232,462],'under-rock-lip'),walk(c,[104,590],'tucked-mouth')]
        plan=[cmd('axis',value=0),cmd('jump'),cmd('jump_release',8),cmd('shoot',2,direction=[0,1]),cmd('axis',4,value=1),settle(176,8)]
        return [dict(kind='module',target=target(c,[176,462],'vertical-recoil-under-overhang'),control_plan=plan,budget_ticks=900),walk(c,[232,462],'rim-launch'),shelf_rise(c,[128,334],'return-over-rim',-1),walk(c,center,'decision')]
    m=make('overhang-junction-compact-'+str(upper_span),rocks,[],center,[('W',[0,2],'W',[24,334]),('upper',[upper_span//128-1,0],'E',[upper_span-24,78]),('lower',[0,4],'E',[104,590])],paths,estimate_clearance=False)
    # Finite candidate envelopes; actual verified body samples replace these
    # before inventory matching. The launch keeps the body LEFT of the lower
    # boundary until it has risen above that boundary's Block row.
    m['action_clearance']=[[0,300,192,52],[80,400,48,208],[80,416,176,96],[112,160,144,352]]
    for key in ['W','upper']:
        for incoming,program in [(True,m['port_to_center'][key]),(False,m['center_to_port'][key])]:
            prev=m['ports'][key]['dock']['position']if incoming else center
            for leg in program:
                p=leg['target']['position'];x=max(0,min(p[0],prev[0])-16);right=min(upper_span,max(p[0],prev[0])+16);top=min(p[1],prev[1])-(320 if leg['kind']=='module'else 32)
                m['action_clearance'].append([x,top,right-x,max(p[1],prev[1])+20-top]);prev=p
    cells=set().union(*(raster(r)for r in regions(m)));m=declare(m,cells);errors=validate(m)
    if errors:raise ValueError(str(errors))
    m['case']['world_bounds']=[-128,-768,upper_span+256,1664];m['functional_roles']=['junction','fork','merge','open_space'];return m
