"""Independent frozen production audit. Reads gzip/JSON; never starts Godot."""
from pathlib import Path
import json,gzip,hashlib,importlib.util,collections,random,re,sys,subprocess,os,datetime,gc,ast,copy
ROOT=Path('/workspace/pcg-research');OUT=ROOT/'evidence/factory-audit';V1=ROOT/'results/factory-production-v1';V2=ROOT/'results/factory-production-v2';fail=[]
def chk(x,m):
 if not x:fail.append(m)
def load(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def word(r):
 out=[];last='free'
 for f in r['frames']:
  state=f['traversal_state']
  if state=='hook_hang'and last!='hook_hang':out.append('hook_hang')
  if state=='hook_contact_kick'and last!='hook_contact_kick':out.append('hook_bounce')
  for e in f['accepted']:
   if e['type']in ('ground_jump','air_jump','anchor_jump','wall_jump'):out.append(e['type'])
   elif e['type']=='shot':out.append('recoil')
   elif e['type']=='traversal'and e['state']=='wall_kick':out.append('wall_jump')
  last=state
 return out
def purpose(c,r):
 expected=[a for a in c['word']if a not in ('wall_contact','wall_separate')]
 if c['family'].startswith('carrier_'):expected=['ground_jump','ground_jump','air_jump'if c['family']=='carrier_double'else 'recoil']
 keys=[];previous='free'
 for f in r['frames']:
  state=f['traversal_state']
  if any(e['type']in ('ground_jump','air_jump','anchor_jump','shot','wall_jump')or(e['type']=='traversal'and e['state']=='wall_kick')for e in f['accepted'])or(state in ('hook_hang','hook_contact_kick')and state!=previous):keys.append(f['frame'])
  previous=state
 continuous=len(keys)>1 and all(not f['grounded']for f in r['frames']if keys[0]<=f['frame']<=keys[-1])
 ride=[f for f in r['frames']if f.get('support_id')=='carrier'and abs(f['axis'])<.01]
 carry=max((f['x']for f in ride),default=0)-min((f['x']for f in ride),default=0);moving=sum(abs(f['platform_velocity'][0])>20 for f in ride)
 matched=word(r)==expected
 good=r['ok']and matched and((len(ride)>=30 and carry>=100 and moving>=20)if c['family'].startswith('carrier_')else continuous)
 return dict(ok=bool(good),word=word(r),word_matches=matched,uninterrupted=continuous,neutral_support_frames=len(ride),neutral_carried_displacement=carry,moving_supported_frames=moving)
def features(r):
 w=word(r);mask=sum(b for a,b in [('wall_jump',1),('air_jump',2),('recoil',4)]if a in w)
 if any(a in w for a in ('hook_hang','hook_bounce','anchor_jump')):mask|=8
 signs=[];last=0;run=0;fs=r['frames']
 for a,b in zip(fs,fs[1:]):
  dx=b['x']-a['x'];s=1 if dx>.4 else -1 if dx<-.4 else 0;run=run+1 if s==last else 1;last=s
  if s and run==3 and(not signs or signs[-1]!=s):signs.append(s)
 active=fs[:max((i for i,f in enumerate(fs)if f.get('accepted')),default=len(fs)-1)+1]
 stationary=sum(sum(abs(v)for v in f.get('real_velocity',[f.get('vx',0),f.get('vy',0)]))<2 for f in active)/max(1,len(active));turns=max(0,len(signs)-1)
 return dict(cell=[mask,digest(w)[:12],min(turns,3),0 if stationary<.05 else 1 if stationary<.25 else 2],source='executed_action_word_and_real_motion',actual_word=w,direction_changes=turns,stationary_fraction=stationary,seconds=len(fs)/60.,skill_mask=mask)
def cost(w):
 return {cap for a,cap in [('wall_jump','wall_climb'),('air_jump','double_jump'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple'),('anchor_jump','grapple')]if a in w},len(w)
binding=load(V1/'source_binding.json');source_bad=[rel for rel,h in binding['source_files'].items()if sha(V1/'source_snapshot'/rel)!=h]
chk(not source_bad,'frozen source bytes');chk(binding['source_manifest_sha256']==digest(binding['source_files']),'source manifest hash');chk('prototype/factory/feedback_cli.py'in binding['source_files'],'CLI source missing')
spec=importlib.util.spec_from_file_location('frozen_factory_quality',V1/'source_snapshot/prototype/factory/core/quality.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
entries=load(V1/'discovery_entries.json');byuid={e['uid']:e for e in entries};compact={}
for e in entries:
 chk(q.candidate_hash(e['case'])==e['uid'],'candidate hash '+e['uid']);chk(q.scenario_hash(e['case'])==e['scenario_sha256'],'scenario hash '+e['uid'])
 for row in e['rows']:compact[(row['evidence']['batch'],row['evidence']['index'])]=row
cat1=load(V1/'catalog.json');cat2=load(V2/'catalog.json');rows1={r['uid']:r for r in cat1['candidates']};rows2={r['uid']:r for r in cat2['candidates']};prefix={uid[:16]:uid for uid in rows1};hold=collections.defaultdict(lambda:collections.defaultdict(list));short=collections.defaultdict(list)
batch_receipts=load(V1/'batches.json');case_total=rawbytes=compressedbytes=trace_compact_checks=0;stages=collections.Counter();raw_success=0;hold_phase_checks=0
for b in batch_receipts:
 packed=V1/b['gzip_path'];data=packed.read_bytes();raw=gzip.decompress(data);rawbytes+=len(raw);compressedbytes+=len(data)
 chk(hashlib.sha256(data).hexdigest()==b['gzip_sha256']and hashlib.sha256(raw).hexdigest()==b['raw_output_sha256']and len(raw)==b['raw_output_bytes'],'compressed original '+b['batch'])
 chk(not (V1/'physics'/(b['batch']+'.output.json')).exists(),'uncompressed duplicate '+b['batch'])
 result= json.loads(raw);rs=result['results'];inp=V1/'physics'/(b['batch']+'.input.json');cs=load(inp)['cases'];ex=load(V1/b['execution'])
 chk(ex['exit_code']==0 and ex['input_sha256']==sha(inp),'execution '+b['batch']);chk([c['id']for c in cs]==[r['id']for r in rs],'ids '+b['batch']);chk(len(cs)<=16,'batch bound')
 chk(result['source_commit']=='12f6cb006d7119598e3235f4ca4f7323e4c9d092','actual game source')
 log=(V1/'physics'/(b['batch']+'.log')).read_text();chk('ERROR:'not in log and 'SCRIPT ERROR'not in log,'engine log '+b['batch'])
 stages[b['stage']]+=len(rs);case_total+=len(rs);raw_success+=sum(r['ok']for r in rs)
 for i,(c,r)in enumerate(zip(cs,rs)):
  p=purpose(c,r)
  if r['ok']:chk(r['hp']==5 and not r['damage_commits']and not r['hazard_contacts']and not r['returns']and r['safe'],'unsafe exit '+r['id'])
  if b['stage'].startswith('discovery'):
   row=compact[(b['batch'],i)];trace_compact_checks+=1
   chk(row['word']==word(r)and row['purpose']==p and row['features']==features(r),'actual behavior '+r['id'])
   chk(row['violation']==q.constraint_distance(c,r,p,word(r)),'actual FI distance '+r['id'])
  elif b['stage']=='holdout':
   uid=prefix[c['id'][:16]];m=re.search(r'-(clean|mild|moderate)-(\d+)$',c['id']);level,trial=m.group(1),int(m.group(2));hold[uid][level].append(dict(purpose=p,safe_stable=r['ok']))
   rng=random.Random(751100+900000+trial*104729+{'clean':0,'mild':1,'moderate':2}[level]*1000003)
   for field in ('moving_platforms','saws'):
    for o in c[field]:chk(o['initial_phase']==rng.random(),'holdout phase stream '+r['id']);hold_phase_checks+=1
   if level!='clean':chk(c['noise']['seed']==rng.randrange(2**30),'holdout noise stream '+r['id'])
  elif b['stage']=='alternatives':
   uid=prefix[c['id'][:16]];a,n=cost(byuid[uid]['best']['word']);z,m=cost(word(r))
   if r['ok']and(z<a or(z==a and m<n)):short[uid].append(dict(word=word(r),alternative=c['alternative'],evidence=dict(batch=b['batch'],index=i,output=b['gzip_path'],raw_output_sha256=b['raw_output_sha256'])))
 del raw,data,result,rs,cs;gc.collect()
summary=load(V1/'summary.json');chk(case_total==1002 and len(batch_receipts)==65,'production totals');chk(len(entries)==82,'unique policies')
archive=q.BehaviorArchive()
for e in entries:
 chk(e['discovery']=={level:q.counts([r for r in e['rows']if r['level']==level])for level in ('clean','mild')},'discovery counts '+e['uid'])
 chk(e['best']==min(e['rows'],key=lambda r:r['violation']['total']),'best actual trace '+e['uid']);chk(e['features']==e['best']['features'],'best descriptor')
 chk(e['quality']==q.discovery_quality(e['discovery'],e['features']),'discovery-only quality '+e['uid'])
 chk(abs(e['violation']-sum(r['violation']['total']for r in e['rows'])/len(e['rows']))<1e-12,'mean distance')
 archive.insert(e)
chk(archive.history==load(V1/'archive_history.json'),'actual archive replacement history');chk(len(archive.feasible)==len(archive.infeasible)==6,'FI archive cells')
# Reconstruct the selected generation-0 parents and exact frozen mutations.
first=q.BehaviorArchive()
for e in entries:
 if not e['case'].get('factory_parent'):first.insert(e)
parents=sorted(first.infeasible.values(),key=lambda e:e['violation'])[:4]+sorted(first.feasible.values(),key=lambda e:-e['quality'])[:4]
tree=ast.parse((V1/'source_snapshot/prototype/factory/core/producer.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='mutate');namespace={'copy':copy,'random':random};exec(compile(ast.Module(body=[node],type_ignores=[]),'frozen_mutate','exec'),namespace)
children={q.candidate_hash(namespace['mutate'](parent,i*2+j)):namespace['mutate'](parent,i*2+j)for i,parent in enumerate(parents)for j in range(2)}
for e in entries:
 if e['case'].get('factory_parent'):chk(e['uid']in children and e['case']==children[e['uid']],'actual selected-parent mutation '+e['uid'])
elite=[];seen=set()
for e in sorted(archive.feasible.values(),key=lambda e:(-e['quality'],e['uid'])):
 if e['scenario_sha256']not in seen:seen.add(e['scenario_sha256']);elite.append(e['uid'])
chk(set(elite)==set(rows1),'pre-holdout finalists')
for uid,row in rows1.items():
 chk(row['features']==byuid[uid]['features'],'holdout altered features')
 chk(row['validation']=={level:q.counts(hold[uid][level])for level in ('clean','mild','moderate')},'holdout admission counts '+uid)
 chk(short[uid]==row['shortcut_witnesses'],'bounded alternatives '+uid)
 chk(row['admission']==q.gate(row['validation'],row['shortcut_witnesses'],row['family']in ('hook_saw','carrier_double','carrier_recoil'),cat1['quality_policy']),'old gate reproduction '+uid)
for cat in (cat1,cat2):chk(digest({k:v for k,v in cat.items()if k!='catalog_sha256'})==cat['catalog_sha256'],'catalog digest')
chk(cat1['physics_binding']['source_manifest_sha256']==binding['source_manifest_sha256'],'catalog source manifest binding')
chk(set(rows1)==set(rows2),'derived changed finalist set')
for uid,r in rows2.items():
 for field in ('uid','scenario_sha256','family','features','calibration','validation','shortcut_witnesses'):chk(r[field]==rows1[uid][field],'derived changed evidence '+uid+'/'+field)
 s=r['validation'];passed=all(s[k]['trials']>=(1 if k=='clean'and r['family']=='thorn_wall'else 12)for k in ('clean','mild','moderate'))and s['clean']['rate']>=.9 and s['mild']['rate']>=.85 and s['moderate']['rate']>=.65 and not r['shortcut_witnesses']
 chk((r['admission']['status']=='awaiting_human_review')==passed,'strict regular gate '+uid)
chk(sum(r['admission']['status']=='awaiting_human_review'for r in rows2.values())==4,'four regular')
reviews1=load(V1/'review_cases.json')['cases'];reviews2=load(V2/'review_cases.json')['cases'];byreview={r['factory_id']:r for r in reviews1}
for c in reviews2:
 old=byreview[c['factory_id']];chk(q.module_hash(c)==c['module_sha256']==old['module_sha256'],'derived module hash')
 chk({k:v for k,v in c.items()if k not in ('title','review_alias')}=={k:v for k,v in old.items()if k not in ('title','review_alias')},'derived gameplay/witness changed')
chk(len(reviews2)==4,'derived reviews four');chk(cat2['human_feedback_count']==cat2['approved_offline_count']==0 and not cat2['formal_game_ready'],'false human approval')
transitions=[]
for e in entries:
 parent=byuid.get(e['case'].get('factory_parent'))
 if parent and parent['discovery']['clean']['rate']<1 and e['discovery']['clean']['rate']==e['discovery']['mild']['rate']==1:transitions.append(dict(parent_uid=parent['uid'],child_uid=e['uid'],family=e['case']['family'],parent_distance=parent['violation'],child_distance=e['violation'],mutation=e['case']['factory_mutation'],child_discovery=e['discovery']))
chk(len(transitions)==1,'actual FI to feasible transition')
protected=load(ROOT/'prototype/godot/source_provenance.json');drift=[p for p,h in protected['files'].items()if sha(ROOT/'prototype/godot'/p)!=h];chk(not drift,'original game drift')
tmp=OUT/'tmp';tmp.mkdir(exist_ok=True);test=subprocess.run([sys.executable,'-m','unittest','discover','-s','prototype/factory/tests','-v'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(tmp)),text=True,capture_output=True);chk(test.returncode==0,'current tests')
receipt=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Independent frozen JSON/gzip/source review and pure Python tests only. No engine/browser run or actual human review.',failures=fail,source=dict(files=len(binding['source_files']),mismatches=source_bad,manifest_sha256=binding['source_manifest_sha256'],includes_cli=True),batches=len(batch_receipts),physics_cases=case_total,stage_cases=dict(stages),raw_output_bytes=rawbytes,gzip_bytes=compressedbytes,compact_trace_checks=trace_compact_checks,holdout_phase_values_checked=hold_phase_checks,archive=dict(feasible_cells=len(archive.feasible),infeasible_cells=len(archive.infeasible),replacement_events=sum(h['replaced']for h in archive.history),history=archive.history,FI_transitions=transitions),derived=dict(unchanged_finalists=len(rows2),regular_reviews=len(reviews2),rework=2,new_physics=0,human_feedback=0,approved_offline=0,all_gameplay_fields_and_witnesses_identical=True),protected=dict(files=len(protected['files']),drift=drift),unittest=dict(exit_code=test.returncode,stdout=test.stdout,stderr=test.stderr))
(OUT/'production-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in receipt.items()if k not in ('archive','unittest')},indent=2));print('FI transitions',transitions)
if fail:raise SystemExit(1)
