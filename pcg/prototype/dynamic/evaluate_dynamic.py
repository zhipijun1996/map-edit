"""Holdout phases, command disturbances and bounded mechanical counterexamples.
No count, hash, bot success or absent counterexample establishes human fun.
"""
import copy,json,random,collections,argparse,time
from simulator import ROOT,Simulator
from generators import actual_word,compile_probe,command,gated,dynamic

def critical_frames(r):
 out=[];previous='free'
 for f in r.get('frames',[]):
  state=f['traversal_state']
  if any(e['type'] in ('ground_jump','air_jump','anchor_jump','shot','wall_jump') or (e['type']=='traversal' and e['state']=='wall_kick') for e in f['accepted']) or (state in ('hook_hang','hook_contact_kick') and state!=previous):out.append(f['frame'])
  previous=state
 return out

def purpose(case,r):
 w=actual_word(r)
 expected=tuple(x for x in case['word'] if x not in ('wall_contact','wall_separate'))
 if case['family'].startswith('carrier_'):expected=('ground_jump','ground_jump','air_jump' if case['family']=='carrier_double' else 'recoil')
 keys=critical_frames(r);uninterrupted=len(keys)>1 and all(not f['grounded'] for f in r['frames'] if keys[0]<=f['frame']<=keys[-1])
 ride=[f for f in r.get('frames',[]) if f.get('support_id')=='carrier' and abs(f['axis'])<.01]
 carry=max((f['x'] for f in ride),default=0)-min((f['x'] for f in ride),default=0)
 moving=sum(abs(f.get('platform_velocity',[0,0])[0])>20 for f in ride)
 matched=w==expected
 good=r['ok'] and matched and ((len(ride)>=30 and carry>=100 and moving>=20) if case['family'].startswith('carrier_') else uninterrupted)
 return dict(ok=bool(good),word=list(w),word_matches=matched,uninterrupted=uninterrupted,neutral_support_frames=len(ride),neutral_carried_displacement=carry,moving_supported_frames=moving)

def pick_entries(source,per_family=3):
 cases=json.load(open(source/'01-calibration.input.json'))['cases'];rs=json.load(open(source/'01-calibration.output.json'))['results'];raw=json.load(open(source/'candidate-policies.json'))
 by_prefix=collections.defaultdict(list)
 for c,r in zip(cases,rs):by_prefix[c['id'].rsplit('-phase',1)[0]].append((c,r))
 archive={}
 for c in raw:
  rows=by_prefix[c['id']];valid=[(cc,r) for cc,r in rows if purpose(cc,r)['ok']]
  if not valid:continue
  key=c['id'].split('-s')[0] if c['family']=='hook_saw' else c['id']
  e=dict(case=c,calibration_success=len(valid),calibration_trials=len(rows),reference=dict(case=valid[0][0],result=valid[0][1]))
  if key not in archive or len(valid)>archive[key]['calibration_success']:archive[key]=e
 selected=[]
 for family in ('thorn_wall','hook_saw','carrier_double','carrier_recoil'):
  rows=[e for e in archive.values() if e['case']['family']==family]
  rows.sort(key=lambda e:(-e['calibration_success']/e['calibration_trials'],e['case']['id']))
  selected+=rows[:per_family]
 return selected,archive

def randomized_phase(case,rng):
 c=copy.deepcopy(case);phases={}
 for kind,key in [('moving_platforms','platform_id'),('saws','source_id')]:
  for obj in c[kind]:obj['initial_phase']=rng.random();phases[obj[key]]=obj['initial_phase']
 return c,phases

def phase_ablation(case):
 c=copy.deepcopy(case)
 for step in c['control_plan']:
  trigger=step.get('trigger',{});query=trigger.get('dynamic',{})
  if query.get('kind') in ('saw_phase','platform_phase'):
   trigger.pop('dynamic');trigger['after']=0
 return c

