"""Materialize exact approved drawings through the existing Module data format."""
import argparse
import copy
from pcg.migration import core,corners,physics
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from .first30_content_v2 import decode

AUTH=core.REPO/'feedback/manual-review/implementation-results/first-30-v2/authorization'
AUTHOR='pcg/manual_review/first30_author_v2.py'


def dock(p):
    x,y=p['position'];nx,ny=p['normal']
    return [x-24*nx,y+14]if nx else[x,y-24*ny]


def hop(x,dy=.7,hold=20):
    return [settle(x),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-(1-dy*dy)**.5,dy]),ground(),cmd('wait',12)]


def plan_for(n,target,source,design):
    a,z=target['from'],target['to'];ports={p['id']:dock(p)for p in design['ports']}
    match=next((c for c in source if c['route_spec']['from_port']==a and c['route_spec']['to_port']==z),source[0])
    p=copy.deepcopy(match['control_plan'])
    for v in p:
        if v.get('target_x')==match['exit_port'][0]:v['target_x']=ports[z][0]
    if n=='06':
        branch=source[1 if z=='C'else 0]['control_plan'][8:]
        if a=='A':p=copy.deepcopy(source[1 if z=='C'else 0]['control_plan'])
        else:
            middle=560 if a=='B'else 330;direction=-1 if a=='B'else 1
            p=[settle(middle),wait_x(middle-direction*6,direction),ground(),cmd('wait',12)]
            p+=copy.deepcopy(branch)if z!='A'else[settle(24),wait_x(30,-1),ground(),cmd('wait',20)]
        for v in p:
            if v.get('aim_cell',{}).get('kind')=='bell':v['aim_cell']['id']='upper-route-gears'
    elif n=='07':
        p=[settle(420),wait_x(414),settle(744),cmd('wait',12),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair')),ground(),cmd('wait',20)]
    elif n=='10':
        for v in p:
            if v.get('trigger',{}).get('dynamic',{}).get('value')==457:v['trigger']['dynamic']['value']=650
    elif n=='12' and not any(c['route_spec']['from_port']==a and c['route_spec']['to_port']==z for c in source):
        prefix=[]
        if a in ('B','C'):
            direction=1 if a=='B'else-1
            prefix=[settle(640),wait_x(620 if direction>0 else 660,direction),ground(),cmd('wait',12)]
        else:prefix=[settle(640),ground(),cmd('wait',12)]
        if z in ('B','C'):
            right=z=='C';destination=1010 if right else 270
            p=prefix+hop(destination,.72)+[settle(ports[z][0]),wait_x(ports[z][0]+(-6 if right else 6),1 if right else-1),ground(),cmd('wait',20)]
            if not right:
                for v in p[len(prefix):]:
                    if v['op']=='shoot':v['direction'][0]*=-1
        else:
            p=prefix+[cmd('shoot',aim_cell=dict(kind='bell',id=source[0]['latches'][0]['id'],receiver='access')),cmd('wait',30),ground(),cmd('wait',12),
                settle(240 if z=='A'else 1040),wait_x(246 if z=='A'else 1034,-1 if z=='A'else 1),cmd('jump'),cmd('jump_release',12),settle(ports[z][0]),ground(),cmd('wait',20)]
    elif n=='17' and a=='C':
        p=[settle(1050),wait_x(1056,-1),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='return-control')),cmd('wait',100),
            settle(900),cmd('jump'),cmd('jump_release',12),ground(),cmd('wait',70),settle(200),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.9,.435889894]),ground(),cmd('wait',20)]
    elif n=='23':
        if a=='A':p=[settle(-240),wait_x(-225,-1),cmd('shoot',direction=[-1,0]),settle(360 if z=='B'else-320),ground(),cmd('wait',20)]
        else:p=[settle(320),wait_x(326,-1),cmd('jump'),cmd('jump_release',8),cmd('shoot',aim_cell=dict(kind='enemy',id='design-lower-entry-sentry')),settle(-320),cmd('wait',90)]
        if z=='C':p=[v for v in p if v.get('trigger',{}).get('state')!='grounded']
    elif n=='28' and a=='B':
        p=[settle(540),wait_x(546,-1),ground(),cmd('wait',8),settle(152),cmd('jump'),cmd('jump_release',8),
            cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),ground(),cmd('wait',20)]
    return p,match


