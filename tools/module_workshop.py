"""Idea intake, versioned diagram publication and exact human design decisions. No Module generation or physics."""
from pathlib import Path
import argparse, copy, hashlib, json, re, subprocess
from publish_design_review import seal_design
ROOT=Path(__file__).resolve().parents[1]
IDEAS='feedback/module-workshop/ideas-v1.json'
def read(p):return json.loads((ROOT/p).read_text())
def write(p,d):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def safe_id(id):
 if not re.fullmatch(r'idea-[a-z0-9-]{6,100}',id):raise ValueError('Use a stable idea- ID')
 return id

def intake(packet):
 d=read(IDEAS);incoming=packet.get('drafts',packet.get('rows',[]));existing={r['id']:r for r in d['rows']}
 if not incoming:raise ValueError('No ideas')
 for row in incoming:
  id=safe_id(row['id']);raw=row.get('verbatim');kind=row.get('sourceType')
  if kind not in ['human_idea','ai_idea']or not isinstance(raw,str)or not raw.strip()or len(raw)>20000:raise ValueError('Keep source type and verbatim text')
  if id in existing:
   if existing[id]['verbatim']!=raw:raise ValueError('Stable ID has different original text; create a revision instead')
   continue
  if row.get('stage','IDEA')!='IDEA':raise ValueError('Intake cannot grant approval or implementation')
  r=dict(id=id,title=row.get('title',''),sourceType=kind,verbatim=raw,interpretation=None,constraints=row.get('constraints',{}),stage='IDEA',humanApproval='UNKNOWN',technicalStatus='UNKNOWN',productionApproval=False)
  if kind=='ai_idea':
   if not row.get('source',{}).get('producer'):raise ValueError('Record actual model caller')
   r['source']=row['source']
  existing[id]=r
 d['rows']=list(existing.values());write(IDEAS,d)

def attach(id,design):
 id=safe_id(id);d=read(IDEAS);r=next(r for r in d['rows']if r['id']==id)
 if r['stage']=='READY_FOR_IMPLEMENTATION':raise ValueError('Do not overwrite an approved design; first agree a revision in chat')
 if design.get('id')!=id:raise ValueError('Design identity mismatch')
 design=seal_design(copy.deepcopy(design));version=design['designVersion'];folder='generation/module-workshop/ideas/'+id+'/'+version[7:19];file=folder+'/design.json'
 if (ROOT/file).exists()and read(file)!=design:raise ValueError('Version collision')
 write(file,design)
 manifest=dict(rows=[dict(reviewId=design['reviewId'],moduleId=id,title=design['title'],summary=design.get('summary',''),source=file,sourceSha256=digest(file),instructions=design.get('reviewInstructions',[]))]);write(folder+'/diagram-batch.json',manifest)
 subprocess.run(['python3','generation/manual-review/batch-001/render_diagrams.py','--manifest',folder+'/diagram-batch.json','--out',folder+'/images','--draft'],cwd=ROOT,check=True)
 if r.get('design'):r.setdefault('history',[]).append(dict(design=r['design'],stage=r['stage']))
 old=r.get('design',{});meta=dict(file=file,version=version,sha256=digest(file),diagram=folder.removeprefix('generation/module-workshop/')+'/images/'+design['reviewId']+'.png')
 if old.get('key'):
  meta.update(key=old['key'],label=old.get('label',design['title']));r['designVariants']=[meta if v.get('key')==old['key']else v for v in r.get('designVariants',[])]
 r.update(title=design['title'],stage='DESIGN_REVIEW',design=meta,humanApproval='UNKNOWN')
 write(IDEAS,d)

