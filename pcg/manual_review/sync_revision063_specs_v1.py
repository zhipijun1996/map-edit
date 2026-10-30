"""User-authorized versioned specification alignment in a dedicated main worktree."""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
IMPL=Path(__file__).resolve().parents[2];ROOT=Path(sys.argv[1]);VERBATIM='h09初始态上方只出不进\n第二轮s09可以地刺间加宽一点点。\n另外4个按照你的建议修复\n\n6个双平台继续完成\n\n规格不一致修改main的规格为最新实现'
def read(p):return json.loads((ROOT/p).read_text())
def write(p,v):p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seal(d):d.pop('designVersion',None);d['designVersion']='sha256:'+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
h=read('feedback/manual-review/implementation-handoff-v1.json');ideas=read('feedback/module-workshop/ideas-v1.json');received=read('feedback/manual-review/received-design-decisions-v1.json');revisions=read('generation/manual-review/revisions/latest.json');queue=read('generation/manual-review/queue.json');receipt='feedback/manual-review/spec-sync-r063-receipt.json';mappings={'42':('058','42'),'51':('053','51'),'52':('053','52'),'196':('053','196'),'idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3':('053','three'),'idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3':('053','lift')};selected=[r for r in h['rows']if r['reviewId']in mappings or r['reviewId']in ['idea-plains-hq09-001','idea-spec02-s09-001']];assert len(selected)==8;notes=[];numeric=[];rrows=[]
for row in selected:
 old=copy.deepcopy(row);d=read(row['designFile']);name=row['reviewId'];description='';source=None
 if name in mappings:
  rnd,label=mappings[name];res=json.loads((IMPL/('feedback/manual-review/implementation-results/revision-'+rnd+'-v1/'+label+'.json')).read_text());source=res['sourceModule'];module=json.loads((IMPL/source['path']).read_text());actual={o['id']:o for o in module['objects']};d['bounds']=copy.deepcopy(module['generationContract']['space']['bounds'])
  for visual in d['visualObjects']:
   if visual['type']in ['route','note','anchor']:continue
   assert visual['id']in actual;v=actual[visual['id']]
   for key in ['x','y','w','h','designMotion','trackId','designCollision','definition','surfaceBinding']:
    if key in v and(key in visual or key in ['x','y','w','h']):visual[key]=copy.deepcopy(v[key])
  ports={p['id']:p for p in module['generationContract']['ports']}
  for p in d['ports']:
   a=ports[p['id']]
   for key in ['position','normal','surface','permission','stagingPosition']:
    if key in a:p[key]=copy.deepcopy(a[key])
  if name in ['42','51','52']:description={'42':'同步已通过实现：右岸x304、宽208，缺口48px。','51':'同步已通过实现：屋顶及附着危险上移128px，下层岩体/危险下移64px，净空与bounds同步。','52':'同步已通过实现：屋顶及附着危险上移128px，下层岩体/危险下移64px，净空与bounds同步。'}[name]
  elif name=='196':description='同步已通过实现：底口为真实可穿平台，保留已实现支撑与jump/wall_climb要求。';d['capabilityRequirements']=copy.deepcopy(module['capabilityRequirements'])
  else:
   auth=json.loads((IMPL/('feedback/manual-review/implementation-results/revision-053-v1/authorization/revised-designs/'+label+'.json')).read_text());ids={o['id']for o in d['visualObjects']}
   for o in auth['visualObjects']:
    if o['id']not in ids and o['type']in ['gate','bell']:d['visualObjects'].append(copy.deepcopy(o))
   d['intendedRoutes']=[r for r in d['intendedRoutes']if r['from']!='B'];description='同步最新实现：顶口初态OUTPUT，接岸y64、宝箱y40，原生4秒风铃门向上出；原难度不简化。'
  d['implementationAlignment']=dict(sourceCommit='5f382eb0354f155846279b8db56eb6264ac15485',sourceModule=source,priorDesign=dict(file=old['designFile'],version=old['designVersion'],sha256=old['designFileSha256']),authorizationReceipt=receipt,scope='Specification matches actual implemented layout/interface; not a new technical certificate')
 elif name=='idea-plains-hq09-001':
  p=next(p for p in d['ports']if p['id']=='T');p['permission']='OUTPUT';d['intendedRoutes']=[r for r in d['intendedRoutes']if r['from']!='T'];d['visualObjects']=[o for o in d['visualObjects']if not(o['type']=='route'and('T-L'in o['id']or'T-to-L'in o['id']))];description='用户确认：T顶口初态只出不进；上下刺收回后同世界返回另行验证，不冒充初始双向口。'
 else:
  obs={o['id']:o for o in d['visualObjects']};assert obs['lower-wall']['y']==288 and obs['lower-rim']['y']==272;obs['lower-wall']['y']+=16;obs['lower-wall']['h']-=16;obs['lower-rim']['y']+=16;description='用户授权小幅加宽刺窗：下沿墙顶与附着刺下移16px，净高96→112px；矩形/Port/锯轨道/怪不改。'
 d['summary']=description;d.setdefault('designNotes',[]).append(description);d['userRevision']=dict(receipt=receipt,verbatim=VERBATIM,technicalValidation='UNKNOWN_FOR_NEW_SPECIFICATION',implementationAuthorized=True)
 for p in d['ports']:
  along=p['position'][1]if p['face']in ['LEFT','RIGHT']else p['position'][0];origin=d['bounds']['y']if p['face']in ['LEFT','RIGHT']else d['bounds']['x'];p['index']=round((along-origin)/128-.5)
  for c in p.get('cornerRelocations',{}).values():
   if c.get('applicable'):c['permission']=p['permission'];c['allowed']='UNKNOWN';c['reason']='基础规格已同步；角落换边仍需独立验证。'
 seal(d);version=d['designVersion'];is_numeric=name.isdigit()
 if is_numeric:
  file='generation/manual-review/designs/implementation-sync-r063/'+name+'.design.json';oldrev=next(r for r in revisions['rows']if r['moduleId']==row['moduleId']);numeric.append(dict(moduleId=row['moduleId'],reviewId=name,file=file,reviewStage='design',baseSourceSha256=oldrev['baseSourceSha256'],beforeDiagram=oldrev['diagram'],beforeVersion=old['designVersion'],verbatim=VERBATIM,title=d['title'],summary=description,notes=[description]))
 else:
  idea=next(i for i in ideas['rows']if i['id']==row['sourceIdea']['id']);options=idea.get('designVariants',[])or[idea['design']];option=next(v for v in options if v['version']==old['designVersion']);previous=copy.deepcopy(option);file='generation/module-workshop/ideas/'+idea['id']+'/'+version[7:19]+'/design.json';diagram='ideas/'+idea['id']+'/'+version[7:19]+'/images/'+d['reviewId']+'.png';option.update(file=file,version=version,sha256='',diagram=diagram);idea.setdefault('designHistory',[]).append(previous);idea.setdefault('approvalHistory',[]).append(dict(version=old['designVersion'],receipt=idea.get('designApprovals',{}).get(old['designVersion'],idea.get('decisionReceipt'))))
  if idea.get('designApprovals'):
   a=idea['designApprovals'].pop(old['designVersion']);a.update(receipt=None);idea['designApprovals'][version]=a
  else:idea['decisionReceipt']=None
  rrows.append((idea,option,row,version,description))
 write(file,d);row.update(designFile=file,designVersion=version,designFileSha256=sha(ROOT/file),authorizationReceipt=receipt);row.setdefault('specificationHistory',[]).append({k:old[k]for k in ['designFile','designVersion','designFileSha256']});notes.append(dict(reviewId=name,moduleId=row['moduleId'],version=version,decision='KEEP',file=file,sha256=sha(ROOT/file),summary=description))
 if is_numeric:
  previous=next(x for x in received['rows']if x['moduleId']==row['moduleId']);received['history'].append(copy.deepcopy(previous));previous.update(version=version,decision='KEEP',verbatim=VERBATIM,receipt=receipt)
