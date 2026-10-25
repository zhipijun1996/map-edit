"""Import frozen selected20 into original CandidateLibrary, byte for byte.

No generator, Engine, simulation, quality-policy changes, or content rewriting.
Each command is an independent process; retrieve calls original WorkshopLibrary.
"""
import argparse,copy,gzip,hashlib,json,os,shutil,sys,time,uuid
from pathlib import Path
from pcg.map_directed.library import CandidateLibrary,verified_document,verify_case_binding
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.quality import gate,counts,module_hash
from pcg.prototype.factory.core.engine import file_sha
REPO=Path(__file__).resolve().parents[3]
DEFAULT_SELECTED=REPO/'pcg/creative-production/novelty-review/selected20.json'
DEFAULT_OUT=REPO/'pcg/results/workshop-creative20-catalog-v1'
DEFAULT_LIBRARY=REPO/'pcg/map_directed/library'
FILES=('record.json','case.json','module.mapnote.json')

def read(p):return json.loads(Path(p).read_text())
def relative(p):return str(Path(p).resolve().relative_to(REPO))
def path(p):
 q=(REPO/p).resolve()
 if not q.is_relative_to(REPO):raise ValueError('outside_repository:'+str(p))
 return q

def write_new(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

class Audit:
 def __init__(self):self.files={};self.gzip_files=0;self.frozen_sources=0
 def check(self,p,expected=None):
  p=path(p);actual=file_sha(p)
  if expected is not None and actual!=expected:raise ValueError('sha_drift:'+relative(p))
  previous=self.files.setdefault(relative(p),actual)
  if previous!=actual:raise ValueError('changed_during_audit:'+relative(p))
  return actual
 def artifact(self,a):return self.check(a['path'],a['sha256'])
 def batches(self,run):
  p=run/'batches.json';self.check(p);rows=read(p);by={}
  for b in rows:
   q=run/b['gzip_path'];self.check(q,b['gzip_sha256']);h=hashlib.sha256();length=0
   with gzip.open(q,'rb')as f:
    while data:=f.read(1024*1024):h.update(data);length+=len(data)
   if h.hexdigest()!=b['raw_output_sha256']or length!=b['raw_output_bytes']:raise ValueError('original_raw_batch_drift:'+relative(q))
   by[b['batch']]=b;self.gzip_files+=1
  return by
 def frozen(self,run):
  p=run/'source_binding.json';self.check(p);binding=read(p)
  for name,sha in binding['source_files'].items():self.check(run/'source_snapshot'/name,sha);self.frozen_sources+=1
  return binding

def scene_for(s,c):
 owner=s['relation_id'].split('/')[0]
 if owner=='occupancy':name='pcg/prototype/creative_batches/occupancy/main_v1.tscn'
 elif owner=='enemy-world':name='pcg/prototype/creative_batches/enemy_world/main_v1.tscn'
 elif owner=='machinery'and s['relation_id'].endswith('carrier-dual-service'):name='pcg/prototype/creative_batches/machinery/dock_main_v17.tscn'
 elif owner=='resource-routes'and any('sequence_offset'in l for l in c.get('latches',[])):name='pcg/prototype/creative_batches/resource_routes/main-sequence-v1.tscn'
 else:name='pcg/prototype/workshop/main.tscn'
 return dict(path=name,sha256=file_sha(path(name)),scope='owner native main scene; presentation only, no new physics validation')

def frozen_selection(selected,audit):
 selected=path(selected);a=read(selected);audit.check(selected);audit.check(a['review'],a['review_sha256'])
 if a['count']!=20 or len(a['selected'])!=20 or len({s['version']for s in a['selected']})!=20:raise ValueError('not_exactly_twenty_unique_frozen_versions')
 return a

def validate(selected,out,library):
 started=time.perf_counter();audit=Audit();selection=frozen_selection(selected,audit);versions={s['version'][7:]for s in selection['selected']};sources={v:[]for v in versions}
 for p in sorted((REPO/'pcg/results').rglob('record.json')):
  if p.parent.name in sources and p.parent.parent.name=='candidates':sources[p.parent.name].append(p.parent)
 rows=[]
 for s in selection['selected']:
  matches=sources[s['version'][7:]]
  if not matches:raise ValueError('missing_private_candidate:'+s['version'])
  signatures=[{n:audit.check(p/n)for n in FILES}for p in matches]
  if any(v!=signatures[0]for v in signatures[1:]):raise ValueError('conflicting_private_version:'+s['version'])
  src=matches[0];rec=read(src/'record.json');c=read(src/'case.json');doc=verified_document(src/'module.mapnote.json');verify_case_binding(c,doc)
  if rec['contentVersion']!=s['version']or doc['generationContract']['contentVersion']!=s['version']:raise ValueError('selection_version_mismatch')
  if rec['id']!=doc['id']or c['id']!=s['case_id']:raise ValueError('selection_case_identity_mismatch')
  if rec['technical_status']!='passed_scoped'or rec['production_admitted']or rec['quality_gate'].get('engineering_tier')!='regular'or rec['quality_gate']['status']!='awaiting_human_review':raise ValueError('not_original_regular_scoped_candidate')
  if s['version']in CandidateLibrary(library).withdrawn:raise ValueError('selected_version_withdrawn')
  audit.check(src/'case.json',rec['case_sha256']);audit.check(src/'module.mapnote.json',rec['document_sha256']);audit.check(s['module'],s['module_sha256'])
  if path(s['module']).read_bytes()!=(src/'module.mapnote.json').read_bytes():raise ValueError('frozen_selection_document_differs_from_library')
  for a in rec['evidence']:audit.artifact(a)
  proofs=[v for v in doc['generationContract']['validations']if v['kind']=='physics'and v['result']=='pass']
  for proof in proofs:
   for artifact in proof['artifacts']:audit.artifact(artifact)
  audit.check(s['case_source'],s['case_source_sha256']);original=next(v for v in read(path(s['case_source']))['cases']if v['id']==s['case_id'])
  if any(c.get(k)!=v for k,v in original.items()):raise ValueError('canonical_case_changed_from_selected_original')
  proposal=s['proposal_source'];audit.check(proposal['implementation_source'],proposal['implementation_source_sha256'])
  if proposal.get('card'):audit.check(proposal['card'],proposal['card_sha256'])
  run=path(s['run']);binding=audit.frozen(run);batches=audit.batches(run);qualities={}
  for stage,name in [('calibration','calibration-evaluations.json'),('holdout','evaluations.json')]:
   q=run/name;audit.check(q);entries=read(q);e=next(e for e in entries if e['case']['id']==c['id'])
   stats={level:counts([r for r in e['rows']if r['level']==level])for level in ['clean','mild','moderate']}
   if stats!=e['stats']:raise ValueError('quality_stats_do_not_match_original_rows')
   dynamic=bool(c.get('moving_platforms')or c.get('enemies')or c.get('saws'));quality=gate(stats,False,dynamic)
   if quality!=e['quality_gate']or quality.get('engineering_tier')!='regular'or quality['status']!='awaiting_human_review':raise ValueError('original_regular_gate_not_passed:'+s['relation_id'])
   for row in e['rows']:
    ev=row['evidence'];b=batches[ev['batch']]
    if ev['raw_output_sha256']!=b['raw_output_sha256']or ev['output']!=b['gzip_path']:raise ValueError('evaluation_original_batch_binding_drift')
   qualities[stage]=dict(file=relative(q),sha256=file_sha(q),stats=stats,quality_gate=quality)
  ev=c['factory_evidence'];b=batches[ev['batch']]
  if ev['raw_output_sha256']!=b['raw_output_sha256']:raise ValueError('canonical_raw_source_drift')
  canonical=read_gzip(run/b['gzip_path'])['results'][ev['index']]
  if not canonical['ok']or canonical['id']!=c['id']:raise ValueError('canonical_physics_witness_not_passed')
  expected=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in canonical['frames']]
  if c['recorded_frames']!=expected:raise ValueError('canonical_recorded_inputs_differ_from_original_witness')
  scene=scene_for(s,c);audit.check(scene['path'],scene['sha256'])
  gc=doc['generationContract'];rows.append(dict(index=s['index'],relation_id=s['relation_id'],name=s['name'],contentVersion=s['version'],id=rec['id'],source_candidate=relative(src),identical_private_copies=[relative(p)for p in matches],file_sha256=signatures[0],canonical_case_id=c['id'],canonical_module_sha256=c['module_sha256'],original_case_source=s['case_source'],original_case_source_sha256=s['case_source_sha256'],run=s['run'],proposal_source=proposal,map_specification=c['map_specification'],scene=scene,physics_runner=binding.get('runner','UNKNOWN'),qualities=qualities,physics_proof_artifacts=sum(len(p['artifacts'])for p in proofs),limitations=dict(assembly='UNKNOWN contracts remain blocked; every new placement needs validation',return_routes=[r.get('return','UNKNOWN')for r in gc['routes']],ports=gc['ports'],transforms=gc['space'].get('transforms','UNKNOWN'),whole_map='UNKNOWN',human_fun='unreviewed',manual_play='unreviewed',production_admitted=False)))
  print(json.dumps(dict(stage='validate',index=s['index'],version=s['version'],ok=True)),flush=True)
 # Detect every destination collision before the first mutation.
 for row in rows:
  dst=path(library)/'candidates'/row['contentVersion'][7:]
  if dst.exists()and any(not(dst/n).is_file()or file_sha(dst/n)!=sha for n,sha in row['file_sha256'].items()):raise ValueError('shared_version_conflict:'+relative(dst))
 result=dict(schema='pcg/creative20-catalog-validation/v1',selected=relative(selected),selected_sha256=file_sha(selected),library=relative(library),rows=rows,verified_files=[dict(path=p,sha256=h)for p,h in sorted(audit.files.items())],verified_file_count=len(audit.files),verified_gzip_batches=audit.gzip_files,verified_frozen_sources=audit.frozen_sources,new_physics_cases=0,generator_called=False,wall_seconds=time.perf_counter()-started,source=dict(path=relative(__file__),sha256=file_sha(__file__)))
 write_new(out/'validation.json',result);return result

