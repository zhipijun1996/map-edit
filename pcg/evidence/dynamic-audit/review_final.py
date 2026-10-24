"""Independent final receipt audit; read JSON/source only, never launch Godot."""
from pathlib import Path
import json,hashlib,collections,math,random,gc,datetime,sys
ROOT=Path('/workspace/pcg-research');OUT=ROOT/'evidence/dynamic-audit';failed=[];hashes={};batches=[]
def load(rel):
 p=ROOT/rel;raw=p.read_bytes();hashes[rel]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
def chk(x,m):
 if not x:failed.append(m)
def batch(folder,label):
 p='results/'+folder+'/'+label;cs=load(p+'.input.json')['cases'];data=load(p+'.output.json');rs=data['results'];ex=load(p+'.execution.json')
 chk(ex['exit_code']==0,p+' exit');chk(ex['input_sha256']==hashes[p+'.input.json'],p+' input hash');chk([c['id']for c in cs]==[r['id']for r in rs],p+' paired ids')
 chk(data['source_commit']=='12f6cb006d7119598e3235f4ca4f7323e4c9d092',p+' original source')
 log=(ROOT/(p+'.log')).read_text();chk('ERROR:'not in log and 'SCRIPT ERROR'not in log,p+' log error')
 for c,r in zip(cs,rs):
  if r.get('ok'):
   chk(r['safe']and r['settled_goal']and r['plan_completed']and r['hp']==5 and not r['damage_commits']and not r['hazard_contacts']and not r['returns']and not r['dead'],p+' unsafe success '+r['id'])
   chk(r['goal_stable_frames']>=6,p+' stable count '+r['id'])
   chk(all(not f.get('hazard_contacts')and f['hp']==5 for f in r['frames']),p+' hidden frame damage '+r['id'])
   chk(math.hypot(*r['frames'][-1]['real_velocity'])<=1.000001,p+' final velocity '+r['id'])
 batches.append(dict(prefix=p,cases=len(rs),success=sum(r.get('ok',False)for r in rs),wall_seconds=ex['wall_seconds']))
 return cs,rs
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
 frames=[];last='free'
 for f in r['frames']:
  state=f['traversal_state']
  if any(e['type']in ('ground_jump','air_jump','anchor_jump','shot','wall_jump')or(e['type']=='traversal'and e['state']=='wall_kick')for e in f['accepted'])or(state in ('hook_hang','hook_contact_kick')and state!=last):frames.append(f['frame'])
  last=state
 grounded=[f['frame']for f in r['frames']if len(frames)>1 and frames[0]<=f['frame']<=frames[-1]and f['grounded']]
 continuous=len(frames)>1 and not grounded
 ride=[f for f in r['frames']if f.get('support_id')=='carrier'and abs(f['axis'])<.01]
 displacement=max((f['x']for f in ride),default=0)-min((f['x']for f in ride),default=0)
 moving=sum(abs(f['platform_velocity'][0])>20 for f in ride)
 match=word(r)==expected;carrier=c['family'].startswith('carrier_')
 return dict(ok=r['ok']and match and ((len(ride)>=30 and displacement>=100 and moving>=20)if carrier else continuous),actual_word=word(r),expected_word=expected,uninterrupted=continuous,intermediate_grounded_frames=grounded,neutral_support_frames=len(ride),neutral_carried_displacement=displacement,moving_supported_frames=moving)
