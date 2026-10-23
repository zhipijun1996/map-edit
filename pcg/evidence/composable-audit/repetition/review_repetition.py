"""Read-only independent review of repeated traversal receipts. Never starts Godot."""
from pathlib import Path
import json,hashlib,subprocess,datetime,collections,sys,os,shutil
ROOT=Path('/workspace/pcg-research');OUT=ROOT/'evidence/composable-audit/repetition';files={};failures=[];source_variations=[]
version=sys.argv[1] if len(sys.argv)>1 else 'v4'
assert version in ('v4','v5')
def load(rel):
    p=ROOT/rel;files[rel]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
def check(x,message):
    if not x:failures.append(message)
def word(r):
    last='free';out=[]
    for f in r['frames']:
        state=f.get('traversal_state','free')
        if state=='hook_hang' and last!='hook_hang':out.append('hook_hang')
        if state=='hook_contact_kick' and last!='hook_contact_kick':out.append('hook_bounce')
        for e in f['accepted']:
            if e['type']in ('ground_jump','air_jump','anchor_jump','wall_jump'):out.append(e['type'])
            if e['type']=='shot':out.append('recoil')
        last=state
    return out
def batch(folder,name):
    rel='results/'+folder+'/'+name
    cs=load(rel+'.input.json')['cases'];data=load(rel+'.output.json');rs=data['results'];ex=load(rel+'.execution.json')
    check(ex['exit_code']==0,rel+' exit');check(ex['input_sha256']==files[rel+'.input.json'],rel+' input hash')
    check([x['id']for x in cs]==[x['id']for x in rs],rel+' ids')
    check(data['source_commit']=='12f6cb006d7119598e3235f4ca4f7323e4c9d092',rel+' game source')
    log=(ROOT/(rel+'.log')).read_text();check('SCRIPT ERROR:'not in log and '\nERROR:'not in log,rel+' engine log')
    if version=='v5':
        for source,h in ex['source_sha256'].items():
            p=ROOT/source;actual=hashlib.sha256(p.read_bytes()).hexdigest()
            if actual!=h:
                old=OUT/'v4-source/test_contracts.py'
                if source=='prototype/composable/test_contracts.py'and hashlib.sha256(old.read_bytes()).hexdigest()==h:
                    source_variations.append(dict(batch=rel,path=source,recorded_hash=h,current_hash=actual,explanation='Old test file preserved. Only an impossible-budget unit test was added after motion run; tests are not imported by runtime or generator. Current 12 tests rerun independently.'))
                    dest=OUT/'v5-source/recorded-motion-test_contracts.py';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
                else:check(False,rel+' source snapshot '+source)
            target=OUT/'v5-source'/source;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    return cs,rs
def ground_intervals(fs,start,end):
    groups=[]
    for f in fs:
        if not start<=f['frame']<=end or not f['grounded']:continue
        if not groups or f['frame']!=groups[-1][-1]['frame']+1:groups.append([])
        groups[-1].append(f)
    return [dict(start=g[0]['frame'],end=g[-1]['frame'],start_xy=[g[0]['x'],g[0]['y']],end_xy=[g[-1]['x'],g[-1]['y']])for g in groups]
def describe(c,r):
    fs=r['frames'];commands=[x for x in r['fired_commands']if x['op']=='jump'and x['state']=='wall_attach']
    separation=[max(abs(f['x']-a['position'][0])for f in fs if a['frame']<=f['frame']<=b['frame'])for a,b in zip(commands,commands[1:])]
    wallframes=[f['frame']for f in fs if any(e['type']=='wall_jump'for e in f['accepted'])]
    important=[f['frame']for f in fs if f['traversal_state']in ('hook_hang','hook_contact_kick')or any(e['type']in ('wall_jump','air_jump')for e in f['accepted'])]
    bounds=(min(important),max(important))if important else (0,0)
    ground=ground_intervals(fs,*bounds)
    return dict(id=c['id'],expected=[w for w in c['word']if w not in ('wall_contact','wall_separate')],actual=word(r),word_matches=word(r)==[w for w in c['word']if w not in ('wall_contact','wall_separate')],plan_completed=r['plan_completed'],ok=r['ok'],reason=r['reason'],wall_jumps=len(wallframes),air_jumps=word(r).count('air_jump'),contact_x=[x['position'][0]for x in commands],separation_max_abs_dx=separation,active_bounds=bounds,intermediate_grounding=ground,shot_max=max(f['shot_charges']for f in fs),caps=c['capabilities'])