def read_gzip(p):
 with gzip.open(p,'rt')as f:return json.load(f)

def import_records(selected,out,library):
 v=read(out/'validation.json')
 if v['selected_sha256']!=file_sha(selected)or v['library']!=relative(library):raise ValueError('validated_plan_identity_changed')
 # All source bytes and existing destination bytes checked before any copy.
 for row in v['rows']:
  src=path(row['source_candidate']);dst=path(library)/'candidates'/row['contentVersion'][7:]
  for n,h in row['file_sha256'].items():
   if file_sha(src/n)!=h:raise ValueError('validated_source_changed')
   if dst.exists()and(not(dst/n).is_file()or file_sha(dst/n)!=h):raise ValueError('shared_version_conflict:'+relative(dst))
 rows=[]
 for row in v['rows']:
  src=path(row['source_candidate']);dst=path(library)/'candidates'/row['contentVersion'][7:];existing=dst.exists()
  if not existing:
   stage=path(library)/'.catalog-staging'/uuid.uuid4().hex;stage.mkdir(parents=True)
   for n in FILES:shutil.copy2(src/n,stage/n)
   for n,h in row['file_sha256'].items():
    if file_sha(stage/n)!=h:raise ValueError('staged_bytes_changed')
   dst.parent.mkdir(parents=True,exist_ok=True);stage.rename(dst)
  rows.append(dict(relation_id=row['relation_id'],contentVersion=row['contentVersion'],source=row['source_candidate'],destination=relative(dst),action='existing_identical'if existing else'copied_original_bytes',file_sha256={n:file_sha(dst/n)for n in FILES}))
 result=dict(schema='pcg/creative20-catalog-import/v1',validation_sha256=file_sha(out/'validation.json'),count=len(rows),new_physics_cases=0,rows=rows,pid=os.getpid());write_new(out/'import.json',result);return result