def decide(receipt):
 id=safe_id(receipt['id']);d=read(IDEAS);r=next(r for r in d['rows']if r['id']==id)
 if receipt.get('sourceType')!='human_feedback'or not isinstance(receipt.get('verbatim'),str)or not receipt['verbatim'].strip():raise ValueError('Use actual human feedback received in chat')
 if r.get('design',{}).get('version')!=receipt.get('designVersion'):
  variant=next((v for v in r.get('designVariants',[])if v['version']==receipt.get('designVersion')),None)
  if variant is None or r['stage']!='DESIGN_REVIEW':raise ValueError('Decision targets a stale or missing design')
  if digest(variant['file'])!=variant['sha256']or read(variant['file']).get('designVersion')!=variant['version']:raise ValueError('Variant bytes changed')
  r.setdefault('history',[]).append(dict(design=copy.deepcopy(r['design']),stage=r['stage']))
  r['design']=copy.deepcopy(variant)
 if digest(r['design']['file'])!=r['design']['sha256']:raise ValueError('Design bytes changed')
 choice=receipt.get('decision')
 if choice not in ['KEEP','CHANGE','DISCARD']:raise ValueError('Unknown decision')
 if r['stage']!='DESIGN_REVIEW':raise ValueError('Design already resolved; record a new revision explicitly')
 path='feedback/manual-review/idea-decisions/'+id+'-'+receipt['designVersion'][7:19]+'-'+str(len(r.get('feedback',[]))+1)+'.json'
 canonical=dict(reviewId=id,moduleId=id,version=receipt['designVersion'],decision=choice,verbatim=receipt['verbatim'],versionType='design')
 if choice=='KEEP'and any(x['moduleId']==id for x in read('feedback/manual-review/implementation-handoff-v1.json')['rows']):raise ValueError('An implementation handoff already exists')
 write(path,dict(schema='pcg/human-module-design-feedback/v1',scope='design_only',verbatimMessage=receipt['verbatim'],rows=[canonical],**receipt))
 aggregate='feedback/manual-review/received-design-decisions-v1.json'
 received=read(aggregate)if(ROOT/aggregate).exists()else dict(schema='pcg/received-design-decisions/v1',scope='design_only',rows=[],history=[])
 old=next((v for v in received['rows']if v['reviewId']==id),None)
 if old is not None:received.setdefault('history',[]).append(copy.deepcopy(old));old.clear();old.update(canonical)
 else:received['rows'].append(canonical)
 received['latestReceipt']=path;write(aggregate,received)
 r['decisionReceipt']=dict(path=path,sha256=digest(path));r['humanApproval']=choice;r['stage']={'KEEP':'READY_FOR_IMPLEMENTATION','CHANGE':'DESIGN_REVIEW','DISCARD':'DISCARDED'}[choice]
 r.setdefault('feedback',[]).append(copy.deepcopy(receipt))
 if r.get('designVariants'):
  r.setdefault('variantDecisions',{})[receipt['designVersion']]=choice
  if choice=='DISCARD':
   pending=[v for v in r['designVariants']if r['variantDecisions'].get(v['version'])not in ['KEEP','DISCARD']]
   if pending:r.update(design=copy.deepcopy(pending[0]),stage='DESIGN_REVIEW',humanApproval='UNKNOWN')
 if choice=='KEEP':
  file='feedback/manual-review/implementation-handoff-v1.json';h=read(file)
  if any(x['moduleId']==id for x in h['rows']):raise ValueError('An implementation handoff already exists')
  h['rows'].append(dict(reviewId=id,moduleId=id,designFile=r['design']['file'],designVersion=r['design']['version'],designFileSha256=r['design']['sha256'],status='READY_FOR_IMPLEMENTATION',sourceIdea=dict(file=IDEAS,id=id),outputDirectory='pcg/manual_review/implementation/ideas/'+id,designDecisionSource=path));h['revision']+=1;write(file,h)
 write(IDEAS,d)

