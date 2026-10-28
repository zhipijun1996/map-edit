"""Apply this user's five explicit edits to isolated versioned review candidates.

No admission, generator, map, or physics replacement. Reuses the existing contract compiler.
"""
from pathlib import Path
import copy,json,hashlib,subprocess
from pcg.migration import core,corners,godot_package,physics
ROOT=core.REPO
OUT=ROOT/'pcg/manual_review/batch-001/revision-001'
NOTES=[
('CHANGE','最底下的平台冗余，删除下方3行block。中间平台上方增加一个空中怪物'),
('CHANGE','下方的5个平台冗余，删除下面5行block。最高那个平台上面放一个怪物'),
('CHANGE','整个模块可以变短，左侧平台保留1block长，中间跳跃4block，右侧1block共6block。高度删除最下方2行block，最下面平台冗余。上面宝箱过于简单，路径上增加1空中1陆上怪物。'),
('KEEP','最下方平台冗余删掉，最下方2行和最上方1行block可以取消'),
('CHANGE','删除下方3行，左边2列block')]
BOUNDS=[dict(x=0,y=0,w=1280,h=768),dict(x=0,y=0,w=1536,h=768),dict(x=-256,y=128,w=768,h=512),dict(x=0,y=128,w=1024,h=640),dict(x=256,y=0,w=768,h=640)]

def enemy(doc,ident,definition,x,y):
 return dict(id=doc['id']+'/'+ident,type='enemy',sourceId=ident,definition=definition,x=x-14,y=y-16,w=28,h=32,rotation=0,label='空中俯冲怪'if definition=='plains_diver'else'陆上哨兵',mechanics=dict(initialIdleCooldown=0.0))

def clip(o,b):
 x=max(o['x'],b['x']);y=max(o['y'],b['y']);z=min(o['x']+o['w'],b['x']+b['w']);v=min(o['y']+o['h'],b['y']+b['h'])
 if z<=x or v<=y:return None
 return dict(o,x=x,y=y,w=z-x,h=v-y)

