"""Review only the new presentation binding/browser/one diagnostic receipt."""
from pathlib import Path
import json,hashlib,gzip,sys,copy,shutil,datetime
ROOT=Path('/workspace/pcg-research');OUT=ROOT/'evidence/factory-audit';WEB=ROOT/'delivery/factory-v1/web-release';TEST=ROOT/'results/factory-feedback-loop-test-v2';fail=[]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def chk(x,m):
 if not x:fail.append(m)
sys.path.insert(0,str(ROOT));from prototype.factory.core.quality import module_hash
from prototype.factory.core.feedback import validate,ingest,repair_job,decide,FeedbackError
catalog=load(WEB/'catalog.json');technical=load(ROOT/'results/factory-production-v2/catalog.json');manifest=load(WEB/'overlay-manifest.json');binding=catalog['presentation_binding']
chk(digest({k:v for k,v in catalog.items()if k!='catalog_sha256'})==catalog['catalog_sha256'],'web catalog hash')
chk(catalog['source_technical_catalog_sha256']==technical['catalog_sha256'],'technical catalog link')
base={k:v for k,v in catalog.items()if k not in ('presentation_binding','source_technical_catalog_sha256','catalog_sha256')};chk(base=={k:v for k,v in technical.items()if k!='catalog_sha256'},'changed technical evidence')
chk(binding['pack_sha256']==manifest['overlay']['sha256']==sha(WEB/manifest['overlay']['pack']),'actual PCK hash')
source_status=[]
for rel,h in binding['source_files'].items():
 p=ROOT/rel;chk(sha(p)==h,'presentation current source '+rel)
 if '/web/'in rel:chk(sha(WEB/Path(rel).name)==h,'deployed webpage source '+rel)
 q=OUT/'incremental-source'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);source_status.append(dict(path=rel,sha256=h))
cases=load(ROOT/'results/factory-production-v2/review_cases.json')['cases'];byuid={c['factory_id']:c for c in cases}
packed_json=json.dumps({'cases':cases},ensure_ascii=False).encode();chk(hashlib.sha256(packed_json).hexdigest()==manifest['files']['modules_v3.json']['sha256'],'PCK cases manifest binding')
for m in catalog['review_modules']:chk(module_hash(byuid[m['uid']])==m['module_sha256'],'module witness unchanged')
browser=load(ROOT/'delivery/factory-v1/browser-release/browser.json');records=browser['records'];replays=[r for r in records if r['action'].startswith('replay_')and r['action']!='replay_is_not_manual_play'];chk(len(replays)==5,'five replay executions')
chk({r['state']['selected']for r in replays}=={0,1,2,3},'four distinct review modules')
chk(all(r['state']['safe']and r['state']['finished']and r['state']['hp']==5 and r['state']['stable_frames']>=6 for r in replays),'successful browser witnesses')
chk(not browser['errors']and not any(e['type']=='error'or'SCRIPT ERROR'in e.get('text','')or e.get('text','').startswith('ERROR:')for e in browser['events']),'browser recorded errors')
chk(browser['feedback_actor']=='synthetic_test'and browser['real_human_reviews']==0,'browser actor provenance')
manual=next(r['state']for r in records if r['action']=='real_manual_D_attempt');chk(manual['mode']=='manual'and manual['hp']==4 and manual['returns']and not manual['safe'],'actual manual input failure observed')
export=load(ROOT/'delivery/factory-v1/browser-release/synthetic-feedback.json');sub=export['submissions'][0]
chk(export['catalog_sha256']==sub['catalog_sha256']==catalog['catalog_sha256'],'latest presentation feedback binding')
chk(sub['source_kind']=='synthetic_test'and all(t['mode']=='manual'for t in sub['manual_attempts']),'synthetic origin and UI manual telemetry')
rejections={}
for name,fn in [('real_import',lambda:validate(sub,catalog))]:
 try:fn();rejections[name]='NOT_REJECTED';chk(False,name+' accepted synthetic')
 except FeedbackError as e:rejections[name]=str(e)