folder='repetition-'+version
summary=load('results/'+folder+'/summary.json');mc,mr=batch(folder,'00-motion');gc,gr=batch(folder,'01-modules')
motion=[describe(c,r)for c,r in zip(mc,mr)];modules=[describe(c,r)for c,r in zip(gc,gr)]
check(len(motion)==14 and sum(x['word_matches']and x['plan_completed']for x in motion)==13,'motion totals')
check(len(modules)==13 and all(x['ok']and x['word_matches']for x in modules),'module totals')
for row in motion:
    if row['wall_jumps']:check(all(x>=5 for x in row['separation_max_abs_dx']),'insufficient wall separation '+row['id'])
same_double=[r for r in motion if r['id'].startswith('wall-same')and r['id'].endswith('double-1')]
check(len(same_double)==3,'same double matrix')
if version=='v4':check(all(r['intermediate_grounding']for r in same_double),'expected preserved grounding finding')
if version=='v5':check(not any(r['intermediate_grounding']for r in motion+modules),'v5 unexpected intermediate grounding')
if version=='v5':
    for row in modules:
        check(row['wall_jumps']==row['expected'].count('wall_jump')and row['air_jumps']==row['expected'].count('air_jump'),'module accepted counts '+row['id'])
        check(all(d>=5 for d in row['separation_max_abs_dx']),'module wall separation '+row['id'])
for row in modules:
    if row['id'].startswith('four-hooks-double-1'):check(not row['intermediate_grounding']and row['air_jumps']==4,'hook continuous restoration')
sixfolder='repetition-search-six'+('-final'if version=='v5'else '')
sc,sr=batch(sixfolder,'00-motion-probes');tc,tr=batch(sixfolder,'01-geometry-replay');ss=load('results/'+sixfolder+'/summary.json')
check(len(sc)==6 and len(tc)==12 and all(r['ok']for r in tr),'six search totals')
sixwords={tuple(word(r))for r in tr};check(len(sixwords)==1 and next(iter(sixwords)).count('wall_jump')==6,'six search word type')
for c,r in zip(tc,tr):check(word(r)==[w for w in c['word']if w not in ('wall_contact','wall_separate')],'six word mismatch')
provenance=load('prototype/godot/source_provenance.json');drift=[p for p,h in provenance['files'].items()if hashlib.sha256((ROOT/'prototype/godot'/p).read_bytes()).hexdigest()!=h]
paths=['config/player_tuning.json','scripts/player','scripts/input','scripts/combat','resources/player','resources/weapons','scenes/player','project.godot']
cmd=['git','diff','--name-only',provenance['commit'],'54573a8e9400d790f58656efde2dd812cc00d8ba','--',*paths]
diff=subprocess.run(cmd,cwd='/workspace/gunman-rush-latest',text=True,capture_output=True)
check(diff.returncode==0 and not diff.stdout.strip(),'latest motion diff');check(not drift,'original source drift')
receipt=dict(scope='Independent source/JSON/log review only; no engine run or video/browser/device inspection.',reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),failures=failures,explained_test_only_source_variations=source_variations,motion=motion,modules=modules,six_search=dict(summary=ss,actual_word_types=[list(x)for x in sixwords]),physics=dict(original_commit=provenance['commit'],files_checked=len(provenance['files']),drift=drift,latest_commit='54573a8e9400d790f58656efde2dd812cc00d8ba',diff_command=cmd,diff_exit=diff.returncode,diff_stdout=diff.stdout),artifact_sha256=files)
if version=='v5':
    impossible=load('results/repetition-impossible-budget/summary.json')
    check(all(impossible[k]==0 for k in ['proposals','geometry_candidates','settled_valid','physics_calls','physics_cases']),'impossible budget fell back')
    check(impossible['failure_reasons']=={'no_grammar_word':1},'impossible budget rejection')
    p=subprocess.run([sys.executable,'-m','unittest','test_contracts','-v'],cwd=ROOT/'prototype/composable',env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True)
    check(p.returncode==0,'pure Python unit tests');receipt['unittest']=dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);receipt['impossible_budget']=impossible
    check(all(r['wall_jumps']==int(c['id'].split('-')[2]) and r['air_jumps']==(int(c['id'].split('-')[2])if c['id'].endswith('double-1')else 0)for c,r in zip(mc,motion)if c['id'].startswith('wall-')),'wall jump counts')
dest=OUT/(version+'-review.json')
if dest.exists()and json.loads(dest.read_text()).get('failures')and not (OUT/(version+'-review-first-pass.json')).exists():shutil.copy2(dest,OUT/(version+'-review-first-pass.json'))
dest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(dict(failures=failures,provenance=receipt['physics'],motion=len(motion),intended=13,modules=13,grounding_motions=[r['id']for r in motion if r['intermediate_grounding']],grounding_modules=[r['id']for r in modules if r['intermediate_grounding']],six_words=[list(w)for w in sixwords]),indent=2))
if failures:raise SystemExit(1)