def approve_variants(receipt):
 """One real human message can approve several already-published exact options."""
 id=safe_id(receipt['id']);d=read(IDEAS);r=next(r for r in d['rows']if r['id']==id)
 if receipt.get('sourceType')!='human_feedback'or not receipt.get('verbatim','').strip():raise ValueError('Actual human feedback required')
 versions=receipt.get('designVersions',[])
 if not versions or len(set(versions))!=len(versions):raise ValueError('Unique published versions required')
 hfile='feedback/manual-review/implementation-handoff-v1.json';h=read(hfile);selected=[]
 for version in versions:
  v=next((v for v in r.get('designVariants',[])if v['version']==version),None)
  if v is None or not v.get('key'):raise ValueError('Version is not a published option')
  if digest(v['file'])!=v['sha256']or read(v['file']).get('designVersion')!=version:raise ValueError('Published option changed')
  module_id=safe_id(id+'-'+v['key'])
  if any(x['moduleId']==module_id or(x.get('sourceIdea',{}).get('id')==id and x['designVersion']==version)for x in h['rows']):raise ValueError('Option already handed off')
  selected.append((v,module_id))
 # All checks finish before any receipt or queue is mutated.
 stamp=hashlib.sha256('|'.join(versions).encode()).hexdigest()[:12];path='feedback/manual-review/idea-decisions/'+id+'-variants-'+stamp+'.json'
 canonical=[dict(reviewId=mid,moduleId=mid,version=v['version'],decision='KEEP',verbatim=receipt['verbatim'],versionType='design',sourceIdeaId=id,designVariant=v['key'])for v,mid in selected]
 write(path,dict(schema='pcg/human-module-design-feedback/v1',scope='design_only',verbatimMessage=receipt['verbatim'],rows=canonical,decision='KEEP',**receipt))
 aggregate='feedback/manual-review/received-design-decisions-v1.json';received=read(aggregate)
 for v,mid in selected:
  h['rows'].append(dict(reviewId=mid,moduleId=mid,designFile=v['file'],designVersion=v['version'],designFileSha256=v['sha256'],status='READY_FOR_IMPLEMENTATION',sourceIdea=dict(file=IDEAS,id=id,variantKey=v['key']),outputDirectory='pcg/manual_review/implementation/ideas/'+id+'/'+v['key'],designDecisionSource=path))
  r.setdefault('designApprovals',{})[v['version']]=dict(moduleId=mid,reviewId=mid,decision='KEEP',receipt=dict(path=path,sha256=digest(path)))
  r.setdefault('variantDecisions',{})[v['version']]='KEEP'
 received['rows'].extend(canonical);received['latestReceipt']=path;h['revision']+=1
 r.setdefault('feedback',[]).append(dict(receipt,decision='KEEP'));r.update(stage='READY_FOR_IMPLEMENTATION',humanApproval='KEEP',decisionReceipt=dict(path=path,sha256=digest(path)))
 write(aggregate,received);write(hfile,h);write(IDEAS,d)

def link_result(id,result_path):
 id=safe_id(id);path=Path(result_path)
 if path.is_absolute()or'..'in path.parts or not str(path).startswith('feedback/manual-review/implementation-results/'):raise ValueError('Use the existing implementation-results path')
 h=read('feedback/manual-review/implementation-handoff-v1.json');entry=next(x for x in h['rows']if x['moduleId']==id);idea_id=entry.get('sourceIdea',{}).get('id',id)
 d=read(IDEAS);r=next(r for r in d['rows']if r['id']==idea_id);result=read(result_path)
 if r['humanApproval']!='KEEP'or result.get('designVersion')!=entry['designVersion']or result.get('moduleId')!=id:raise ValueError('Result must bind an approved design identity/version')
 ref=dict(path=str(path),sha256=digest(result_path))
 if idea_id==id:r['implementationResult']=ref
 else:r.setdefault('implementationResults',{})[entry['designVersion']]=ref
 write(IDEAS,d)


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 a=s.add_parser('intake');a.add_argument('packet',type=Path)
 a=s.add_parser('attach-design');a.add_argument('--id',required=True);a.add_argument('--design',type=Path,required=True)
 a=s.add_parser('record-decision');a.add_argument('receipt',type=Path)
 a=s.add_parser('approve-variants');a.add_argument('receipt',type=Path)
 a=s.add_parser('link-result');a.add_argument('--id',required=True);a.add_argument('--result',required=True)
 a=p.parse_args()
 if a.command=='intake':intake(json.loads(a.packet.read_text()))
 elif a.command=='attach-design':attach(a.id,json.loads(a.design.read_text()))
 elif a.command=='record-decision':decide(json.loads(a.receipt.read_text()))
 elif a.command=='approve-variants':approve_variants(json.loads(a.receipt.read_text()))
 else:link_result(a.id,a.result)
 subprocess.run(['node','tools/build_module_workshop.mjs'],cwd=ROOT,check=True)