def prepare():
 if OUT.exists():raise ValueError('immutable_revision_already_exists')
 source=core.read(ROOT/'generation/manual-review/batch-001/batch.json');receipt=[]
 for i,row in enumerate(source['rows']):
  origin=ROOT/row['source'];assert core.sha(origin)==row['sourceSha256']
  doc=core.read(origin);assert doc['generationContract']['contentVersion']==row['contentVersion']
  cs=core.read(origin.parent/'cases.json')['cases'];g=doc['generationContract'];b=BOUNDS[i];oldb=copy.deepcopy(g['space']['bounds']);oldobjects=copy.deepcopy(doc['objects']);oldplatforms={o['sourceIndex']:o['id']for o in oldobjects if o['type']in('terrain','platform')}
  if i==2:
   keep={'migration-shore-A':[-256,480,128,96],'migration-shore-B':[384,224,128,24],'migration-shore-C':[384,608,128,32]}
   objects=[]
   for o in doc['objects']:
    if o['type']in('terrain','platform'):
     rect=keep.get(o['id'].split('/')[-1])
     if rect is None:continue
     o.update(zip(('x','y','w','h'),rect))
    objects.append(o)
   doc['objects']=objects
   for p in g['ports']:
    if p['id'] in ('B','C'):p['position'][0]=512;p['stagingPosition'][0]=488
   cache=next(o for o in doc['objects']if o['type']=='reward');cache['x']=430;cache['mechanics']['source'].update(position=[448,206],region=[418,200,60,12])
  else:
   doc['objects']=[v for o in doc['objects']if (v:=clip(o,b)if o['type']in('terrain','platform','gate')else o)is not None]
  if i==4:
   p=next(p for p in g['ports']if p['id']=='A');p['position'][0]=256;p['stagingPosition'][0]=280
  if i==0:doc['objects'].append(enemy(doc,'review-center-diver','plains_diver',640,520))
  if i==1:doc['objects'].append(enemy(doc,'review-crest-sentry','plains_sentry',1136,144))
  if i==2:
   doc['objects'].append(enemy(doc,'review-cache-sentry','plains_sentry',474,208))
   doc['objects'].append(enemy(doc,'review-gap-diver','plains_diver',160,320))
  platforms=[o for o in doc['objects']if o['type']in('terrain','platform')]
  for j,o in enumerate(platforms):o['sourceIndex']=j
  byid={o['id']:o for o in doc['objects']}
  for p in g['ports']:
   o=byid[p['objectId']];o['x']=p['position'][0]-12;o['y']=p['position'][1]-18
   p['connection']=dict(status='declared',region=dict(x=p['position'][0]-32,y=p['position'][1]-32,w=64,h=64));p['permissionStatus']='declared_pending_revision_validation'
  g['space']['bounds']=copy.deepcopy(b);g['foundation'].update(widthBlocks=b['w']//128,heightBlocks=b['h']//128)
  g['space']['occupancy']['objectIds']=[o['id']for o in doc['objects']if o['type']not in('entry','exit','route','anchor','note','trackLine')]
  g['space']['occupancy']['regions']=[v for r in g['space']['occupancy'].get('regions',[])if (v:=clip(r,b))is not None]
  g['space']['dynamicEnvelopes']=[e for e in g['space']['dynamicEnvelopes']if e['objectId']in byid]+[dict(objectId=o['id'],region='UNKNOWN',status='UNKNOWN',note='Real original enemy; patrol/attack envelope awaits revised physical evidence')for o in doc['objects']if o['type']=='enemy']
  for k in ('actionClearance',):
   if isinstance(g['space'].get(k),dict):g['space'][k]['regions']=[v for r in g['space'][k].get('regions',[])if (v:=clip(r,b))is not None]
  g['composition']['cells']=[dict(id=o['id'],objectIds=[o['id']],contentVersion='sha256:'+'0'*64)for o in doc['objects']if o['type']not in('route','entry','exit','anchor','note')]
  for seam in g['space']['seams']:
   p=next((p for p in g['ports']if seam['id']in p['seamIds']),None)
   if p:seam['region']=copy.deepcopy(p['connection']['region'])
   seam['status']='UNKNOWN'
  for v in g['validations']:v.update(result='UNKNOWN',artifacts=[],coverage={},failures=[],method='pending_user_revision_physics',unverified=['geometry and enemies changed; old evidence not inherited'])
  if g.get('staticChecks'):g['staticChecks']['result']='UNKNOWN'
  for rel in g['relations']:rel['status']='UNKNOWN'
  for r in g['routes']:
   r['availability']='UNKNOWN';r['evidenceStatus']='UNKNOWN';r['transfer']['status']='UNKNOWN';r['return']['status']='UNKNOWN';r['onward']['status']='UNKNOWN';r['durationSeconds']='UNKNOWN'
   a=next(p for p in g['ports']if p['id']==r['from']);z=next(p for p in g['ports']if p['id']==r['to']);r['localDisplacementBlocks']=[(z['position'][k]-a['position'][k])/128 for k in(0,1)]
   o=byid[r['pathObjectId']];o['points']=[dict(zip(('x','y'),p['stagingPosition']))for p in(a,z)];o['note']='待验证的端口方向示意；不是实测动作轨迹'
  for closure in g.get('closures',[]):closure.update(status='UNKNOWN',validationIds=[]);closure['objectIds']=[v for v in closure['objectIds']if v in byid]
  g['mirror'].update(status='UNKNOWN',validationIds=[])
  corners.annotate(doc)
  choice,note=NOTES[i];g['generation']['humanReviewRevision']=dict(id='batch-001/revision-001',sourceVersion=row['contentVersion'],sourceSha256=row['sourceSha256'],decisionOnSource=choice,verbatim=note,status='REQUESTED_EDITS_APPLIED_AWAITING_REVIEW',technicalApproval='UNKNOWN')
  # Every case shares exactly the authored Cell geometry. Frozen control programs remain local programs, never synthetic motion.
  content=godot_package.content_from_objects(doc)
  for c in cs:
   original_ports={p['id']:copy.deepcopy(p)for p in c['ports']}
   c.update(copy.deepcopy(content));c['ports']=[]
   for p in g['ports']:c['ports'].append(dict(id=p['id'],position=copy.deepcopy(p['stagingPosition']),normal=p['normal'],support_index=byid[p['support']['objectId']]['sourceIndex']))
   for p in g['ports']:
    if p['id']in c.get('block_ports',{}):c['block_ports'][p['id']].update(position=copy.deepcopy(p['position']),stagingPosition=copy.deepcopy(p['stagingPosition']))
   if i==2:
    c['spawn']=[-232,462];c['entry_port']=[-232,462];c['exit_port']=[448,206]if c['route_spec']['to_port']=='B'else[488,590];c['goal']=[c['exit_port'][0]-7,c['exit_port'][1]-4,14,8]
    for command in c['control_plan']:
     dyn=command.get('trigger',{}).get('dynamic',{})
     if dyn.get('kind')=='actor_x':dyn['value']=-156
     if 'target_x'in command:command['target_x']=c['exit_port'][0]
   if i==4:c['spawn'][0]=max(c['spawn'][0],280);c['entry_port'][0]=280
   c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[0,0],cells=[[x,y]for x in range(b['x']//128,(b['x']+b['w'])//128)for y in range(b['y']//128,(b['y']+b['h'])//128)])
   if c.get('migration_compat'):c['migration_compat']['foundationRectangle']=copy.deepcopy(b)
   if c.get('migration_adaptation'):c['migration_adaptation']['rectangle']=copy.deepcopy(b)
   c['world_bounds']=[b['x']-256,b['y']-384,b['w']+512,b['h']+768]
   for k in('recorded_frames','factory_id','factory_evidence','validation_summary','module_sha256'):c.pop(k,None)
   c['human_review_revision']=dict(id='batch-001/revision-001',sourceVersion=row['contentVersion'])
  folder=OUT/row['moduleId'];core.write(folder/'module.mapnote.json',doc);core.write(folder/'cases.json',dict(cases=cs))
  result=core.contract(folder/'module.mapnote.json',refresh=True)
  receipt.append(dict(reviewId=row['reviewId'],moduleId=row['moduleId'],source=row['source'],sourceSha256=row['sourceSha256'],sourceVersion=row['contentVersion'],decisionOnSource=choice,verbatim=note,beforeBounds=oldb,afterBounds=b,removedObjects=[o['id']for o in oldobjects if o['id']not in byid],candidate=core.relative(folder),contentVersion=result['contentVersion']if 'contentVersion'in result else core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],status='DRAFT_REQUIRES_PHYSICS_AND_HUMAN_REVIEW'))
 core.write(OUT/'feedback.json',dict(schema='pcg/manual-review-feedback-revision/v1',sourceType='human_idea',batch='batch-001',revision='revision-001',rows=receipt,formalLibraryChanged=False,automaticBatchWorkResumed=False))
 return receipt
if __name__=='__main__':
 print(json.dumps(prepare(),ensure_ascii=False))