def lower_cost(reference,r):
 def cost(w):
  caps=set()
  for action,cap in [('wall_jump','wall_climb'),('air_jump','double_jump'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple')]:
   if action in w:caps.add(cap)
  return caps,len(w)
 a,n=cost(actual_word(reference));b,m=cost(actual_word(r));return b<a or (a==b and m<n)

def alternatives(case):
 out=[];gx=case['goal'][0]+case['goal'][2]/2;sign=1 if gx>case['spawn'][0] else -1;caps=case['capabilities']
 def add(plan,label):
  c=copy.deepcopy(case);c['id']+='-alt-'+label;c['control_plan']=plan+[command('settle',after=5,target_x=gx,deadband=6)];c['alternative']=label;out.append(c)
 for hold in (8,16,26):
  for kind in ('walk','jump','double','recoil','jump_recoil','single_hook'):
   if kind=='double' and 'double_jump'not in caps:continue
   if 'recoil'in kind and 'shot_recoil'not in caps:continue
   if kind=='single_hook' and ('grapple'not in caps or not case['hooks']):continue
   plan=[command('axis',value=sign)]
   if kind in ('jump','double','jump_recoil','single_hook'):plan += [command('jump',after=5),command('jump_release',after=hold)]
   if kind=='double':plan += [gated('jump','airborne',min_after=4),command('jump_release',after=hold)]
   if 'recoil'in kind:plan.append(command('shoot',after=6,direction=[-sign*.8,.6]))
   if kind=='single_hook':
    h=case['hooks'][0];plan += [command('grapple',after=5,aim_target=[h['x'],h['y']]),gated('jump','hook_hang',min_after=3,timeout=90),command('jump_release',after=hold)]
   add(plan,kind+'-'+str(hold))
 if 'wall_climb'in caps:
  n=case['word'].count('wall_jump')
  word=['wall_contact','wall_jump']+['wall_separate','wall_contact','wall_jump']*max(0,n-1)
  for seed in (1501,1502,1503):add(compile_probe(word,caps,seed,case.get('synthesis',{}).get('wall_layout','same'))['control_plan'],'walls_no_air_'+str(seed))
 if case['family'].startswith('carrier_'):
  for hold in (8,16,26):
   plan=copy.deepcopy(case['control_plan']);k=next(i for i,s in enumerate(plan) if s.get('trigger',{}).get('dynamic',{}).get('kind')=='on_platform')
   # Retain actual boarding/coasting, then take a full ordinary jump at departure.
   leave=plan[:k+1]+[command('axis',value=0),dynamic('wait','platform_phase',query=dict(id='carrier',window=[.5,.525]),timeout=800),command('axis',value=1),command('jump'),command('jump_release',after=hold)]
   add(leave,'ride_then_plain_jump_'+str(hold))
 # Changed control policies are explicitly weaker probes, not complete replanning.
 for i,step in enumerate(case['control_plan']):
  if step['op']not in ('jump','shoot','grapple'):continue
  c=copy.deepcopy(case);c['id']+='-omit-'+str(i);c['control_plan'][i]['op']='wait';c['alternative']='omit_'+step['op'];out.append(c)
 return out

def run(args):
 source=ROOT/'results'/args.source;sim=Simulator(ROOT/'results'/args.name);start=time.perf_counter();entries,archive=pick_entries(source,args.per_family)
 rng=random.Random(args.seed);cases=[];labels=[]
 for i,e in enumerate(entries):
  base=e['case'];count=args.phases if base['moving_platforms'] or base['saws'] else 1
  for p in range(count):
   c,vector=randomized_phase(base,rng);c['id']+=f'-holdout-{p}';cases.append(c);labels.append(dict(module=i,kind='clean',trial=p,phase_vector=vector))
   if vector:
    ab=phase_ablation(c);ab['id']+='-no_phase_gate';cases.append(ab);labels.append(dict(module=i,kind='no_phase_gate',trial=p,phase_vector=vector))
  for level,frames,angle in [('mild',1,2),('moderate',3,6)]:
   for trial in range(args.trials):
    c,vector=randomized_phase(base,rng);c['id']+=f'-{level}-{trial}';c['noise']=dict(seed=args.seed+trial,timing_frames=frames,aim_degrees=angle);cases.append(c);labels.append(dict(module=i,kind=level,trial=trial,phase_vector=vector))
 rs=sim.run(cases,'00-holdout');alts=[];owners=[]
 for i,e in enumerate(entries):
  cs=alternatives(e['reference']['case']);alts+=cs;owners += [i]*len(cs)
 ars=sim.run(alts,'01-alternatives');shortcuts=collections.defaultdict(list)
 for i,c,r in zip(owners,alts,ars):
  if r['ok'] and lower_cost(entries[i]['reference']['result'],r):shortcuts[i].append(dict(case_id=c['id'],alternative=c['alternative'],word=list(actual_word(r))))
 groups={};per=[]
 for family in ('thorn_wall','hook_saw','carrier_double','carrier_recoil'):
  g={}
  for kind in ('clean','no_phase_gate','mild','moderate'):
   rows=[(entries[l['module']]['case'],r) for l,r in zip(labels,rs) if l['kind']==kind and entries[l['module']]['case']['family']==family]
   g[kind]=dict(trials=len(rows),safe_stable=sum(r['ok'] for c,r in rows),purpose_valid=sum(purpose(c,r)['ok'] for c,r in rows))
  groups[family]=g
 for i,e in enumerate(entries):
  stats={}
  for kind in ('clean','no_phase_gate','mild','moderate'):
   rows=[r for l,r in zip(labels,rs) if l['module']==i and l['kind']==kind];stats[kind]=dict(trials=len(rows),safe_stable=sum(r['ok'] for r in rows),purpose_valid=sum(purpose(e['case'],r)['ok'] for r in rows))
  per.append(dict(id=e['case']['id'],family=e['case']['family'],actual_word=list(actual_word(e['reference']['result'])),stats=stats,shortcuts=shortcuts[i],calibration=e['calibration_success'],calibration_trials=e['calibration_trials']))
 summary=dict(schema='pcg/dynamic-evaluation/v3',source=args.source,seed=args.seed,modules=len(entries),groups=groups,per_module=per,alternative_trials=len(alts),modules_with_discovered_lower_cost_route=sum(bool(v) for v in shortcuts.values()),physics_cases=sim.cases,wall_seconds=time.perf_counter()-start,limits=['Phases and command disturbances apply to an automated observable-state policy, not human success.','No-phase-gate is a specific policy ablation, not an optimal player baseline.','Bounded alternatives can refute necessity; failure to find a route never proves necessity.','Actual event/ride checks are technical evidence, not human fun or production-region approval.'])
 (sim.out/'summary.json').write_text(json.dumps(summary,indent=2));(sim.out/'selected.json').write_text(json.dumps(entries));(sim.out/'holdout-labels.json').write_text(json.dumps(labels));(sim.out/'purpose-archive.json').write_text(json.dumps(list(archive.values())));print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',default='dynamic-search-v3');p.add_argument('--name',default='dynamic-evaluation-v1');p.add_argument('--seed',type=int,default=741901);p.add_argument('--per-family',type=int,default=3);p.add_argument('--phases',type=int,default=12);p.add_argument('--trials',type=int,default=12);run(p.parse_args())