def retrieve(selected,out,library):
 v=read(out/'validation.json');imp=read(out/'import.json')
 if v['selected_sha256']!=file_sha(selected)or imp['validation_sha256']!=file_sha(out/'validation.json'):raise ValueError('catalog_plan_changed')
 lib=WorkshopLibrary(path(library));rows=[];started=time.perf_counter()
 for row in v['rows']:
  matches=lib.find_single_exact(row['map_specification']);exact=[m for m in matches if m['record']['contentVersion']==row['contentVersion']]
  if len(exact)!=1 or exact[0]['case']['id']!=row['canonical_case_id']:raise ValueError('exact_original_library_retrieval_missing_or_duplicate')
  root=path(exact[0]['path']).parent
  if any(file_sha(root/n)!=h for n,h in row['file_sha256'].items()):raise ValueError('retrieved_original_bytes_changed')
  rows.append(dict(index=row['index'],relation_id=row['relation_id'],contentVersion=row['contentVersion'],record=exact[0]['path'],case_id=exact[0]['case']['id'],exact_matches=len(exact),generator_called=False,new_physics_cases=0));print(json.dumps(dict(stage='retrieve',index=row['index'],ok=True)),flush=True)
 result=dict(schema='pcg/creative20-catalog-retrieval/v1',pid=os.getpid(),import_pid=imp['pid'],separate_process=os.getpid()!=imp['pid'],method='unchanged WorkshopLibrary.find_single_exact',count=len(rows),rows=rows,new_physics_cases=0,generator_called=False,wall_seconds=time.perf_counter()-started);write_new(out/'retrieve.json',result)
 cases=[read(path(library)/'candidates'/row['contentVersion'][7:]/'case.json')for row in v['rows']]
 write_new(out/'review_cases.json',dict(cases=cases))
 write_new(out/'catalog.json',dict(schema='pcg/creative20-unified-candidate-catalog/v1',selected=v['selected'],selected_sha256=v['selected_sha256'],count=20,library=v['library'],candidates=v['rows'],retrieval=relative(out/'retrieve.json'),retrieval_sha256=file_sha(out/'retrieve.json'),original_case_bundle=relative(out/'review_cases.json'),original_case_bundle_sha256=file_sha(out/'review_cases.json'),validation=relative(out/'validation.json'),validation_sha256=file_sha(out/'validation.json'),import_receipt=relative(out/'import.json'),import_sha256=file_sha(out/'import.json'),new_physics_cases=0,production_admitted=False,human_fun='unreviewed',whole_map='UNKNOWN'))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['validate','import','retrieve']);p.add_argument('--selected',type=Path,default=DEFAULT_SELECTED);p.add_argument('--out',type=Path,default=DEFAULT_OUT);p.add_argument('--library',type=Path,default=DEFAULT_LIBRARY);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 try:
  result={'validate':validate,'import':import_records,'retrieve':retrieve}[a.command](a.selected,a.out,a.library);print(json.dumps(dict(command=a.command,ok=True,count=len(result.get('rows',[])),new_physics_cases=0)))
 except Exception as e:
  error=dict(command=a.command,ok=False,error=type(e).__name__+': '+str(e),new_physics_cases=0,pid=os.getpid());target=a.out/(a.command+'-failure-'+str(time.time_ns())+'.json');write_new(target,error);print(json.dumps(error),file=sys.stderr);raise
if __name__=='__main__':main()
