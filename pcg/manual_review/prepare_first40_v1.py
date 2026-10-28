"""Materialize exact approved drawings through the existing Module data format."""
import argparse
import copy
from pcg.migration import core,corners,physics
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from .first30_content_v2 import decode

AUTH=core.REPO/'feedback/manual-review/implementation-results/first-40-v1/authorization'
AUTHOR='pcg/manual_review/first30_author_v2.py'


def dock(p):
    x,y=p['position'];nx,ny=p['normal']
    return [x-24*nx,y+14]if nx else[x,y-24*ny]


def hop(x,dy=.7,hold=20):
    return [settle(x),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-(1-dy*dy)**.5,dy]),ground(),cmd('wait',12)]


def plan_for(n,target,source,design):
    match=source[0];p=copy.deepcopy(match['control_plan']);ports={p['id']:dock(p)for p in design['ports']}
    if n=='32':p[1]['trigger']['dynamic']['value']=210
    elif n=='34':p=[settle(ports[target['to']][0]),ground(),cmd('wait',20)]
    elif n=='35':
        p=p[:42]+[settle(920),wait_x(914),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',8),settle(1000),ground(),cmd('wait',20)]
    elif n=='36':
        p=p[:4]+[cmd('jump_release',4),cmd('shoot',2,direction=[-1,0]),cmd('shoot',17,direction=[-1,0]),settle(872),ground(),cmd('wait',20)]
    elif n=='37':
        p=p[:24]
        p[-1]['trigger']['migration_goal']=[935,498,10,8]
        p += [settle(1000),ground(),cmd('wait',20)]
    elif n=='39':
        p=p[:10];p[0]['target_x']=24;p[1]['trigger']['migration_goal']=[19,-4,10,8]
        p += [settle(488),ground(),cmd('wait',20)]
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
        if o['type']=='hazard'and o.get('sourceType')in('spike','wallSpike','gear'):o['type']=o['sourceType']
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
        c['route_spec']=dict(id=target['id'],from_port=target['from'],to_port=target['to'],role={'ingress':'main'}.get(target['role'],target['role']),via_ports=[],require_bell=n in('12','28')and target['from']in('A','D'))
        c['required_rewards']=[v['id']for v in content['reward_sites']]if (n not in('12','23','27') or (n=='12'and target['to']in('B','C'))or(n=='23'and target['to']=='B')or(n=='27'and target['to']=='B'))else[]
        if n=='12':c['required_rewards']=[v['id']for v in content['reward_sites']if abs(v['position'][0]-z['stagingPosition'][0])<60]
        c['expected_reward']=sum(v['amount']for v in content['reward_sites']if v['id']in c['required_rewards'])
        c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[b['x']%128,b['y']%128],cells=[[x,y]for x in range(b['x']//128,(b['x']+b['w'])//128)for y in range(b['y']//128,(b['y']+b['h'])//128)])
        c['approved_implementation']=dict(reviewId=n,designVersion=row['designVersion'],rectangle=b,originalAuthor=match['generation_rule']['registration_source'])
        c['generation_rule']['registration_source']='pcg/manual_review/first40_r'+n+'_v1.py'
        air=[{k:p[k]for k in ('id','position','stagingPosition','face','surface','permission')}for p in ports if p['surface']=='AIR']
        if air:c['air_port_contracts']=air
        if n in('32','34','35'):c['approved_first30']=copy.deepcopy(c['approved_implementation'])
        c['world_bounds']=[b['x']-256,b['y']-384,b['w']+512,b['h']+768]
        for field in ('migration_adaptation','migration_compat','block_ports','required_carrier_park','recorded_frames','noise','module_sha256','factory_evidence','factory_id'):c.pop(field,None)
        cases.append(c)
    g['routes']=routes
    g['relations']=[{'from':a['id'],'to':z['id'],'status':'UNKNOWN','conditions':'UNKNOWN','routeIds':[r['id']for r in routes if r['from']==a['id']and r['to']==z['id']]}for a in ports for z in ports]
    g['validations']=[];g['unlocks']=[];g['closures']=[];g['mirror'].update(status='UNKNOWN',validationIds=[]);g['portConfigurations']=[]
    g['composition']['cells']=[dict(id=o['id'],objectIds=[o['id']],contentVersion='sha256:'+'0'*64)for o in objects if o['type']not in('entry','exit','route','note','anchor')]
    for p in ports:p['routeRoles']=[r['id']+':'+('entry'if r['from']==p['id']else'exit')for r in routes if p['id']in(r['from'],r['to'])]
    g['generation']['approvedImplementation']=dict(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],controlProgramsSha256=digest([c['control_plan']for c in cases]),productionApproval=False)
    doc.pop('unused',None);g.pop('internalWaypoints',None)
    from pcg.migration import godot_package
    doc=godot_package.bind_case_behavior(doc,cases)
    corners.annotate(doc);core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.contract(out/'module.mapnote.json',refresh=True)
    core.write(out/'migration.json',dict(moduleId=row['moduleId'],sourcePath=row['sourceModule']['file'],sourceVersion=row['sourceModule']['contentVersion'],status='prepared_unverified',designVersion=row['designVersion'],humanReview='design_keep',productionAdmitted=False,evidence=[],unresolved=['actual approved-design validation']))
    core.write(out/'parameters.json',dict(designVersion=row['designVersion'],content=content,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases],quality='original regular',productionApproval=False))
    print(n,'prepared',len(cases),'routes',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');a=p.parse_args()
    for r in core.read(AUTH/'handoff.json')['rows']:
        if 30<int(r['reviewId'])<=40 and (not a.ids or r['reviewId']in a.ids):prepare(r)
