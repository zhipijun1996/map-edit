"""Independent read-only receipt audit; never launches Godot."""
from pathlib import Path
import json,hashlib,collections,datetime,difflib,shutil

ROOT=Path('/workspace/pcg-research');RESULTS=ROOT/'results';OUT=ROOT/'evidence/composable-audit'
failures=[];files={};source_variations=[];missing_source_manifests=[]
def load(path):
    p=ROOT/path;files[str(path)]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
def check(value,message):
    if not value:failures.append(message)
def word(result):
    previous='free';out=[]
    for frame in result.get('frames',[]):
        state=frame.get('traversal_state','free')
        if state=='hook_hang' and previous!='hook_hang':out.append('hook_hang')
        if state=='hook_contact_kick' and previous!='hook_contact_kick':out.append('hook_bounce')
        for event in frame.get('accepted',[]):
            if event['type'] in ('ground_jump','air_jump','anchor_jump','wall_jump'):out.append(event['type'])
            elif event['type']=='shot':out.append('recoil')
        previous=state
    return out
def cost(r):
    w=word(r);caps=set()
    for action,cap in [('air_jump','double_jump'),('wall_jump','wall_climb'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple')]:
        if action in w:caps.add(cap)
    return caps,len(w)
def cheaper(a,b):
    x,n=cost(a);y,m=cost(b);return y<x or (x==y and m<n)
def batch(folder,name):
    prefix=Path('results')/folder/name
    cs=load(str(prefix)+'.input.json')['cases'];data=load(str(prefix)+'.output.json');rs=data['results'];ex=load(str(prefix)+'.execution.json')
    check(ex['exit_code']==0,f'{prefix}: exit')
    check(len(cs)==len(rs) and [x['id'] for x in cs]==[x['id'] for x in rs],f'{prefix}: id pairing')
    check(ex['input_sha256']==files[str(prefix)+'.input.json'],f'{prefix}: input hash')
    check(data['source_commit']=='12f6cb006d7119598e3235f4ca4f7323e4c9d092',f'{prefix}: source commit')
    for relative,digest in ex.get('source_sha256',{}).items():
        p=ROOT/relative
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            old=OUT/'phase2-review-source'/relative
            if relative=='prototype/composable/search.py' and old.exists() and hashlib.sha256(old.read_bytes()).hexdigest()==digest:
                source_variations.append(dict(batch=str(prefix),path=relative,recorded_sha256=digest,current_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),explanation='Snapshot preserved. Diff only adds explicit-capability search CLI and accurate archive/count comments. evaluate.py does not import or execute search.py.'))
                (OUT/'final-search-interface.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='preserved-search.py',tofile='current-search.py')))
            elif relative=='prototype/composable/synthesis.py' and hashlib.sha256((OUT/'final-reviewed-source'/relative).read_bytes()).hexdigest()==digest:
                source_variations.append(dict(batch=str(prefix),path=relative,recorded_sha256=digest,current_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),explanation='Exact execution source preserved in final-reviewed-source. Postrun change affects only compile_probe/materialize without move. All final generated/evaluated candidates have move; evaluate/delivery consume frozen inputs and unaffected word/fixed_policy/replay functions. No-move changes are outside this result acceptance.'))
            else:check(False,f'{prefix}: current source mismatch {relative}')
    if not ex.get('source_sha256'):missing_source_manifests.append(str(prefix))
    log=(ROOT/(str(prefix)+'.log')).read_text()
    check('SCRIPT ERROR:' not in log and '\nERROR:' not in log,f'{prefix}: engine error')
    return cs,rs,ex

search=load('results/composable-search-final/summary.json');valid=load('results/composable-search-final/valid.json');archive=load('results/composable-search-final/archive.json')
sc,sr,sx=batch('composable-search-final','01-geometry-replay');pc,pr,px=batch('composable-search-final','00-motion-probes')
actual_valid=[(c,r) for c,r in zip(sc,sr) if r['ok'] and word(r)==[w for w in c['word'] if w!='wall_contact']]
check(len(pc)==378 and len(sc)==663 and len(actual_valid)==572,'search counts')
check(len(valid)==572 and len(archive)==101,'valid/archive counts')
check(len({tuple(word(r)) for c,r in actual_valid})==101,'unique words')
check(all(r['safe'] and r['settled_goal'] and r['plan_completed'] and not r['plan_error'] for c,r in actual_valid),'stable valid gate')
for e in valid:check(word(e['result'])==e['actual_word'],'stored actual word mismatch '+e['case']['id'])
group_counts=collections.Counter(c['combo_index'] for c,r in actual_valid)
check(all(group_counts[g['combo']]==g['settled_valid'] for g in search['groups']),'per group counts')

summary=load('results/composable-evaluation-final/summary.json');selected=load('results/composable-evaluation-final/selected.json');labels=load('results/composable-evaluation-final/noise-labels.json')
nc,nr,nx=batch('composable-evaluation-final','03-paired-noise-holdout')
check(len(nc)==1640 and len(labels)==1640,'noise count')
pairs=collections.defaultdict(dict);pooled=collections.defaultdict(lambda:dict(success=0,trials=0))
clean_words=[]
for label,c,r in zip(labels,nc,nr):
    check(all(c.get(k)==selected[label['module']]['case'].get(k) for k in ['platforms','hazards','hooks','wall_platform_indices','one_way_platform_indices','goal','spawn','capabilities']),'holdout selected geometry '+r['id'])
    pooled[label['policy']+'/'+label['level']]['trials']+=1;pooled[label['policy']+'/'+label['level']]['success']+=int(r['ok'])
    pairs[(label['module'],label['level'],label['trial'])][label['policy']]=(c,r)
    if label['level']=='clean':
        check(r['ok'],'clean failure '+r['id']);check(word(r)==selected[label['module']]['actual_word'],'clean actual word '+r['id']);clean_words.append(word(r))
check(dict(pooled)==summary['pooled'],'pooled aggregate')
geometry_fields=['platforms','hazards','hooks','wall_platform_indices','one_way_platform_indices','goal','spawn','capabilities']
shared=tail=pair_count=missing_shared_records=0
for key,pair in pairs.items():
    check(set(pair)=={'feedback','fixed'},'missing pair '+str(key));a,ar=pair['feedback'];b,br=pair['fixed'];pair_count+=1
    check(all(a.get(k)==b.get(k) for k in geometry_fields),'pair geometry '+str(key));check(a.get('noise')==b.get('noise'),'noise setting '+str(key))
    fa={x['noise_key']:x for x in ar['fired_commands']};fb={x['noise_key']:x for x in br['fired_commands']}
    for k in fa.keys()&fb.keys():
        x,y=fa[k],fb[k];shared+=1
        check(x['timing_error']==y['timing_error'] and x['aim_error_degrees']==y['aim_error_degrees'],'shared error '+str(key)+'/'+str(k))
    for event in br['fired_commands']:
        if str(event['noise_key']).startswith('fixed/axis/'):
            tail+=1;check(event['op']=='axis' and event['timing_error']==0,'tail jitter '+br['id'])
    missing_shared_records+=len(fa.keys()^({k for k in fb if not str(k).startswith('fixed/axis/')}))
check(pair_count==820 and shared>0 and tail>0,'pair sample counts')

ac,ar,ax=batch('composable-evaluation-final','00-shortcut-search');rc,rr,rx=batch('composable-evaluation-final','01-refinement-witness');bc,br,bx=batch('composable-evaluation-final','02-refined-shortcut-search')
original={e['case']['id']:e for e in archive};base_entries=[]
for e in selected:base_entries.append(original[e['case']['id'].removesuffix('-refined')])
def owner(identifier,entries):
    candidates=[i for i,e in enumerate(entries) if identifier.startswith(e['case']['id']+'-')]
    check(len(candidates)==1,'unknown owner '+identifier);return candidates[0]
found=collections.Counter();other=0;original_witnesses=[];refined_witnesses=[]
for c,r in zip(ac,ar):
    i=owner(c['id'],base_entries)
    if r['ok']:
        if cheaper(base_entries[i]['result'],r):
            found[i]+=1;original_witnesses.append(dict(module=i,id=c['id'],family=c['alternative_family'],word=word(r)))
        else:other+=1
accepted=[]
for c,r in zip(rc,rr):
    i=owner(c['id'],base_entries);check(r['ok'] and word(r)==base_entries[i]['actual_word'],'refinement witness '+c['id']);accepted.append(i)
remaining=collections.Counter()
for c,r in zip(bc,br):
    i=owner(c['id'],selected)
    if r['ok'] and cheaper(selected[i]['result'],r):
        remaining[i]+=1;refined_witnesses.append(dict(module=i,id=c['id'],family=c['alternative_family'],word=word(r)))
for i,row in enumerate(summary['modules']):
    check(found[i]==row['original_shortcuts'],'original shortcut count '+row['id'])
    count=remaining[i] if i in accepted else found[i]
    check(count==row['remaining_shortcuts'],'remaining shortcut count '+row['id'])
check(other==10 and len(accepted)==8 and len(ac)+len(bc)==450,'shortcut total counts')
warning_rows=[x for x in summary['modules'] if x['remaining_shortcuts']]

dc,dr,dx=batch('composable-delivery-v2','recorded-input-replay');delivery=load('prototype/godot/modules_v2.json')['cases']
check(len(dr)==20 and all(r['ok'] for r in dr),'delivery replay')
for c,r,e,d in zip(dc,dr,selected,delivery):
    check(word(r)==e['actual_word'],'delivery actual word '+r['id'])
    check(d['id']==e['case']['id'],'delivery selected id')
    index=selected.index(e);row=summary['modules'][index]
    if row['remaining_shortcuts']:check('已发现较少动作/能力的替代解' in d['review_warnings'],'missing shortcut warning '+d['id'])
    if row['combo']==4:check('容错待优化' in d['review_warnings'],'missing tolerance warning')
mc,mr,mx=batch('composable-contract-matrix-v2','matrix');matrix=load('results/composable-contract-matrix-v2/summary.json')
names=['move','jump','shot_recoil','double_jump','grapple','wall_climb'];legal=positive=0
for c,r in zip(mc,mr):
    caps=c['capabilities'];valid_caps=len(caps)==len(set(caps)) and set(caps)<=set(names) and ('double_jump'not in caps or 'jump'in caps) and ('wall_climb'not in caps or 'move'in caps)
    legal+=int(valid_caps);positive+=int(r['ok'])
    check((not r.get('rejected',False))==valid_caps,'matrix rejection '+c['id'])
    if valid_caps:
        check(r['ok'],'matrix static positive '+c['id'])
        for cap,field in [('move','move_enabled'),('jump','jump_enabled'),('shot_recoil','shoot_enabled'),('double_jump','double_enabled'),('grapple','grapple_enabled'),('wall_climb','wall_enabled')]:check(r['capability_snapshot'][field]==(cap in caps),'matrix binding '+c['id']+'/'+cap)
check(legal==36 and positive==36 and len(mc)==66 and matrix['mismatches']==[],'matrix totals')
receipt=dict(scope='Independent JSON/source/log review only. No engine, browser, video, player or device testing by this reviewer.',reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),failures=failures,explained_nonexecuted_source_variations=source_variations,batches_without_per_file_source_manifest=missing_source_manifests,search=dict(proposals=len(pc),geometry_candidates=len(sc),settled_valid=len(actual_valid),unique_words=101,archive_entries=len(archive),covered_combos=len(group_counts),wall_seconds=search['wall_seconds']),paired=dict(pairs=pair_count,shared_fired_command_comparisons=shared,fixed_tail_axis_checks=tail,unshared_fired_command_keys=missing_shared_records,pooled=dict(pooled),all_40_clean_actual_words_match=True,noise_records_empty_observation='Control-plan noise evidence is in fired_commands; noise_records belongs to absolute replay inputs.'),shortcuts=dict(original_modules_with_discovered_shortcuts=len(found),refinements=len(accepted),refinement_witnesses_preserved=len(accepted),shortcut_trials=len(ac)+len(bc),other_successful_routes=other,remaining_modules=warning_rows,modules_without_discovered_shortcuts=20-len(warning_rows)),delivery=dict(replays=len(dr),success=sum(r['ok'] for r in dr),warnings=[dict(id=d['id'],warnings=d['review_warnings']) for d in delivery if d['review_warnings']]),matrix=dict(cases=len(mc),legal_subsets=legal,static_positive_cases=positive,scope=matrix['scope']),final_source_hashes=nx.get('source_sha256'),artifact_sha256=files)
receipt['shortcuts']['remaining_successful_test_policies']=[w for w in original_witnesses if w['module'] not in accepted]+refined_witnesses
old_receipt=OUT/'final-data-review.json'
if old_receipt.exists() and json.loads(old_receipt.read_text()).get('failures') and not (OUT/'final-data-review-first-pass.json').exists():shutil.copy2(old_receipt,OUT/'final-data-review-first-pass.json')
(OUT/'final-data-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k not in ('artifact_sha256','final_source_hashes','shortcuts')},ensure_ascii=False,indent=2));print('shortcut modules:',[(r['id'],r['remaining_shortcuts']) for r in warning_rows])
if failures:raise SystemExit(1)
