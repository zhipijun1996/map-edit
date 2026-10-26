"""Audit/import the published legacy six-family set, Map adapter and two Macros.

Uses original CandidateLibrary/WorkshopLibrary and immutable byte copies. No
Engine, generator, terrain construction, gameplay changes, or physics launches.
"""
import argparse,collections,copy,json,os,re,shutil,subprocess,time,uuid
from pathlib import Path
from pcg.map_directed.library import CandidateLibrary,verified_document,verify_case_binding,withdrawn_versions
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import module_hash
REPO=Path(__file__).resolve().parents[4]
LIBRARY=REPO/'pcg/map_directed/library'
OUT=REPO/'pcg/results/workshop-plains-inventory-v1'
MANIFESTS=[('baseline_six_family_interface','generation/workshop/v2/modules/manifest.json'),('map_adapter','generation/workshop/map-demand-rework-v3/modules/manifest.json'),('composed_macro','generation/workshop/macro-v1/modules/manifest.json')]

def path(p):
 q=(REPO/p).resolve()
 if not q.is_relative_to(REPO):raise ValueError('outside_repository:'+str(p))
 return q

def relative(p):return str(path(p).relative_to(REPO))
def read(p):return json.loads(path(p).read_text())
def write(p,value):
 p=path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

class Audit:
 def __init__(self):self.files={};self.documents={};self.components={};self.unknown_hashes=[]
 def sha(self,p,expected=None):
  p=path(p);actual=file_sha(p);name=relative(p)
  if expected is not None and actual!=expected:raise ValueError('sha_mismatch:'+name)
  if name in self.files and self.files[name]!=actual:raise ValueError('changed_during_audit:'+name)
  self.files[name]=actual;return actual
 def nested_artifacts(self,value):
  if isinstance(value,dict):
   if isinstance(value.get('path'),str)and isinstance(value.get('sha256'),str):
    if re.fullmatch('[0-9a-f]{64}',value['sha256']):self.sha(value['path'],value['sha256'])
    else:self.unknown_hashes.append(value)
   for v in value.values():self.nested_artifacts(v)
  elif isinstance(value,list):
   for v in value:self.nested_artifacts(v)
 def document(self,p):
  p=path(p);self.sha(p)
  if relative(p)in self.documents:return self.documents[relative(p)]
  doc=verified_document(p);self.nested_artifacts(doc);self.documents[relative(p)]=doc
  deps=doc['generationContract']['generation']['source'].get('componentDocuments',[])
  for dep in deps:
   self.sha(dep['path'],dep['sha256']);component=self.document(dep['path'])
   if component['id']!=dep['id']or component['generationContract']['contentVersion']!=dep['contentVersion']:raise ValueError('macro_component_identity_drift')
   self.components[dep['contentVersion']]=dict(dep,independent_candidate_record=False,role='exact Macro dependency; not an added family or automatically indexed standalone candidate')
  return doc
 def record(self,folder,selected_role):
  folder=path(folder);record=read(folder/'record.json');self.sha(folder/'record.json');doc=self.document(folder/'module.mapnote.json');gc=doc['generationContract'];self.sha(folder/'module.mapnote.json',record['document_sha256']);self.nested_artifacts(record)
  if record['contentVersion']!=gc['contentVersion']or record['id']!=doc['id']:raise ValueError('record_document_version_mismatch')
  if record['contentVersion']in withdrawn_versions():raise ValueError('withdrawn_version_cannot_import')
  multi=record['technical_status']=='passed_scoped_multi_route';filename='cases.json'if multi else'case.json';self.sha(folder/filename,record['cases_sha256'if multi else'case_sha256']);value=read(folder/filename);cases=value['cases']if multi else[value]
  if multi:
   declared={r['sourceCaseId']:r['moduleSha256']for r in gc['generation']['source']['routeCases']}
   if declared!={c['id']:module_hash(c)for c in cases}:raise ValueError('multi_case_binding_mismatch')
   if any(c.get('module_sha256')!=module_hash(c)for c in cases):raise ValueError('multi_case_content_hash_mismatch')
   WorkshopLibrary(folder.parent.parent).verify_components(folder/'module.mapnote.json',doc)
   specification=record['specification'];quality=record['quality_gates']
  else:
   verify_case_binding(cases[0],doc);specification=cases[0].get('map_specification','UNKNOWN');quality=[record.get('quality_gate',{})]
  if selected_role!='existing_shared'and(record['technical_status']not in ['passed_scoped','passed_scoped_multi_route']or any(q.get('status')!='awaiting_human_review'or q.get('engineering_tier')!='regular'for q in quality)):raise ValueError('legacy_target_original_regular_gate_missing')
  if record.get('production_admitted'):raise ValueError('unexpected_production_admission')
  files=['record.json',filename,'module.mapnote.json'];caps=sorted({cap for c in cases for cap in c['capabilities']})
  return dict(contentVersion=record['contentVersion'],id=record['id'],role=selected_role,family=cases[0]['family'],kind=gc['kind'],source_library=relative(folder.parent.parent),source_record=relative(folder/'record.json'),source_directory=relative(folder),document_path=relative(folder/'module.mapnote.json'),case_path=relative(folder/filename),files={n:self.sha(folder/n)for n in files},multi_route=multi,canonical_case_ids=[c['id']for c in cases],map_specification=specification,capabilities=caps,capability_requirements=doc.get('capabilityRequirements','UNKNOWN'),quality_gates=quality,technical_status=record['technical_status'],technical_scope=record.get('technical_scope','UNKNOWN'),ports=len(gc['ports']),ordered_relations=len(gc['relations']),declared_paths=sum(r['status']=='path'for r in gc['relations']),unknown_relations=sum(r['status']=='UNKNOWN'for r in gc['relations']),unknowns=dict(return_status=[r.get('return','UNKNOWN')for r in gc['routes']],route_transfers=[r.get('transfer','UNKNOWN')for r in gc['routes']],transforms=gc['space'].get('transforms','UNKNOWN'),seams=gc['space'].get('seams','UNKNOWN'),whole_map='UNKNOWN',arbitrary_state_reuse='UNKNOWN',new_placement_validation_required=True),production_admitted=False,human_quality_record=record.get('human_quality','UNKNOWN'))

