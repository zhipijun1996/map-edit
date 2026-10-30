"""Reuse frozen candidates, applying only the user's explicit geometry/Port changes."""
import copy
from pathlib import Path
from pcg.migration import core,physics,godot_package,corners
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label,AUTH
from .prepare_review045_v1 import at,end,axis,decode as forest_decode
from .lift_idea_v1 import decode as lift_decode

def base_folder(row):
    n=label(row)
    if n=='196':return core.REPO/Path(row['sourceModule']['file']).parent
    parent='new-ideas-final-v1' if n=='three' else 'lift-idea-final-v1' if n=='lift' else 'review-045-final-v1'
    return core.REPO/'pcg/manual_review/implementation'/parent/row['moduleId']
def decode(doc):
    return lift_decode(doc) if any(o.get('designMotion')for o in doc['objects'])or doc['id'].startswith('idea-') else forest_decode(doc)
def stand(port,design):
    x,y=port['position'];nx,ny=port['normal']
    if nx:return[x-24*nx,y+14]
    support=next((o for o in design['visualObjects']if o['id']==port.get('supportObjectId')),None)
    if support is None:support=min([o for o in design['visualObjects']if o['type']in['platform','terrain']and not o.get('trackId')and o['x']<=x<=o['x']+o['w']],key=lambda o:abs(o['y']-y))
    return[x,support['y']-18]
def climb(y):return dict(op='wait',climb_target=y,trigger=dict(after=1,state='climb_y',timeout=900))
def plan196(a,z):
    if a=='entry':prefix=[cmd('drop_through',1)]+at(110,0)
    elif a=='exit':prefix=[axis(1),climb(320),dict(op='settle',target_x=183,deadband=.6,trigger=dict(after=0)),climb(80)]+at(110,0)
    else:prefix=[axis(1),climb(80)]+at(110,0)
    if z=='entry':return prefix+[axis(1),cmd('jump'),climb(-240)]+end(110,-288)
    if z=='bottom':return prefix+[axis(1),dict(op='wait',height_threshold=710,trigger=dict(after=1,state='descending_height',timeout=1000))]+end(110,768)
    return prefix+[axis(1),dict(op='wait',wall_window=[330,430],trigger=dict(after=1,state='wall_launch',timeout=900)),cmd('jump'),axis(-1),cmd('jump_release',8)]+end(-58,384)