def cost(r):
 w=word(r);caps={cap for a,cap in [('wall_jump','wall_climb'),('air_jump','double_jump'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple')]if a in w};return caps,len(w)
def lower(a,b):
 x,n=cost(a);y,m=cost(b);return y<x or(y==x and m<n)

# Calibrated search counts are physical exit counts, deliberately not purpose counts.
ss=load('results/dynamic-search-v3/summary.json');cs,rs=batch('dynamic-search-v3','00-motion');chk(len(cs)==16,'search 16 motion');del cs,rs;gc.collect()
cs,rs=batch('dynamic-search-v3','01-calibration');chk(len(rs)==584 and sum(r['ok']for r in rs)==313,'search calibration totals')
counts={}
for family in ss['groups']:
 rows=[r for c,r in zip(cs,rs)if c['family']==family];counts[family]=dict(trials=len(rows),success=sum(r['ok']for r in rows));chk(all(counts[family][k]==ss['groups'][family][k]for k in ('trials','success')),'search groups '+family)
del cs,rs;gc.collect()

summary=load('results/dynamic-evaluation-v1/summary.json');entries=load('results/dynamic-evaluation-v1/selected.json');labels=load('results/dynamic-evaluation-v1/holdout-labels.json');cs,rs=batch('dynamic-evaluation-v1','00-holdout')
stats=collections.defaultdict(lambda:dict(trials=0,safe_stable=0,purpose_valid=0));per=collections.defaultdict(lambda:dict(trials=0,safe_stable=0,purpose_valid=0));carriers=[];pairs=collections.defaultdict(dict);random_vectors=[]
rng=random.Random(741901);expected_labels=[]
for i,e in enumerate(entries):
 base=e['case'];n=12 if base['moving_platforms']or base['saws']else 1
 def vector():
  return {obj[key]:rng.random()for field,key in [('moving_platforms','platform_id'),('saws','source_id')]for obj in base[field]}
 for t in range(n):
  v=vector();expected_labels.append((i,'clean',t,v))
  if v:expected_labels.append((i,'no_phase_gate',t,v))
 for kind in ('mild','moderate'):
  for t in range(12):expected_labels.append((i,kind,t,vector()))
chk(len(expected_labels)==len(labels)==507,'holdout labels count')
for c,r,l,expected in zip(cs,rs,labels,expected_labels):
 chk((l['module'],l['kind'],l['trial'],l['phase_vector'])==expected,'random stream '+c['id'])
 observed={o[key]:o['initial_phase']for field,key in [('moving_platforms','platform_id'),('saws','source_id')]for o in c[field]};chk(observed==l['phase_vector'],'input phase binding '+c['id'])
 chk(all(v not in (0.,.25,.5,.75)for v in observed.values()),'calibration phase reused '+c['id'])
 chk(sum(len(c[k])for k in ('moving_platforms','saws'))<=1,'multiple dynamic objects unexpectedly claimed')
 q=purpose(c,r);key=(c['family'],l['kind']);pkey=(l['module'],l['kind'])
 for dest,k in ((stats,key),(per,pkey)):
  dest[k]['trials']+=1;dest[k]['safe_stable']+=int(r['ok']);dest[k]['purpose_valid']+=int(q['ok'])
 if l['kind']in ('clean','no_phase_gate'):pairs[(l['module'],l['trial'])][l['kind']]=(c,r)
 if q['ok']and c['family'].startswith('carrier_'):carriers.append(dict(id=c['id'],**q))
for (family,kind),s in stats.items():chk(s==summary['groups'][family][kind],'holdout group '+str((family,kind)))
for i,row in enumerate(summary['per_module']):
 for kind,s in row['stats'].items():chk(per[(i,kind)]==s,'module stats '+row['id']+'/'+kind)
ablation_pairs=0
for key,p in pairs.items():
 if 'no_phase_gate'not in p:continue
 a,ar=p['clean'];b,br=p['no_phase_gate'];ablation_pairs+=1
 for field in ('platforms','thorns','saws','moving_platforms','spawn','goal','capabilities'):chk(a[field]==b[field],'ablation geometry/phase '+str(key))
 expected=json.loads(json.dumps(a['control_plan']))
 for s in expected:
  trigger=s.get('trigger',{})
  if trigger.get('dynamic',{}).get('kind')in ('saw_phase','platform_phase'):trigger.pop('dynamic');trigger['after']=0
 chk(expected==b['control_plan'],'ablation plan '+str(key))
del cs,rs;gc.collect()
cs,rs=batch('dynamic-evaluation-v1','01-alternatives');short=collections.defaultdict(list)
for c,r in zip(cs,rs):
 owner=[i for i,e in enumerate(entries)if c['id'].startswith(e['reference']['case']['id']+'-')];chk(len(owner)==1,'alt owner '+c['id'])
 if r['ok']and lower(entries[owner[0]]['reference']['result'],r):short[owner[0]].append(dict(case_id=c['id'],alternative=c['alternative'],word=word(r)))
chk(len(cs)==196 and len(short)==4,'shortcut counts')
for i,row in enumerate(summary['per_module']):chk(row['shortcuts']==short[i],'shortcut witnesses '+row['id'])
del cs,rs;gc.collect()

# Region constraints are recomputed against actual geometry, followed by raw words.
sys.path.insert(0,str(ROOT/'prototype/dynamic'));from regions import check_candidate
regional=load('results/region-sky-v1/summary.json');spec=load('results/region-sky-v1/region-spec.json');archive=load('results/region-sky-v1/archive.json')
cs,rs=batch('region-sky-v1','00-motion');chk(len(cs)==16,'region proposals');del cs,rs;gc.collect()
cs,rs=batch('region-sky-v1','01-regional-geometry');valid=[];rejected=[]
for c,r in zip(cs,rs):
 chk(not check_candidate(c,spec),'actual regional geometry violation '+c['id']);q=purpose(c,r)
 # Independently inspect this concrete sky contract, without trusting its label.
 chk(not any(c.get(k)for k in ('thorns','saws','moving_platforms','hazards')),'sky forbidden actual mechanism '+c['id'])
 goal=[c['goal'][0]+c['goal'][2]/2,c['goal'][1]+c['goal'][3]/2]
 chk(c['spawn'][1]-goal[1]>=120,'sky actual rise '+c['id'])
 for p in c['platforms']:
  port=any(p[0]+12<=x<=p[0]+p[2]-12 and abs(y+18-p[1])<=2 for x,y in [c['spawn'],goal])
  chk((p[2]<=360 and p[3]<=180)if port else (32<=p[2]<=160 and 32<=p[3]<=160),'sky actual rock/port dimensions '+c['id'])
 walls=[c['platforms'][i]for i in c['wall_platform_indices']];components=[{i}for i in range(len(walls))]
 for i,p in enumerate(walls):
  for j,z in enumerate(walls[:i]):
   if min(p[0]+p[2],z[0]+z[2])<=max(p[0],z[0])+.001:continue
   gap=max(p[1],z[1])-min(p[1]+p[3],z[1]+z[3])
   if gap>.001:chk(gap>=24,'sky actual vertical separation '+c['id'])
   else:
    a=next(g for g in components if i in g);b=next(g for g in components if j in g)
    if a is not b:a.update(b);components.remove(b)
 for group in components:chk(max(walls[i][1]+walls[i][3]for i in group)-min(walls[i][1]for i in group)<=180,'sky disguised contiguous wall '+c['id'])
 (valid if q['ok']else rejected).append(dict(id=c['id'],rise=c['spawn'][1]-(c['goal'][1]+c['goal'][3]/2),platforms=c['platforms'],walls=c['wall_platform_indices'],**q))
chk(len(cs)==10 and len(valid)==8 and len(archive)==8,'regional clean totals');chk(len(rejected)==2 and all(r['intermediate_grounded_frames']for r in rejected),'regional rejected grounding')
mixed=[r for r in valid if {'wall_jump','air_jump','recoil'}<=set(r['actual_word'])and any(a.startswith('hook_')for a in r['actual_word'])];chk(len(mixed)==3,'regional mixed three')
chk({r['id']for r in valid}=={e['case']['id']for e in archive},'regional archive identities')
del cs,rs;gc.collect()
cs,rs=batch('region-sky-v1','02-disturbance');rl=load('results/region-sky-v1/disturbance-labels.json');rstats=collections.defaultdict(lambda:dict(trials=0,safe_stable=0,purpose_valid=0))
for c,r,l in zip(cs,rs,rl):
 q=purpose(c,r);d=rstats[l['level']];d['trials']+=1;d['safe_stable']+=int(r['ok']);d['purpose_valid']+=int(q['ok'])
chk(dict(rstats)==regional['disturbance'],'regional disturbance totals');del cs,rs;gc.collect()

worker=load('results/dynamic-worker-v1/smoke.output.json')['results'];byid={r['id']:r for r in worker}
for name in ('saw-real-return','thorn-real-return'):
 r=byid[name];chk(r['hp']==4 and len(r['damage_commits'])==len(r['returns'])==1 and r['contact_frames']==1,'real ENV negative '+name)
 ret=r['returns'][0];chk(ret['clock_before']==ret['clock_after']and ret['actor_epoch_after']==ret['actor_epoch_before']+1,'real return epoch/clock '+name)
fatal=byid['saw-real-fatal'];chk(fatal['dead']and fatal['hp']==0 and not fatal['returns'],'real fatal')
chk(byid['neutral-carrier-transfer']['frames']==byid['carrier-priority-driver']['frames'],'normal/priority exact scheduling trace')
browser=load('delivery/dynamic-v3/browser-final/browser.json');replays=[e for e in browser['checks']if e.get('action','').startswith('replay_')]if 'checks'in browser else []
if not replays:
 for value in browser.values():
  if isinstance(value,list):replays.extend(e for e in value if isinstance(e,dict)and str(e.get('action','')).startswith('replay_'))
chk(not browser.get('errors')and len(replays)==17 and all(e['state']['safe']and e['state']['finished']and e['state']['stable_frames']>=6 for e in replays),'browser final seventeen')
ui=load('delivery/dynamic-v3/ui-replay-results.json')+load('delivery/dynamic-v3/ui-replay-sky-results.json')
chk(len(ui)==17 and sum(r['compared']for r in ui)==7404 and all(r['compared']==r['frames']and r['safe']and r['hp']==5 and not r['commits']and not r['contact_frames']and r['maximum_position_delta']<1e-6 for r in ui),'UI 7404 frame receipt')
metadata_differences=[dict(id=e['case']['id'],proposal_contract=e['case'].get('capability_contract',{}).get('ids'),declared=e['case']['capabilities'],actual=e['result']['capability_snapshot']['declared'])for e in archive if set(e['case'].get('capability_contract',{}).get('ids',[]))!=set(e['case']['capabilities'])]
provenance=load('prototype/godot/source_provenance.json');drift=[p for p,h in provenance['files'].items()if hashlib.sha256((ROOT/'prototype/godot'/p).read_bytes()).hexdigest()!=h];chk(not drift,'protected original hash drift')
receipt=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Independent read-only JSON/log/source review. No Godot/browser/video execution or human playtest by this reviewer.',failures=failed,batches=batches,dynamic_search_group_counts=counts,dynamic_evaluation_groups={family:{kind:s for (f,kind),s in stats.items()if f==family}for family in summary['groups']},ablation_pairs=ablation_pairs,phase_stream='Exact independent Random(741901) draws match every label/input. One dynamic object per candidate; clean/no-gate pairs share phases; mild/moderate draw new phases and are not paired noise-only comparisons.',purpose_valid_carrier_rollouts=len(carriers),minimum_carrier_support=dict(frames=min(r['neutral_support_frames']for r in carriers),displacement=min(r['neutral_carried_displacement']for r in carriers),moving_frames=min(r['moving_supported_frames']for r in carriers)),shortcuts={str(i):s for i,s in short.items()if s},region=dict(valid=valid,rejected_grounding=rejected,mixed=mixed,disturbance=dict(rstats)),browser=dict(replay_checks=len(replays),errors=browser.get('errors')),protected_original=dict(files=len(provenance['files']),drift=drift),artifact_sha256=hashes)
receipt['ui']=dict(cases=len(ui),compared_frames=sum(r['compared']for r in ui));receipt['regional_proposal_metadata_differences']=metadata_differences
(OUT/'final-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps(dict(failures=failed,batches=batches,ablation_pairs=ablation_pairs,carrier_min=receipt['minimum_carrier_support'],region_valid=len(valid),region_mixed=len(mixed),browser_replays=len(replays)),indent=2))
if failed:raise SystemExit(1)