def prepare(row):
    n=row['reviewId'];out=core.REPO/row['outputDirectory']
    if out.exists():raise ValueError('candidate_exists:'+str(out))
    design=core.read(core.REPO/row['designFile']);doc=core.read(core.REPO/row['sourceModule']['file'])
    assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
    source=core.read((core.REPO/row['sourceModule']['file']).parent/'cases.json')['cases']
    g=doc['generationContract'];previous={o['id']:o for o in doc['objects']};objects=[]
    for visual in design['visualObjects']:
        o=copy.deepcopy(previous.get(visual['id'],{}));o.update(copy.deepcopy(visual))
        if o['type']=='route':o.pop('trajectory',None);o.setdefault('duration',1);o.setdefault('mode','once')
        if o['type']=='reward':
            value=o['mechanics']['source'];old=value['position'];center=[o['x']+o['w']/2,o['y']+o['h']/2]
            value['region']=[value['region'][0]+center[0]-old[0],value['region'][1]+center[1]-old[1],*value['region'][2:]];value['position']=center
        if o['type']=='hazard'and o.get('sourceType')in('spike','wallSpike')and o.get('hostId'):o['type']=o['sourceType']
        if o['type']=='enemy':o.setdefault('sourceId',o['id'].split('/')[-1]);o.setdefault('definition','plains_sentry');o.setdefault('mechanics',{})['initialIdleCooldown']=0
        if n=='06'and o.get('mechanics',{}).get('kind')=='design_retractable_gears':
            o['mechanics']['kind']='retractable_gears/v1'
            if o['type']=='bell':o.update(sourceId='upper-route-gears');o.pop('targetId',None);o.pop('targetIds',None)
        if n=='12'and o['type']=='gate':o['mechanics']=dict(kind='timed_gate',openSeconds=2.4)
        if n=='12'and o['id']=='design-upper-return-bell':
            primary=source[0]['latches'][0]['id'];gate=next(v for v in design['visualObjects']if v['type']=='gate')
            o.update(sourceId=primary+'/return',targetId=gate['id'],mechanics=dict(service='ShotLatch.add_access_bell',returnSideOnly=True))
        objects.append(o)
    static=[o for o in objects if o['type']in('terrain','platform')and not o.get('trackId')]
    for i,o in enumerate(static):o['sourceIndex']=i
    doc['objects']=objects;doc['title']=design['title'];b=design['bounds'];g['space']['bounds']=copy.deepcopy(b)
    g['foundation'].update(widthBlocks=b['w']//128,heightBlocks=b['h']//128)
    ports=[]
    for p in design['ports']:
        q=copy.deepcopy(next((v for v in g['ports']if v['id']==p['id']),g['ports'][0]));q.update(copy.deepcopy(p));q['permission']={'IN':'INPUT','OUT':'OUTPUT'}.get(q['permission'],q['permission'])
        q['stagingPosition']=dock(p);q['objectId']=doc['id']+'/port-'+p['id']
        q['seamIds']=[p['id']+'-seam'];q['connection']=dict(status='declared',region=dict(x=p['position'][0]-32,y=p['position'][1]-32,w=64,h=64))
        q['permissionStatus']='declared_pending_approved_validation'
        if q['permission']!='INOUT':q['initialPermissionConditions']=dict(availableAbilitiesExact=source[0]['capabilities'],requiresRevalidationWithAdditionalUpwardAbilities=True)
        support=next((o for o in static if o['x']<=q['stagingPosition'][0]<=o['x']+o['w']and o['y']==q['stagingPosition'][1]+18),None)
        q['support']=dict(objectId=support['id'],face='top',status='source_derived')if support else 'UNKNOWN'
        if p['surface']=='AIR':q['support']='UNKNOWN'
        ports.append(q);objects.append(dict(id=q['objectId'],type='entry'if p['id']=='A'else'exit',x=p['position'][0]-12,y=p['position'][1]-18,w=24,h=36,rotation=0))
    g['ports']=ports;g['space']['occupancy']['objectIds']=[o['id']for o in objects if o['type']not in('entry','exit','route','note','anchor')];g['space']['occupancy']['regions']=[]
    g['space']['dynamicEnvelopes']=[dict(objectId=o['id'],region='UNKNOWN',status='UNKNOWN')for o in objects if o['type']in('gate','enemy','gear')or o.get('trackId')];g['space']['actionClearance'].update(status='UNKNOWN',regions=[])
    g['space']['seams']=[dict(id=p['id']+'-seam',portId=p['id'],allowedOverlap=[],region=p['connection']['region'],status='UNKNOWN')for p in ports]
    content=decode(doc);routes=[];cases=[]
    for design_target in design['intendedRoutes']:
        target=copy.deepcopy(design_target)
        target['role']={'ingress':'main','air_exit':'main'}.get(target['role'],target['role'])
        route=copy.deepcopy(g['routes'][0]);route.update({k:target[k]for k in ('id','from','to','role','pathObjectId')})
        route.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',durationSeconds='UNKNOWN',validationIds=[],resourceProfile=dict(status='UNKNOWN'),initialConditions=dict(status='UNKNOWN'))
        for key in ('transfer','return','onward'):route[key]['status']='UNKNOWN'
        a,z=[next(p for p in ports if p['id']==target[k])for k in ('from','to')]
        route['localDisplacementBlocks']=[(z['position'][i]-a['position'][i])/128 for i in (0,1)];routes.append(route)
        plan,match=plan_for(n,target,source,design);c=copy.deepcopy(match);c.update(copy.deepcopy(content))
        c.update(id='approved-first30-'+n+'-'+target['id'],control_plan=plan,spawn=a['stagingPosition'][:],entry_port=a['stagingPosition'][:],exit_port=z['stagingPosition'][:],
            goal=[z['stagingPosition'][0]-7,z['stagingPosition'][1]-4,14,8],max_frames=2400)
        c['ports']=[dict(id=p['id'],position=p['stagingPosition'],normal=p['normal'],**(dict(support_index=next(o['sourceIndex']for o in static if o['id']==p['support']['objectId']))if isinstance(p['support'],dict)and p['support'].get('objectId')else{}))for p in ports]
        c['route_spec']=dict(id=target['id'],from_port=target['from'],to_port=target['to'],role=target['role'],via_ports=[],require_bell=n in('12','28')and target['from']in('A','D'))
        c['required_rewards']=[v['id']for v in content['reward_sites']]if (n not in('12','23','27') or (n=='12'and target['to']in('B','C'))or(n=='23'and target['to']=='B')or(n=='27'and target['to']=='B'))else[]
        if n=='12':c['required_rewards']=[v['id']for v in content['reward_sites']if abs(v['position'][0]-z['stagingPosition'][0])<60]
        c['expected_reward']=sum(v['amount']for v in content['reward_sites']if v['id']in c['required_rewards'])
        c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[b['x']%128,b['y']%128],cells=[[x,y]for x in range(b['x']//128,(b['x']+b['w'])//128)for y in range(b['y']//128,(b['y']+b['h'])//128)])
        c['approved_first30']=dict(reviewId=n,designVersion=row['designVersion'],rectangle=b,originalAuthor=match['generation_rule']['registration_source'])
        c['generation_rule']['registration_source']=AUTHOR
        c['world_bounds']=[b['x']-256,b['y']-384,b['w']+512,b['h']+768]
        for field in ('migration_adaptation','migration_compat','block_ports','required_carrier_park','recorded_frames','noise','module_sha256','factory_evidence','factory_id'):c.pop(field,None)
        cases.append(c)
    g['routes']=routes
    g['relations']=[{'from':a['id'],'to':z['id'],'status':'UNKNOWN','conditions':'UNKNOWN','routeIds':[r['id']for r in routes if r['from']==a['id']and r['to']==z['id']]}for a in ports for z in ports]
    g['validations']=[];g['unlocks']=[];g['closures']=[];g['mirror'].update(status='UNKNOWN',validationIds=[]);g['portConfigurations']=[]
    g['composition']['cells']=[dict(id=o['id'],objectIds=[o['id']],contentVersion='sha256:'+'0'*64)for o in objects if o['type']not in('entry','exit','route','note','anchor')]
    for p in ports:p['routeRoles']=[r['id']+':'+('entry'if r['from']==p['id']else'exit')for r in routes if p['id']in(r['from'],r['to'])]
    g['generation']['approvedImplementation']=dict(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],controlProgramsSha256=digest([c['control_plan']for c in cases]),productionApproval=False)
    corners.annotate(doc);core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.contract(out/'module.mapnote.json',refresh=True)
    core.write(out/'migration.json',dict(moduleId=row['moduleId'],sourcePath=row['sourceModule']['file'],sourceVersion=row['sourceModule']['contentVersion'],status='prepared_unverified',designVersion=row['designVersion'],humanReview='design_keep',productionAdmitted=False,evidence=[],unresolved=['actual approved-design validation']))
    core.write(out/'parameters.json',dict(designVersion=row['designVersion'],content=content,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases],quality='original regular',productionApproval=False))
    print(n,'prepared',len(cases),'routes',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');a=p.parse_args()
    for r in core.read(AUTH/'handoff.json')['rows']:
        if int(r['reviewId'])>5 and (not a.ids or r['reviewId']in a.ids):prepare(r)