store=load(TEST/'test-only-store.json');job=load(TEST/'test-only-job.json');chk(store['test_only']is True and not store['decisions']and job['test_only']is True and job['source_kind']=='synthetic_test','diagnostic isolation')
chk(store['catalog_sha256']==job['catalog_sha256']==catalog['catalog_sha256'],'diagnostic latest catalog binding')
chk(job==repair_job(store,catalog,diagnostic=True),'diagnostic task actual feedback consumer')
for name,fn in [('real_repair_job',lambda:repair_job(store,catalog)),('curator_retain_test_store',lambda:decide(store,catalog,sub['candidate_uid'],'retain','audit','test-only',human_confirmed=True))]:
 try:fn();rejections[name]='NOT_REJECTED';chk(False,name+' accepted test store')
 except FeedbackError as e:rejections[name]=str(e)
batches=load(TEST/'batches.json');chk(len(batches)==1 and batches[0]['cases']==1,'one diagnostic physical case');b=batches[0];data=(TEST/b['gzip_path']).read_bytes();raw=gzip.decompress(data)
chk(hashlib.sha256(data).hexdigest()==b['gzip_sha256']and hashlib.sha256(raw).hexdigest()==b['raw_output_sha256']and len(raw)==b['raw_output_bytes'],'diagnostic original gzip')
result=json.loads(raw)['results'][0];inp=TEST/'physics'/(b['batch']+'.input.json');child=load(inp)['cases'][0];execution=load(TEST/b['execution'])
chk(execution['exit_code']==0 and execution['input_sha256']==sha(inp),'diagnostic execution')
chk(child['diagnostic_test_only']is True and child['factory_parent']==sub['candidate_uid'],'diagnostic child identity')
parent=byuid[sub['candidate_uid']];task=job['tasks'][0];chk(task['module_sha256']==parent['module_sha256']==module_hash(parent),'repair target actual module hash')
# The task widens the receiving primitive, but leaves goal/control and recorded
# witness invalidation subject to a fresh physical check.
changed=[(a,z)for a,z in zip(parent['platforms'],child['platforms'])if a!=z]
chk(len(changed)==1 and changed[0][1][0]==changed[0][0][0]-16 and changed[0][1][2]==changed[0][0][2]+32,'actual unreadable-landing mutation')
actual=[];last='free';keys=[]
for f in result['frames']:
 s=f['traversal_state'];critical=False
 if s in ('hook_hang','hook_contact_kick')and s!=last:actual.append('hook_hang'if s=='hook_hang'else'hook_bounce');critical=True
 for e in f['accepted']:
  if e['type']in ('ground_jump','air_jump','anchor_jump','wall_jump'):actual.append(e['type']);critical=True
  elif e['type']=='shot':actual.append('recoil');critical=True
  elif e['type']=='traversal'and e['state']=='wall_kick':actual.append('wall_jump');critical=True
 if critical:keys.append(f['frame'])
 last=s
chk(actual==[a for a in child['word']if a not in ('wall_contact','wall_separate')],'diagnostic actual word')
chk(result['ok']and result['hp']==5 and not result['damage_commits']and not result['hazard_contacts']and all(not f['grounded']for f in result['frames']if keys[0]<=f['frame']<=keys[-1]),'diagnostic true purpose')
summary=load(TEST/'summary.json');chk(summary['test_only']and summary['children_revalidated']==summary['children_purpose_pass']==1 and summary['real_human_feedback']==summary['approved_offline']==summary['production_candidates_written']==0,'diagnostic scope counts')
chk(not (TEST/'catalog.json').exists()and not (TEST/'review_cases.json').exists(),'diagnostic accidentally produced production catalog')
for rel in ['prototype/factory/build_review.py','prototype/factory/test_feedback_loop.py','prototype/factory/core/feedback.py']:
 p=ROOT/rel;q=OUT/'incremental-source'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
receipt=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Read-only incremental source/package/browser receipt and one existing diagnostic trace. No Godot/browser execution; no human review.',failures=fail,catalog_sha256=catalog['catalog_sha256'],technical_catalog_sha256=technical['catalog_sha256'],presentation_pack_sha256=binding['pack_sha256'],presentation_sources=source_status,browser=dict(replay_executions=5,distinct_modules=4,manual_input_observed=True,real_human_reviews=0,errors=[]),backend_rejections=rejections,diagnostic=dict(test_only=True,actual_word=actual,tasks=len(job['tasks']),children_revalidated=1,children_purpose_pass=1,real_human_feedback=0,approved_offline=0,production_candidates_written=0),production_technical_catalog_unchanged=True)
(OUT/'incremental-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps(receipt,ensure_ascii=False,indent=2))
if fail:raise SystemExit(1)