def published_targets(audit):
 targets=[]
 for role,filename in MANIFESTS:
  p=path(filename);audit.sha(p)
  for item in read(p)['modules']:
   if role=='composed_macro'and item.get('kind')!='macro':continue
   targets.append(dict(role=role,contentVersion=item['contentVersion'],published_document=relative(p.parent/item['file']),publication_manifest=filename))
 if len(targets)!=15 or collections.Counter(t['role']for t in targets)!=dict(baseline_six_family_interface=12,map_adapter=1,composed_macro=2):raise ValueError('published_legacy_count_drift')
 return targets

def audit(out):
 a=Audit();targets=published_targets(a);versions={t['contentVersion'][7:]for t in targets};by={v:[]for v in versions};excluded=[]
 for p in sorted((REPO/'pcg/results').rglob('record.json')):
  if p.parent.parent.name!='candidates':continue
  if p.parent.name in versions:by[p.parent.name].append(p.parent)
  elif 'creative'not in str(p)and read(p).get('contentVersion')in withdrawn_versions():excluded.append(dict(record=relative(p),contentVersion=read(p)['contentVersion'],reason='original technical withdrawal; not imported or rewritten'))
 before=[a.record(p.parent,'existing_shared')for p in sorted((LIBRARY/'candidates').glob('*/record.json'))];rows=[]
 for target in targets:
  folders=by[target['contentVersion'][7:]]
  if not folders:raise ValueError('missing_legacy_candidate_record:'+target['contentVersion'])
  row=a.record(folders[0],target['role']);a.sha(target['published_document'])
  if path(target['published_document']).read_bytes()!=path(row['document_path']).read_bytes():raise ValueError('published_library_document_bytes_differ')
  for folder in folders[1:]:
   if any(file_sha(folder/n)!=h for n,h in row['files'].items()):raise ValueError('conflicting_same_version_private_copy')
  row.update(target,private_copies=[relative(f)for f in folders]);spec=row['map_specification'];lib=WorkshopLibrary(path(row['source_library']))
  matches=lib.find_multi(spec)if row['multi_route']else lib.find_single_exact(spec)
  if len([m for m in matches if m['record']['contentVersion']==row['contentVersion']])!=1:raise ValueError('original_private_library_retrieval_failed')
  dst=LIBRARY/'candidates'/row['contentVersion'][7:]
  if dst.exists()and any(not(dst/n).exists()or file_sha(dst/n)!=h for n,h in row['files'].items()):raise ValueError('shared_immutable_version_conflict')
  rows.append(row);print(json.dumps(dict(stage='audit',family=row['family'],role=row['role'],contentVersion=row['contentVersion'],ok=True)),flush=True)
 selected=read('pcg/creative-production/novelty-review/selected20-v2.json');main={s['version']for s in selected['selected']};held={s['version']for s in selected.get('pacing_held',[])}
 for row in before:
  row['classification']='selected20_main'if row['contentVersion']in main else'pacing_held'if row['contentVersion']in held else'refund_turnback_extra'if row['family']=='air-refund'else'older_bell_lift_extra'if row['family']=='bell_lift'else'other_existing'
 result=dict(schema='pcg/plains-legacy-inventory-audit/v1',shared_before=before,target_records=rows,target_count=15,published_baseline_modules=12,published_map_adapters=1,published_macros=2,baseline_action_families=sorted({r['family']for r in rows if r['role']=='baseline_six_family_interface'}),dependent_component_documents=list(a.components.values()),excluded_withdrawn_private_records=excluded,global_withdrawn_versions=sorted(withdrawn_versions()),verified_files=[dict(path=p,sha256=h)for p,h in sorted(a.files.items())],verified_file_count=len(a.files),unknown_source_hashes=a.unknown_hashes,restore_actions=[],dependency_gaps=[],new_physics_cases=0,engine_started=False,generator_called=False,source=dict(path=relative(__file__),sha256=file_sha(__file__)))
 write(out/'audit.json',result);return result