def prepare(row):
    n=label(row);base=base_folder(row);f=core.REPO/row['outputDirectory'];assert not f.exists()
    design=core.read(row['designFile']);doc=core.read(base/'module.mapnote.json');original_cases=core.read(base/'cases.json')['cases'];g=doc['generationContract'];old_objects={o['id']:o for o in doc['objects']}
    objects=[]
    for v in design['visualObjects']:
        old=copy.deepcopy(old_objects.get(v['id'],{}));old.update(copy.deepcopy(v))
        if old['type']=='route':old.setdefault('duration',1);old.setdefault('mode','once');old.pop('trajectory',None)
        if old['type']=='enemy':
            cx=old['x']+old['w']/2;cy=old['y']+old['h']/2;bottom=old['y']+old['h'];old.update(x=cx-14,y=cy-16 if old['definition']=='plains_diver'else bottom-32,w=28,h=32)
        objects.append(old)
    for o in objects:
        if o['type']=='reward' and o.get('mechanics',{}).get('source'):
            s=o['mechanics']['source'];center=[o['x']+o['w']/2,o['y']+o['h']/2];delta=[center[i]-s['position'][i]for i in range(2)];s['position']=center
            if 'region'in s:s['region']=[s['region'][0]+delta[0],s['region'][1]+delta[1],*s['region'][2:]]
    static=[o for o in objects if o['type']in ['terrain','platform']and not o.get('trackId')]
    for i,o in enumerate(static):o['sourceIndex']=i
    ports=[]
    for p in design['ports']:
        q=copy.deepcopy(next((v for v in g['ports']if v['id']==p['id']),g['ports'][0]));q.update(copy.deepcopy(p));q['permission']={'IN':'INPUT','OUT':'OUTPUT'}.get(q['permission'],q['permission']);q['stagingPosition']=stand(p,design);q['objectId']=doc['id']+'/port-'+p['id'];q.pop('grid',None)
        support=next(o for o in static if o['x']<=q['stagingPosition'][0]<=o['x']+o['w']and abs(o['y']-q['stagingPosition'][1]-18)<.001)
        q['support']=dict(objectId=support['id'],face='top',status='source_derived');q['supportObjectId']=support['id'];q['connection']=dict(status='declared',region=dict(x=p['position'][0]-32,y=p['position'][1]-32,w=64,h=64));q['permissionStatus']='declared_pending_revision_validation';q['initialPermissionConditions']=dict(availableAbilitiesExact=original_cases[0]['capabilities'],requiresRevalidationWithAdditionalUpwardAbilities=True);q['seamIds']=[p['id']+'-seam'];ports.append(q)
        objects.append(dict(id=q['objectId'],type='entry'if p['id']=='entry'else'exit',x=p['position'][0]-12,y=p['position'][1]-18,w=24,h=36,rotation=0))
    doc['objects']=objects;requirements=copy.deepcopy(design.get('capabilityRequirements',doc['capabilityRequirements']));requirements.update(version=1,status='defined',anyOfGroups=requirements.get('anyOfGroups',[]),note=requirements.get('note','Explicit abilities for the revised approved interface.'));doc['capabilityRequirements']=requirements;b=design['bounds'];g['space']['bounds']=copy.deepcopy(b);g['foundation'].update(widthBlocks=b['w']//128,heightBlocks=b['h']//128);g['ports']=ports
    doc['canvas'].update(width=b['w'],height=b['h']);content=decode(doc);cases=[];routes=[]
    for target in design['intendedRoutes']:
        target=copy.deepcopy(target)
        if target['role']not in ['main','reward','return','recovery','shortcut']:target['role']='return'if 'return'in target['role']else'main'
        a,z=target['from'],target['to'];route=copy.deepcopy(next((r for r in g['routes']if r['id']==target['id']),g['routes'][0]));route.update({k:target[k]for k in ['id','from','to','role','pathObjectId']});route.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',validationIds=[]);route['transfer']['status']='UNKNOWN';route['return']['status']='UNKNOWN';route['onward']['status']='UNKNOWN';route['capabilityRequirements']=requirements;route['localDisplacementBlocks']=[(next(p for p in ports if p['id']==z)['position'][i]-next(p for p in ports if p['id']==a)['position'][i])/128 for i in [0,1]];routes.append(route)
        if n=='196':c=dict(family='wall-slide-launch-window',capabilities=['move','jump','wall_climb'],generation_rule=dict(registration_source='pcg/manual_review/revision053_author_v1.py'),control_plan=plan196(a,z),required_rewards=[],expected_reward=0)
        else:c=copy.deepcopy(next(c for c in original_cases if c['route_spec']['id']==target['id']))
        c.update(copy.deepcopy(content));p=next(p for p in ports if p['id']==a);q=next(p for p in ports if p['id']==z)
        c.update(id='approved-r053-v1-'+n+'-'+target['id'],spawn=p['stagingPosition'][:],entry_port=p['stagingPosition'][:],exit_port=q['stagingPosition'][:],goal=[q['stagingPosition'][0]-7,q['stagingPosition'][1]-4,14,8],max_frames=3000,trace_all=False,route_spec=dict(id=target['id'],from_port=a,to_port=z,role=target['role'],via_ports=[],require_bell=n in ['three','lift']and z=='B'),world_bounds=[b['x']-256,b['y']-384,b['w']+512,b['h']+768])
        c['approved_implementation']=dict(reviewId=row['reviewId'],designVersion=row['designVersion'],rectangle=b,originalAuthor=original_cases[0]['generation_rule']['registration_source']);c['legal_port_mouths']=[{k:p[k]for k in ['id','position','face','surface','permission']}for p in ports]
        c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[b['x']%128,b['y']%128],cells=[[x,y]for x in range(b['x']//128,(b['x']+b['w'])//128)for y in range(b['y']//128,(b['y']+b['h'])//128)])
        c['ports']=[dict(id=p['id'],position=p['stagingPosition'],normal=p['normal'],support_index=next(o['sourceIndex']for o in static if o['id']==p['supportObjectId']))for p in ports]
        for k in list(c):
            if k.startswith('migration_')or k in ['recorded_frames','factory_evidence','module_sha256','noise','block_ports','actual_capabilities']:c.pop(k,None)
        c['generation_rule']['registration_source']='pcg/manual_review/revision053_forest_author_v1.py'if n in ['42','50','51','52'] else 'pcg/manual_review/revision053_lift_author_v1.py'if n=='lift' else 'pcg/manual_review/revision053_three_author_v1.py'if n=='three' else 'pcg/manual_review/revision053_author_v1.py'
        if n in ['51','52']:
            for v in c['control_plan']:
                if v.get('trigger',{}).get('migration_goal') and v['trigger']['migration_goal'][1] in [-321,-297]:
                    y=v['trigger']['migration_goal'][1]
                    if v.get('target_x')not in [-360,488]:pass
                    # Interior floor was lowered64; side docking points stay exact.
                    goal=v['trigger']['migration_goal']
                    if -220<=goal[0]+goal[2]/2<=330:goal[1]+=64
        if n in ['three','lift']and z=='B':
            x=q['position'][0];pplan=c['control_plan'];i=max(i for i,v in enumerate(pplan)if v['op']=='settle');pplan=pplan[:i]+end(x,46)
            pplan +=[dict(op='shoot',aim_cell=dict(kind='bell',id='top-exit-bell'),direction=[0,-1],trigger=dict(after=4,state='grounded_shot_ready',timeout=300)),dict(op='wait',trigger=dict(after=12,state='grounded',timeout=240)),cmd('jump'),cmd('jump_release',24)]+end(x,-50)
            c['control_plan']=pplan;neighbor=[x-48,-32,96,12];idx=len(c['platforms']);c['platforms'].append(neighbor);c['one_way_platform_indices'].append(idx);c['explicit_exit_neighbor']=dict(portId='B',floor=neighbor,index=idx,source='explicit compatible adjacent Module fixture; not owned content',copiedIntoModule=False);c['goal']=[x-7,-54,14,8]
        if n in ['42','50','51','52']:
            count=0
            for v in c['control_plan']:
                if v['op']=='grapple':
                    count+=1
                    if n=='50' and v.get('aim_target')==[188,-40]:v['aim_target']=[200,-40]
                elif v.get('trigger',{}).get('state')=='free' and count:
                    v['hook_count']=count;v['trigger'].update(state='hook_done',after=1)
        cases.append(c)
    g['routes']=routes;g['relations']=[dict(**{'from':p['id'],'to':q['id']},status='UNKNOWN',conditions='initial permission '+p['permission']+'/'+q['permission'],routeIds=[r['id']for r in routes if r['from']==p['id']and r['to']==q['id']])for p in ports for q in ports]
    g['space']['occupancy']['regions']=[];g['space']['dynamicEnvelopes']=[dict(objectId=o['id'],region='UNKNOWN',status='UNKNOWN')for o in objects if o['type']in ['gate','enemy','gear']or o.get('trackId')];g['composition']['cells']=[dict(id=o['id'],objectIds=[o['id']],contentVersion='sha256:'+'0'*64)for o in objects if o['type']not in ['entry','exit','route','note','anchor']];g['validations']=[];g['unlocks']=[];g['mirror'].update(status='UNKNOWN',validationIds=[]);g['closures']=[];g['portConfigurations']=[];g['space']['seams']=[dict(id=p['id']+'-seam',portId=p['id'],allowedOverlap=[],region=p['connection']['region'],status='UNKNOWN')for p in ports]
    g['space']['occupancy']['objectIds']=[o['id']for o in objects if o['type']not in ['entry','exit','route','note','anchor']]
    g['generation']['approvedImplementation']=dict(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],controlProgramsSha256='pending',productionApproval=False)
    
    for transform in g['space']['transforms']:transform.update(status='UNKNOWN',validationIds=[])
    doc=godot_package.bind_case_behavior(doc,cases);corners.annotate(doc);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cases));core.write(f/'migration.json',dict(moduleId=row['moduleId'],sourcePath=core.relative(base/'module.mapnote.json'),status='prepared_unverified',designVersion=row['designVersion']));core.write(f/'parameters.json',dict(content=decode(doc),authorization=core.relative(AUTH/'request.json')));print(n,'PREPARED',len(cases),flush=True)
if __name__=='__main__':
    import sys
    for row in rows():
        if not sys.argv[1:]or label(row)in sys.argv[1:]:prepare(row)
