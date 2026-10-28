"""Implement only the hash-pinned five-design handoff, using existing consumers.

Prepare is deterministic and refuses to replace candidates. Experiments never
edit design files, the review queue, formal modules or human decisions.
"""
import argparse
import copy
import json
from pathlib import Path
from pcg.migration import core, corners, godot_package, physics
from pcg.prototype.workshop.rules import cmd, wait_x, ground, settle
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port

ROOT = core.REPO
QUEUE = ROOT/'feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json'
AUTHOR = 'pcg/manual_review/approved_author_v1.py'


def source_folder(row):
    revision = 'revision-003' if row['reviewId'] == '03' else 'revision-002'
    return ROOT/'pcg/manual_review/batch-001'/revision/row['moduleId']


def verify_handoff():
    queue = core.read(QUEUE)
    decisions = core.read(ROOT/'feedback/manual-review/implementation-results/batch-001/authorization/decisions-v1.json')['rows']
    assert [r['reviewId'] for r in queue['rows']] == ['01','02','03','04','05']
    for row in queue['rows']:
        assert core.sha(ROOT/row['designFile']) == row['designFileSha256']
        assert core.read(ROOT/row['designFile'])['designVersion'] == row['designVersion']
        assert core.sha(ROOT/row['sourceModule']['file']) == row['sourceModule']['sha256']
        assert core.read(ROOT/row['sourceModule']['file'])['generationContract']['contentVersion'] == row['sourceModule']['contentVersion']
        assert any(d['reviewId']==row['reviewId'] and d['version']==row['designVersion'] and d['decision']=='KEEP' for d in decisions)
        assert core.sha(source_folder(row)/'module.mapnote.json') == row['sourceModule']['sha256']
    return queue


def mirror_plan(plan, width):
    result = copy.deepcopy(plan)
    for command in result:
        if command['op']=='axis':command['value'] *= -1
        if 'target_x' in command:command['target_x'] = width-command['target_x']
        if 'direction' in command:command['direction'][0] *= -1
        dynamic = command.get('trigger', {}).get('dynamic', {})
        if dynamic.get('kind')=='actor_x':
            dynamic['value'] = width-dynamic['value']
            dynamic['direction'] = {'gte':'lte','lte':'gte'}[dynamic['direction']]
        if command.get('aim_cell', {}).get('id') in ('left-way','right-way'):
            command['aim_cell']['id'] = {'left-way':'right-way','right-way':'left-way'}[command['aim_cell']['id']]
    return result


def case_for(cases, route):
    match = next((c for c in cases if c['route_spec']['id']==route['id']), None)
    if match:return copy.deepcopy(match)
    if route['id'] in ('D-to-B','D-to-C') and len(cases)==2:
        base = copy.deepcopy(cases[0 if route['to']=='C' else 1])
        base['control_plan'] = mirror_plan(base['control_plan'],1024)
        base['rule_parameters'] = copy.deepcopy(cases[1 if route['to']=='C' else 0]['rule_parameters'])
        return base
    # N06: exact same geometry, new independent programs for all eight pairs.
    target = route['to']; entry = route['from']
    base = copy.deepcopy(next(c for c in cases if c['route_spec']['to_port']==(target if target in ('B','C') else 'B')))
    if entry in ('B','C'):
        # Explicitly reach M before starting its departure; axis commands do
        # not cancel the Harness's persistent settle controller.
        prefix = [cmd('axis',value=1),wait_x(640),cmd('axis',value=0),ground(),cmd('wait',8)]
        if entry=='C':
            prefix = [cmd('axis',value=-1),wait_x(1088,-1),cmd('axis',value=0),ground(),cmd('wait',8),
                      cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),wait_x(640,-1),cmd('axis',value=0),ground(),cmd('wait',8)]
    else:
        prefix = copy.deepcopy(next(c for c in cases if c['route_spec']['from_port']==entry)['control_plan'][:9])
    if target in ('A','D'):
        side = -1 if target=='A' else 1
        end = 24 if side<0 else 1256
        # A real jump off M; original recoil, collision and resource renewal.
        suffix = [settle(540 if side<0 else 740),wait_x(546 if side<0 else 734,side),ground(),cmd('wait',8),
                  settle(end),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-side*.75,.6614378277661477]),
                  wait_x(end-side*6,side),ground(),cmd('wait',20)]
    else:
        suffix = copy.deepcopy(next(c for c in cases if c['route_spec']['id']=='A-to-'+target)['control_plan'][9:])
    base['control_plan'] = prefix+suffix
    return base