def import_records(out):
 d=read(out/'audit.json')
 # Recheck every audited dependency before touching the original shared store.
 for artifact in d['verified_files']:
  if file_sha(path(artifact['path']))!=artifact['sha256']:raise ValueError('audited_dependency_changed')
 for row in d['target_records']:
  dst=LIBRARY/'candidates'/row['contentVersion'][7:]
  if row['contentVersion']in withdrawn_versions():raise ValueError('new_withdrawal_blocks_import')
  if dst.exists()and any(not(dst/n).exists()or file_sha(dst/n)!=h for n,h in row['files'].items()):raise ValueError('shared_candidate_version_conflict')
 rows=[]
 for row in d['target_records']:
  src=path(row['source_directory']);dst=LIBRARY/'candidates'/row['contentVersion'][7:];exists=dst.exists()
  if not exists:
   stage=LIBRARY/'.legacy-inventory-staging'/uuid.uuid4().hex;stage.mkdir(parents=True)
   for n,h in row['files'].items():
    shutil.copy2(src/n,stage/n)
    if file_sha(stage/n)!=h:raise ValueError('staged_copy_drift')
   stage.rename(dst)
  rows.append(dict(contentVersion=row['contentVersion'],role=row['role'],source=row['source_directory'],destination=relative(dst),action='existing_identical'if exists else'copied_original_bytes',files={n:file_sha(dst/n)for n in row['files']}))
 result=dict(schema='pcg/plains-legacy-import/v1',audit_sha256=file_sha(out/'audit.json'),pid=os.getpid(),rows=rows,new_physics_cases=0,shared_before=len(d['shared_before']),shared_after=len(list((LIBRARY/'candidates').glob('*/record.json'))));write(out/'import.json',result);return result

