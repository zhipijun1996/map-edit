"""Minimal immutable retrieval evidence for the fifteen imported legacy records.

Follow hashed record/document references and Macro component documents. Ordinary
artifact JSON is opaque: its original bytes are required, not its complete raw
run/source-snapshot history. No source file, library record or Engine is changed.
"""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT.parent
OUT=ROOT/'results/workshop-plains-inventory-v1/legacy-dependency-closure.json'
INVENTORY=ROOT/'results/workshop-plains-inventory-v1/inventory-v2.json'

def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())

def build():
 inv=read(INVENTORY);items={};doc_seen=set();roots=[];component_versions={};unknown=[];unhashed_paths=[]
 def resolve(raw):
  p=(REPO/raw).resolve()
  if not p.is_relative_to(ROOT):raise ValueError('dependency outside pcg archive root:'+raw)
  return p
 def add(raw,expected,reason,version):
  p=resolve(raw);name=str(p.relative_to(ROOT))
  if not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('unknown required dependency hash:'+str((raw,expected)))
  actual=sha(p)
  if actual!=expected:raise ValueError('immutable dependency SHA mismatch:'+raw)
  row=items.setdefault(name,dict(path=name,repository_path='pcg/'+name,sha256=actual,bytes=p.stat().st_size,required_by_versions=set(),reasons=set()))
  if row['sha256']!=expected:raise ValueError('conflicting dependency hashes:'+name)
  row['required_by_versions'].add(version);row['reasons'].add(reason);return p
 def hashed_refs(value,reason,version):
  if isinstance(value,dict):
   if isinstance(value.get('path'),str)and'sha256'in value:
    if re.fullmatch('[0-9a-f]{64}',str(value['sha256'])):add(value['path'],value['sha256'],reason,version)
    else:unknown.append(dict(reference=value,reason=reason,version=version))
   for key,child in value.items():hashed_refs(child,reason+'/'+key,version)
  elif isinstance(value,list):
   for child in value:hashed_refs(child,reason,version)
 def document(raw,expected,version,reason):
  p=add(raw,expected,reason,version);key=(str(p),version)
  if key in doc_seen:return
  doc_seen.add(key);d=read(p);g=d['generationContract']
  # Includes every physics-proof artifact, source.cases, routeCases.artifacts,
  # explicit component refs and any other hash-bound provenance in the document.
  hashed_refs(d,'document-hashed-reference',version)
  for proof in g.get('validations',[]):
   if proof.get('kind')=='physics':
    for a in proof.get('artifacts',[]):add(a['path'],a['sha256'],'document-physics-proof',version)
  for dep in g['generation']['source'].get('componentDocuments',[]):
   component_versions[dep['contentVersion']]=dep['path'];document(dep['path'],dep['sha256'],version,'macro-component-document')
 for row in inv['records']:
  version=row['contentVersion'];folder=ROOT/'map_directed/library/candidates'/version[7:];record=read(folder/'record.json');case_name='cases.json'if row['multi_route']else'case.json'
  if record['contentVersion']!=version:raise ValueError('legacy record version drift')
  for filename in ['record.json',case_name,'module.mapnote.json']:
   raw=str((folder/filename).relative_to(REPO));add(raw,row['files'][filename],'shared-legacy-root',version);roots.append(raw[4:])
  hashed_refs(record,'record-hashed-reference',version)
  for a in record.get('evidence',[]):add(a['path'],a['sha256'],'record-evidence',version)
  document(str((folder/'module.mapnote.json').relative_to(REPO)),record['document_sha256'],version,'legacy-standard-document')
  cases=read(folder/case_name);case_list=cases['cases']if row['multi_route']else[cases]
  # These refs are opaque original cases; do not serialize rewritten per-case
  # substitutes or recursively pull unrelated calibration/holdout populations.
  hashed_refs(cases,'canonical-case-hashed-reference',version)
  gc=read(folder/'module.mapnote.json')['generationContract'];run=gc['generation']['source'].get('run')
  if isinstance(run,str)and run!='UNKNOWN':
   batches=resolve(run+'/batches.json')
   if batches.exists():
    by={b['batch']:b for b in read(batches)}
    for case in case_list:
     ev=case.get('factory_evidence')
     if not ev:continue
     batch=by[ev['batch']]
     if ev['raw_output_sha256']!=batch['raw_output_sha256']or ev['output']!=batch['gzip_path']:raise ValueError('canonical case evidence binding drift')
     add(run+'/batches.json',sha(batches),'canonical-case-batch-index',version)
     add(run+'/'+batch['gzip_path'],batch['gzip_sha256'],'canonical-case-original-output',version)
 if unknown:raise ValueError('unknown hash-bound reference in legacy closure:'+str(unknown))
 rows=[]
 for name,row in sorted(items.items()):
  row['required_by_versions']=sorted(row['required_by_versions']);row['reasons']=sorted(row['reasons']);rows.append(row)
 result=dict(schema='pcg/plains-legacy-dependency-closure/v1',path_base='pcg',version_count=15,shared_root_file_count=len(set(roots)),component_document_count=len(component_versions),component_documents=[dict(contentVersion=v,repository_path=p)for v,p in sorted(component_versions.items())],paths=[r['path']for r in rows],files=rows,file_count=len(rows),total_bytes=sum(r['bytes']for r in rows),all_sha256_verified=True,missing_paths=[],unknown_required_hashes=[],inventory=dict(path=str(INVENTORY.relative_to(ROOT)),sha256=sha(INVENTORY)),builder=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=sha(Path(__file__))),archive_usage='Pass paths to original pcg.tools.build_archive.build; every path is relative to pcg root and retains original bytes/SHA.',scope='Shared legacy record/case(s)/standard docs plus their explicitly hash-bound evidence and Macro components, including component physics proofs. Ordinary JSON artifacts remain opaque.',excluded='Full source_snapshot trees, unrelated raw calibration/holdout batches, videos, private duplicate records, and historical source archives are not recursively copied. Original source_binding files are included as evidence; their source_files maps do not require extraction of all historical source bytes for unchanged CandidateLibrary retrieval.',new_physics_cases=0,engine_started=False,original_files_changed=False)
 with OUT.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(path=str(OUT.relative_to(REPO)),versions=15,files=result['file_count'],bytes=result['total_bytes'],components=len(component_versions),all_sha256_verified=True,new_physics_cases=0)))
if __name__=='__main__':build()