for idea,option,row,version,description in rrows:
 option['sha256']=row['designFileSha256'];entry=dict(path=receipt,sha256='PENDING')
 if idea.get('designApprovals'):idea['designApprovals'][version]['receipt']=entry
 else:idea['decisionReceipt']=entry
 # Render the actual revised authoritative geometry and permission.
 folder=ROOT/option['file'];folder=folder.parent;manifest=dict(rows=[dict(reviewId=read(option['file'])['reviewId'],moduleId=idea['id'],title=read(option['file'])['title'],summary=description,source=option['file'],sourceSha256=option['sha256'],instructions=[description,'技术资格按实现报告另核，不从设计确认继承。'])]);write(folder.relative_to(ROOT)/'diagram-batch.json',manifest);subprocess.run(['python3',str(ROOT/'generation/manual-review/batch-001/render_diagrams.py'),'--manifest',str(folder/'diagram-batch.json'),'--out',str(folder/'images'),'--draft'],check=True,cwd=ROOT)
write(receipt,dict(schema='pcg/human-specification-sync/v1',sourceType='human_feedback',decision='KEEP',verbatim=VERBATIM,rows=notes,implementationAuthorized=True,technicalApproval=False,mainSpecSyncAuthorized=True));rh=sha(ROOT/receipt)
for idea,option,row,version,description in rrows:
 if idea.get('designApprovals'):idea['designApprovals'][version]['receipt']=dict(path=receipt,sha256=rh)
 else:idea['decisionReceipt']=dict(path=receipt,sha256=rh)
received['latestReceipt']=receipt;h['revision']='implementation-sync-r063';write('feedback/manual-review/received-design-decisions-v1.json',received);write('feedback/module-workshop/ideas-v1.json',ideas);write('feedback/manual-review/implementation-handoff-v1.json',h)
folder='generation/manual-review/designs/implementation-sync-r063';write(folder+'/index.json',dict(id='implementation-sync-r063',rows=numeric));subprocess.run(['python3',str(ROOT/'tools/publish_design_review.py'),str(ROOT/folder)],check=True,cwd=ROOT);subprocess.run(['node','tools/build_module_workshop.mjs'],check=True,cwd=ROOT);print('SYNCED_EIGHT_SPECIFICATIONS',[(r['reviewId'],r['version'][:19])for r in notes])
