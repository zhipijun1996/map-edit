import copy,hashlib,json,shutil,subprocess,sys
from pathlib import Path
R=Path(sys.argv[1])
def read(p):return json.loads((R/p).read_text())
def write(p,d):p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
h=read('feedback/manual-review/implementation-handoff-v1.json');ideas=read('feedback/module-workshop/ideas-v1.json');receipt_path='feedback/manual-review/spec-sync-r063-receipt.json';receipt=read(receipt_path)
p=R/'generation/manual-review/batch-001/render_diagrams.py';s=p.read_text().replace("'FORBIDDEN_EGRESS':'禁止'","'FORBIDDEN_EGRESS':'禁止','FORBIDDEN_INGRESS':'初态禁入'");p.write_text(s)
for row in h['rows']:
 if row['reviewId']not in ['idea-plains-hq09-001','idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3','idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3']:continue
 d=read(row['designFile']);old=row['designVersion'];oldfile=row['designFile'];out={p['id']for p in d['ports']if p['permission']=='OUTPUT'}
 for c in d.get('routeMatrix',{}).get('cells',[]):
  if c['from']in out and c['from']!=c['to']:c['status']='FORBIDDEN_INGRESS'
 paths={r.get('pathObjectId',r['id'])for r in d['intendedRoutes']};d['visualObjects']=[o for o in d['visualObjects']if o['type']!='route'or o['id']in paths];d['connectivityIntent']='initial_permission_compatible_routes';d['routeCaption']='初始顶口只出不进；矩阵按初态权限，开门/收刺后的同世界返回另验。';d.pop('designVersion');d['designVersion']='sha256:'+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();new=d['designVersion'];folder=str(Path(oldfile).parent.parent/new[7:19]);file=folder+'/design.json';write(file,d)
 row.update(designVersion=new,designFile=file,designFileSha256=sha(file));item=next(x for x in receipt['rows']if x['reviewId']==row['reviewId']);item.update(version=new,file=file,sha256=sha(file));idea=next(x for x in ideas['rows']if x['id']==row['sourceIdea']['id']);option=next(x for x in(idea.get('designVariants')or[idea['design']])if x['version']==old);option.update(version=new,file=file,sha256=sha(file),diagram=folder.removeprefix('generation/module-workshop/')+'/images/'+d['reviewId']+'.png')
 if idea.get('designApprovals'):idea['designApprovals'][new]=idea['designApprovals'].pop(old);idea.setdefault('variantDecisions',{})[new]='KEEP'
 manifest=dict(rows=[dict(reviewId=d['reviewId'],moduleId=idea['id'],title=d['title'],summary=d['summary'],source=file,sourceSha256=sha(file),instructions=[d['summary'],'初态禁止从上口进入；技术验证和后续返回另行记录。'])]);write(folder+'/diagram-batch.json',manifest);subprocess.run(['python3','generation/manual-review/batch-001/render_diagrams.py','--manifest',folder+'/diagram-batch.json','--out',folder+'/images','--draft'],cwd=R,check=True);shutil.rmtree(R/Path(oldfile).parent)
write(receipt_path,receipt);rh=sha(receipt_path)
for row in h['rows']:
 if row['reviewId']not in [x['reviewId']for x in receipt['rows']]or row['reviewId'].isdigit():continue
 idea=next(x for x in ideas['rows']if x['id']==row['sourceIdea']['id']);binding=dict(path=receipt_path,sha256=rh)
 if idea.get('designApprovals'):idea['designApprovals'][row['designVersion']]['receipt']=binding
 else:idea['decisionReceipt']=binding
write('feedback/manual-review/implementation-handoff-v1.json',h);write('feedback/module-workshop/ideas-v1.json',ideas);subprocess.run(['node','tools/build_module_workshop.mjs'],cwd=R,check=True)