def prepare():
    queue = verify_handoff()
    for row in queue['rows']:
        out = ROOT/row['outputDirectory']
        if out.exists():raise ValueError('immutable_candidate_exists:'+str(out))
    for row in queue['rows']:
        design = core.read(ROOT/row['designFile'])
        doc = core.read(ROOT/row['sourceModule']['file'])
        cases = core.read(source_folder(row)/'cases.json')['cases']
        g = doc['generationContract']; bounds = design['bounds']
        previous = {o['id']:o for o in doc['objects']}
        objects = []
        for visual in design['visualObjects']:
            obj = copy.deepcopy(previous.get(visual['id'], {}))
            for key,value in visual.items():
                if key=='mechanics':obj.setdefault(key,{}).update(copy.deepcopy(value))
                else:obj[key]=copy.deepcopy(value)
            if obj['type']=='enemy':
                obj.setdefault('sourceId',obj['id'].split('/')[-1])
                obj.setdefault('mechanics',{}).setdefault('initialIdleCooldown',0.)
            if obj['type']=='route':
                obj.setdefault('duration',1.)
                obj.setdefault('mode','once')
                obj['note']='Approved design intent only; not an observed trajectory or physics evidence.'
                obj.pop('trajectory',None)
            objects.append(obj)
        platforms=[o for o in objects if o['type'] in ('terrain','platform')]
        for index,o in enumerate(platforms):o['sourceIndex']=index
        ports=[]
        for p in design['ports']:
            old=next((q for q in g['ports'] if q['id']==p['id']),g['ports'][0])
            pfull=copy.deepcopy(old);pfull.update(copy.deepcopy(p))
            pfull['objectId']=doc['id']+'/port-'+p['id']
            pfull['stagingPosition']=[p['position'][0]-24*p['normal'][0],p['position'][1]+14]
            support=next(o for o in platforms if o['x']<=pfull['stagingPosition'][0]<=o['x']+o['w'] and o['y']==p['position'][1]+32)
            pfull['support']=dict(objectId=support['id'],face='top',status='source_derived')
            pfull['connection']=dict(status='declared',region=dict(x=p['position'][0]-32,y=p['position'][1]-32,w=64,h=64))
            pfull['permissionStatus']='declared_pending_approved_design_validation'
            pfull['seamIds']=[p['id']+'-seam']
            ports.append(pfull)
            objects.append(dict(id=pfull['objectId'],type='entry' if p['id']=='A' else 'exit',x=p['position'][0]-12,y=p['position'][1]-18,w=24,h=36,rotation=0,label=p['id']))
        doc['objects']=objects;doc['title']=design['title'];g['ports']=ports
        g['space']['bounds']=copy.deepcopy(bounds)
        g['foundation'].update(widthBlocks=bounds['w']//128,heightBlocks=bounds['h']//128)
        byid={o['id']:o for o in objects}
        g['space']['occupancy']['objectIds']=[o['id'] for o in objects if o['type'] not in ('entry','exit','route','note','anchor')]
        g['space']['occupancy']['regions']=[]
        g['space']['actionClearance'].update(status='UNKNOWN',regions=[])
        g['space']['dynamicEnvelopes']=[v for v in g['space']['dynamicEnvelopes'] if v['objectId'] in byid]
        for obj in objects:
            if obj['type']=='enemy' and not any(v['objectId']==obj['id'] for v in g['space']['dynamicEnvelopes']):
                g['space']['dynamicEnvelopes'].append(dict(objectId=obj['id'],region='UNKNOWN',status='UNKNOWN'))
        g['space']['seams']=[dict(id=p['id']+'-seam',portId=p['id'],allowedOverlap=[],region=p['connection']['region'],status='UNKNOWN') for p in ports]
        routes=[]; output_cases=[]
        for target in design['intendedRoutes']:
            route=copy.deepcopy(next((r for r in g['routes'] if r['id']==target['id']),g['routes'][0]))
            route.update({k:target[k] for k in ('id','from','to','pathObjectId','role')})
            route.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',durationSeconds='UNKNOWN',resourceProfile=dict(status='UNKNOWN'),initialConditions=dict(status='UNKNOWN'),validationIds=[])
            for key in ('transfer','return','onward'):route[key]['status']='UNKNOWN'
            route['localDisplacementBlocks']=[(next(p for p in ports if p['id']==route['to'])['position'][i]-next(p for p in ports if p['id']==route['from'])['position'][i])/128 for i in (0,1)]
            routes.append(route)
            c=case_for(cases,target)
            original=c['generation_rule']['registration_source']
            c['approved_implementation']=dict(reviewId=row['reviewId'],designVersion=row['designVersion'],originalAuthor=original,rectangle=copy.deepcopy(bounds))
            c['generation_rule']['registration_source']='pcg/manual_review/approved_r'+row['reviewId']+'_v1.py'
            c.update(copy.deepcopy(godot_package.content_from_objects(doc)))
            c['ports']=[dict(id=p['id'],position=p['stagingPosition'],normal=p['normal'],support_index=byid[p['support']['objectId']]['sourceIndex']) for p in ports]
            c['block_ports']={}
            for p in ports:
                cell=[int(p['position'][0]//128)-(1 if p['face']=='RIGHT' else 0),int(p['position'][1]//128)]
                c['block_ports'][p['id']]=dict(block_port(p['id'],cell,'W' if p['face']=='LEFT' else 'E',p['stagingPosition']),face=p['face'],surface=p['surface'],permission=p['permission'])
            a=next(p for p in ports if p['id']==target['from']); z=next(p for p in ports if p['id']==target['to'])
            c['spawn']=a['stagingPosition'][:];c['entry_port']=c['spawn'][:];c['exit_port']=z['stagingPosition'][:]
            c['goal']=[c['exit_port'][0]-7,c['exit_port'][1]-4,14,8]
            c['route_spec'].update(id=target['id'],from_port=target['from'],to_port=target['to'],role=target['role'])
            if row['reviewId']=='01' and target['to'] in ('A','D'):c['route_spec']['require_bell']=False
            if row['reviewId']=='02':
                for command in c['control_plan']:
                    if command.get('target_x')==24:command['target_x']=152
                    dynamic=command.get('trigger',{}).get('dynamic',{})
                    if dynamic.get('kind')=='actor_x' and dynamic.get('value')==30:dynamic['value']=158
            if row['reviewId']=='03':
                for command in c['control_plan']:
                    if 'target_x' in command:command['target_x']=c['exit_port'][0]
            c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[0,0],cells=[[x,y] for x in range(bounds['x']//128,(bounds['x']+bounds['w'])//128) for y in range(bounds['y']//128,(bounds['y']+bounds['h'])//128)])
            for field in ('migration_adaptation','migration_compat'):
                if field in c:c[field]['rectangle' if field=='migration_adaptation' else 'foundationRectangle']=copy.deepcopy(bounds)
            c['world_bounds']=[bounds['x']-256,bounds['y']-384,bounds['w']+512,bounds['h']+768]
            for key in ('recorded_frames','noise','module_sha256','factory_evidence','factory_id'):c.pop(key,None)
            c['id']='approved-b001-'+row['reviewId']+'-'+target['id']+'-v1'
            output_cases.append(c)
        g['routes']=routes
        g['relations']=[{'from':a['id'],'to':b['id'],'status':'UNKNOWN','conditions':'UNKNOWN',
                        'routeIds':[r['id'] for r in routes if r['from']==a['id'] and r['to']==b['id']]}
                       for a in ports for b in ports]
        g['validations']=[];g['staticChecks']['result']='UNKNOWN'
        g['closures']=[];g['mirror'].update(status='UNKNOWN',validationIds=[]);g['portConfigurations']=[]
        g['composition']['cells']=[dict(id=o['id'],objectIds=[o['id']],contentVersion='sha256:'+'0'*64) for o in objects if o['type'] not in ('entry','exit','route','note','anchor')]
        for p in ports:p['routeRoles']=[r['id']+':'+('entry' if r['from']==p['id'] else 'exit') for r in routes if p['id'] in (r['from'],r['to'])]
        g['generation']['approvedImplementation']=dict(queue=core.relative(QUEUE),queueSha256=core.sha(QUEUE),**copy.deepcopy(row),controlProgramsSha256=digest([c['control_plan'] for c in output_cases]),productionApproval=False)
        corners.annotate(doc)
        out=ROOT/row['outputDirectory'];core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=output_cases))
        core.contract(out/'module.mapnote.json',refresh=True)
        core.write(out/'migration.json',dict(sourcePath=row['sourceModule']['file'],sourceVersion=row['sourceModule']['contentVersion'],designVersion=row['designVersion'],productionApproval=False))
        print(json.dumps(dict(reviewId=row['reviewId'],output=core.relative(out)),ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','verify']);args=parser.parse_args()
    if args.action=='prepare':prepare()
    else:verify_handoff();print('All five exact design/source/KEEP bindings verified')