def retrieve(out):
 d=read(out/'audit.json');imp=read(out/'import.json');lib=WorkshopLibrary(LIBRARY);rows=[]
 for row in d['target_records']:
  matches=lib.find_multi(row['map_specification'])if row['multi_route']else lib.find_single_exact(row['map_specification']);hits=[m for m in matches if m['record']['contentVersion']==row['contentVersion']]
  if len(hits)!=1:raise ValueError('shared_exact_retrieval_failed:'+row['contentVersion'])
  dst=path(hits[0]['path']).parent
  if any(file_sha(dst/n)!=h for n,h in row['files'].items()):raise ValueError('shared_bytes_changed')
  rows.append(dict(contentVersion=row['contentVersion'],family=row['family'],role=row['role'],record=hits[0]['path'],method='WorkshopLibrary.find_multi'if row['multi_route']else'WorkshopLibrary.find_single_exact',ok=True));print(json.dumps(dict(stage='retrieve',contentVersion=row['contentVersion'],ok=True)),flush=True)
 result=dict(schema='pcg/plains-legacy-retrieval/v1',count=len(rows),rows=rows,pid=os.getpid(),import_pid=imp['pid'],separate_process=os.getpid()!=imp['pid'],new_physics_cases=0,engine_started=False);write(out/'retrieval.json',result)
 classifications=collections.Counter(r['classification']for r in d['shared_before']);classifications.update(r['role']for r in d['target_records'])
 summary=dict(schema='pcg/plains-workshop-inventory/v1',selected_main20=20,shared_before=imp['shared_before'],shared_after=imp['shared_after'],classifications=dict(classifications),legacy_baseline_versions=12,legacy_baseline_families=6,map_adaptations=1,composed_macros=2,macro_component_dependency_documents=len(d['dependent_component_documents']),additional_action_families_claimed=0,legacy_records_imported=sum(r['action']=='copied_original_bytes'for r in imp['rows']),legacy_records_verified=15,shared_existing_records_audited=len(d['shared_before']),persistent_retrievals=len(rows),separate_process=result['separate_process'],single_route_records=sum(not r['multi_route']for r in d['target_records']),multi_route_records=sum(r['multi_route']for r in d['target_records']),legacy_capability_sets=sorted({tuple(r['capabilities'])for r in d['target_records']}),excluded_withdrawn_private_records=d['excluded_withdrawn_private_records'],restorations=d['restore_actions'],dependency_gaps=d['dependency_gaps'],verified_sha_files=d['verified_file_count'],new_physics_cases=0,engine_started=False,content_versions_rewritten=0,record_case_document_bytes_preserved=True,library='pcg/map_directed/library',limitations='Finite original interfaces and witnesses only. UNKNOWN entry states, return, transforms, assembly and whole-map guarantees remain UNKNOWN. Map adaptation and composed Macro versions do not add action families. No formal production promotion.',records=d['target_records'],macro_dependencies=d['dependent_component_documents'],audit=relative(out/'audit.json'),import_receipt=relative(out/'import.json'),retrieval=relative(out/'retrieval.json'))
 write(out/'inventory.json',summary);return result

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['audit','import','retrieve']);p.add_argument('--out',type=Path,default=OUT);args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 try:
  d={'audit':audit,'import':import_records,'retrieve':retrieve}[args.command](args.out);print(json.dumps(dict(command=args.command,ok=True,new_physics_cases=0)))
 except Exception as e:
  write(args.out/(args.command+'-failure-'+str(time.time_ns())+'.json'),dict(ok=False,command=args.command,error=type(e).__name__+': '+str(e),new_physics_cases=0));raise
if __name__=='__main__':main()
