"""Open landform grammar sample. All terrain belongs to a requested Module.

No enclosure is inferred from bounds. These are fixed calibration productions,
not a claim of arbitrary-seed/Hollow-Knight-quality generation.
"""
import copy
from .synthesis import command
from .three_port import gear_cross
from ..factory.core.quality import digest
from .engine import ROOT
import json

# World-space art direction is supplied by the Director as one bounded motif.
# Each production returns its own complete geometry and physically tested inputs.
def generate(spec):
    key=spec['node_id'];dx,dy=spec['placement']
    platforms=[];oneway=[];ports={};saws=[];latches=[];carriers=[]
    def add(rect,one=False):
        i=len(platforms);platforms.append([rect[0]-dx,rect[1]-dy,*rect[2:]])
        if one:oneway.append(i)
        return i
    def land(x1,x2,body,depth,root=False,one=False):
        idx=add([x1,body+18,x2-x1,depth],one)
        # Actual jagged underside, not a bounding wall or a decorative fake floor.
        if root and not one:
            w=x2-x1
            for a,b,extra in [(0,.22,26),(.22,.57,54),(.57,.84,38),(.84,1,15)]:
                add([x1+w*a,body+18+depth,w*(b-a),extra])
        return idx
    def point(x,y,label):
        local=[x-dx,y-dy]
        indices=[i for i,p in enumerate(platforms)if abs(p[1]-(local[1]+18))<.01 and p[0]+12<=local[0]<=p[0]+p[2]-12]
        if not indices:raise ValueError('open_landing_has_no_support/'+key+'/'+label+'/'+str((x,y)))
        return dict(id=key+'/'+label,position=local,region=[local[0]-8,local[1]-4,16,8],support_indices=indices,grounded=True)
    def leg(kind,x,y,label,hold=20):
        result=dict(kind=kind,target=point(x,y,label))
        if kind=='jump':result['hold_ticks']=hold
        return result
    def seq(values):return [leg(*v)for v in values]
    def import_core(old,entry_world,bell_id,source):
        ox=entry_world[0]-old['entry_port'][0];oy=entry_world[1]-old['entry_port'][1]
        receiver=old['platforms'][1]
        add([receiver[0]+ox,receiver[1]+oy,receiver[2],16],True)
        for raw in old['latches']:
            v=copy.deepcopy(raw);v['id']=bell_id;v['bell']=[raw['bell'][0]+ox-dx,raw['bell'][1]+oy-dy]
            v['gate']=[raw['gate'][0]+ox-dx,raw['gate'][1]+oy-dy,*raw['gate'][2:]];latches.append(v)
        plan=copy.deepcopy(old['control_plan'])
        for op in plan:
            if 'target_x'in op:op['target_x']+=ox-dx
        return dict(entry=point(*entry_world,'air-shot-entry'),exit=point(old['exit_port'][0]+ox,old['exit_port'][1]+oy,'air-shot-exit'),control_plan=plan,source=source)
    vertical=json.loads((ROOT/'results/direct-vertical-bell-v2/selected.json').read_text())['case']
    fork_source='results/plains-three-port-production-v1/review_cases.json'
    angled=next(c for c in json.loads((ROOT/fork_source).read_text())['cases']if c.get('route_spec',{}).get('id')=='upper')
    core=None
    if key=='west':
        land(0,230,820,260,True);land(240,460,940,180,True)
        core=import_core(vertical,[100,820],'entry-bell','results/direct-vertical-bell-v2/selected.json')
        land(228,460,640,16,one=True);land(230,460,640,64,True)
        center=point(100,820,'center')
        outbound={'e0':[dict(kind='module',target=core['exit'],control_plan=core['control_plan'])]+seq([('walk',436,640,'e0')]),
                  'e4':seq([('walk',180,820,'lip'),('drop',340,940,'underhang'),('walk',436,940,'e4')])}
        inbound={'e0':seq([('walk',160,640,'receiver'),('drop',100,820,'center')]),
                 'e4':seq([('walk',290,940,'lower-takeoff'),('jump',180,820,'return'),('walk',100,820,'center')])}
    elif key=='ridge':
        land(460,650,640,46,True)
        core=import_core(angled,[520,640],'ridge-bell',fork_source)
        end=angled['platforms'][1][0]+angled['platforms'][1][2]+440
        land(end,920,460,16,one=True);land(860,920,460,80,True)
        center=core['exit']
        return_plan=copy.deepcopy(core['control_plan'])
        for op in return_plan:
            if op['op']=='axis':op['value']=-1
            if op['op']=='shoot':op['direction']=[.5,.8660254037844386]
            if 'target_x'in op:op['target_x']=576-dx
        outbound={'e0':[dict(kind='module',target=point(576,640,'return-recoil'),control_plan=return_plan)]+seq([('walk',484,640,'e0')]),
                  'e1':seq([('walk',896,460,'e1')])}
        inbound={'e0':seq([('walk',520,640,'shot-entry')])+[dict(kind='module',target=core['exit'],control_plan=core['control_plan'])],
                 'e1':seq([('walk',center['position'][0]+dx,460,'center')])}
    elif key=='lookout':
        land(920,1120,460,54,True);land(1080,1250,460,42,True);land(1250,1320,520,64,True)
        center=point(1160,460,'center')
        outbound={'e1':seq([('walk',1000,460,'lower'),('walk',944,460,'e1')]),
                  'e2':seq([('walk',1220,460,'edge'),('drop',1296,520,'e2')])}
        inbound={'e1':seq([('walk',1040,460,'takeoff'),('walk',1160,460,'center')]),
                 'e2':seq([('jump',1160,460,'center')])}
    elif key=='arch':
        landing=land(1320,1480,520,16,one=True);land(1480,1640,580,16,one=True);land(1640,1740,600,16,one=True)
        core=import_core(angled,[1360,520],'arch-bell',fork_source)
        saws=[dict(source_id='bridge-gear',origin=[1640-dx,588-dy],travel=[0,-70],radius=16,period=2.4,initial_phase=0.)]
        center=point(1540,580,'center')
        outbound={'e2':seq([('jump',1440,520,'upper'),('walk',1344,520,'e2')]),
                  'e3':seq([('jump',1716,600,'e3')]),
                  'e7':seq([('jump',1462,520,'e7')])}
        inbound={'e2':seq([('walk',1360,520,'air-shot-entry')])+[dict(kind='module',target=core['exit'],control_plan=core['control_plan'])]+seq([('drop',1540,580,'center')]),
                 'e3':seq([('jump',1540,580,'center')]),
                 'e7':seq([('jump',1540,580,'center')])}
    elif key=='east':
        land(1740,1860,600,84,True);land(1860,2030,680,24);land(2030,2200,640,16,one=True)
        land(1600,1760,1040,190,True);land(1760,1900,940,155,True);land(1900,2110,860,90,True);land(2110,2310,760,60,True)
        center=point(2160,640,'center')
        outbound={'e3':seq([('walk',1940,680,'return-lip'),('jump',1800,600,'upper'),('walk',1764,600,'e3')]),
                  'e6':seq([('drop',2160,760,'outer-spur'),('drop',2000,860,'mid-spur'),('drop',1820,940,'root-spur'),('drop',1624,1040,'e6')])}
        inbound={'e3':seq([('drop',1940,680,'saddle'),('walk',2006,680,'takeoff'),('jump',2100,640,'ruin'),('walk',2160,640,'center')]),
                 'e6':seq([('walk',1736,1040,'takeoff-1'),('jump',1820,940,'root-spur'),('walk',1876,940,'takeoff-2'),('jump',2000,860,'mid-spur'),('walk',2086,860,'takeoff-3'),('jump',2160,760,'outer-spur'),('jump',2160,640,'center')])}
    elif key=='hollow':
        land(460,650,940,200,True);land(650,850,1020,140,True);land(850,1050,1040,180,True)
        center=point(760,1020,'center')
        saws=[dict(source_id='valley-gear',origin=[950-dx,1028-dy],travel=[0,-70],radius=16,period=2.4,initial_phase=0.)]
        outbound={'e4':seq([('walk',674,1020,'takeoff'),('jump',580,940,'west-step'),('walk',484,940,'e4')]),
                  'e5':seq([('drop',960,1040,'basin'),('walk',1026,1040,'e5')])}
        inbound={'e4':seq([('walk',610,940,'lip'),('drop',760,1020,'center')]),
                 'e5':seq([('walk',900,1040,'takeoff'),('jump',780,1020,'center')])}
    elif key=='bell':
        land(1050,1600,1040,190,True)
        reward=land(1096,1288,860,16,one=True)
        landing=land(1320,1480,520,16,one=True)
        center=point(1160,1040,'center')
        carriers=[dict(platform_id='valley-return',start=[1400-dx,1070-dy],finish=[1400-dx,566-dy],size=[128,24],travel_duration=2.2,dwell_duration=.6,initial_phase=0.)]
        selected=json.loads((ROOT/'results/direct-vertical-bell-v2/selected.json').read_text())['case']
        # Reuse the measured core, then validate this whole open placement afresh.
        ox,oy=1080-dx,620-dy
        for raw in selected['latches']:
            v=copy.deepcopy(raw);v['id']='valley-bell';v['bell']=[raw['bell'][0]+ox,raw['bell'][1]+oy];v['gate']=[raw['gate'][0]+ox,raw['gate'][1]+oy,*raw['gate'][2:]];latches.append(v)
        latches[-1]['starts_ferry']='valley-return'
        plan=copy.deepcopy(selected['control_plan'])
        for op in plan:
            if 'target_x'in op:op['target_x']+=ox
        core=dict(entry=center,exit=point(1220,860,'reward'),control_plan=plan,source='results/direct-vertical-bell-v2/selected.json')
        outbound={'e5':seq([('walk',1074,1040,'e5')]),
                  'e6':seq([('walk',1304,1040,'well-takeoff'),('walk',1510,1040,'well-crossing'),('walk',1576,1040,'e6')]),
                  'e7':seq([('walk',1304,1040,'well-takeoff')])+[dict(kind='module',control_plan=[command('wait')],target=point(1462,520,'e7'),budget_ticks=1000,
                    carrier_transfer={'id':'valley-return','mode':'ascend','source_level':1040-dy,'destination_level':520-dy,'bearing':1,'target_x':1462-dx})]}
        inbound={'e5':seq([('walk',1160,1040,'center')]),
                 'e6':seq([('walk',1504,1040,'well-takeoff'),('walk',1280,1040,'well-crossing'),('walk',1160,1040,'center')]),
                 'e7':seq([('drop',1504,1040,'well-bottom'),('walk',1280,1040,'well-crossing'),('walk',1160,1040,'center')])}
    else:raise ValueError('unsupported_open_landform/'+key)
    if key=='hollow':
        def pressure(target_x,label,direction):
            plan=gear_cross(target_x-dx,950-dx,direction)
            for op in plan:
                q=op.get('trigger',{}).get('dynamic',{})
                if q.get('kind')=='saw_phase':q['id']='valley-gear'
            return dict(kind='module',control_plan=plan,target=point(target_x,1040,label),budget_ticks=720)
        outbound['e5']=[pressure(1026,'e5',1)]
        inbound['e5']=[pressure(900,'gear-return',-1),leg('jump',780,1020,'center')]

    for p in spec['ports']:
        v=copy.deepcopy(p);v['dock']=point(*p['dock_world'],p['id']);v.pop('dock_world')
        if p['kind']=='vertical':v['shared_landing_index']=landing
        ports[p['id']]=v
    case=dict(id='open-'+key,family='plains_open_landform',capabilities=['move','jump','shot_recoil'],platforms=platforms,one_way_platform_indices=oneway,
        wall_platform_indices=[],world_bounds=[-64,-160,spec['space']['core_bounds'][2]+128,spec['space']['core_bounds'][3]+320],
        spawn=center['position'],entry_port=center['position'],exit_port=[center['position'][0]+32,center['position'][1]],goal=[center['position'][0]+20,center['position'][1]-5,24,10],
        control_plan=[],max_frames=3600,trace_all=False,hazards=[],thorns=[],saws=saws,moving_platforms=carriers,latches=latches,hooks=[],enemies=[])
    result=dict(id=key,spec=copy.deepcopy(spec),case=case,ports=ports,center=center,center_to_port=outbound,port_to_center=inbound,
        core=core,core_visit_program=[],boundary_gates=[],assembly_created_geometry=False,
        quality={'human_fun':'unverified','production_admitted':False},origin='open terrain grammar + original measured recoil-bell core')
    if key=='bell':result['core_visit_program']=[dict(kind='module',target=core['exit'],control_plan=plan,budget_ticks=720),leg('drop',1220,1040,'reward-return'),leg('walk',1160,1040,'center')]
    result['content_version']='sha256:'+digest({k:result[k]for k in ['case','ports','core','boundary_gates']})
    return result
