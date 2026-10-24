"""Finite-budget offline synthesis, FI-style behavior search and final gates."""
import argparse,collections,copy,json,random,sys,time
from pathlib import Path
from .engine import ROOT,Engine
from .quality import POLICY,BehaviorArchive,candidate_hash,scenario_hash,module_hash,digest,descriptor,constraint_distance,counts,discovery_quality,gate,rate
from generators import motion_proposals,turn_into_modules,saw_variants,ferry_candidates,actual_word,Grammar,compile_probe,ports,Registry
from evaluate_dynamic import purpose,alternatives,lower_cost,randomized_phase
from regions import prepare_regions,filter_families,transform_candidate,check_candidate,RegionSpecError

def compact(case,result,evidence):
 p=purpose(case,result);word=list(actual_word(result))
 return dict(id=result['id'],safe_stable=bool(result['ok']),purpose=p,reason=result['reason'],hp=result.get('hp'),hazard_contact_frames=result.get('contact_frames',0),damage_commits=len(result.get('damage_commits',[])),word=word,features=descriptor(result.get('frames',[]),word),violation=constraint_distance(case,result,p,word),ticks=result.get('ticks',0),evidence=evidence)

def instantiate(case,seed,level,trial):
 # Common random numbers across candidate revisions; independent objects receive
 # independent phase draws. Holdout seeds never enter discovery.
 rng=random.Random(seed+trial*104729+{'clean':0,'mild':1,'moderate':2}[level]*1000003)
 c,vector=randomized_phase(case,rng);c['id']+=f'-{level}-{trial}'
 if level!='clean':c['noise']=dict(seed=rng.randrange(2**30),timing_frames=1 if level=='mild' else 3,aim_degrees=2 if level=='mild' else 6)
 c['trace_all']=False
 return c,dict(level=level,trial=trial,phase_vector=vector)

def evaluate(engine,cases,seed,trials,stage,levels=('clean','mild')):
 expanded=[];owners={};entries={}
 for base in cases:
  uid=candidate_hash(base);entries[uid]=dict(uid=uid,case=base,scenario_sha256=scenario_hash(base),rows=[],witness=None)
  for level in levels:
   n=trials if level!='clean'or base.get('moving_platforms')or base.get('saws')else 1
   for trial in range(n):
    c,label=instantiate(base,seed,level,trial);c['id']=uid[:16]+'-'+c['id'];expanded.append(c);owners[c['id']]=(uid,label)
 for case,result,evidence in engine.run(expanded,stage):
  uid,label=owners[case['id']];e=entries[uid];r=compact(case,result,evidence);r.update(label);e['rows'].append(r)
  if label['level']=='clean'and r['purpose']['ok']and e['witness']is None:
   e['witness']=dict(case=copy.deepcopy(case),recorded_frames=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in result['frames']],evidence=evidence)
  # Best real trace also preserves progress for infeasible candidates.
  if 'best'in e and r['violation']['total']>=e['best']['violation']['total']:continue
  e['best']=r
 for e in entries.values():
  e['discovery']={level:counts([r for r in e['rows']if r['level']==level])for level in levels}
  e['features']=e['best']['features'];e['violation']=sum(r['violation']['total']for r in e['rows'])/max(1,len(e['rows']))
  e['quality']=discovery_quality(e['discovery'],e['features'])if 'mild'in levels else rate(e['discovery']['clean'])
 return list(entries.values())

def mutate(parent,serial,target=None):
 """Correlated geometry/control changes, always revalidated by real physics."""
 c=copy.deepcopy(parent['case']);rng=random.Random(900000+serial)
 for key in ('recorded_frames','module_sha256','factory_id','factory_evidence','review_alias','title','review_warnings','admission_status','validation_summary'):c.pop(key,None)
 if c.get('region_profile'):c['region_profile']['validation_status']='requires_real_physics_revalidation'
 c['id']+=f'-child{serial}';c['factory_parent']=parent['uid'];c['factory_mutation']=''
 receiver=min(range(len(c['platforms'])),key=lambda i:abs(c['platforms'][i][1]-(c['goal'][1]+42))+abs((c['platforms'][i][0]+c['platforms'][i][2]/2)-(c['goal'][0]+c['goal'][2]/2)))
 if target=='excessive_wait'and c.get('saws'):
  for saw in c['saws']:saw['period']*=.85
  c['factory_mutation']='shorten_saw_period_15_percent'
 elif target=='unreadable_landing':
  p=c['platforms'][receiver];p[0]-=16;p[2]+=32
  c['factory_mutation']='widen_receiving_surface_32'
 elif c['family'].startswith('carrier_'):
  dx=rng.choice((-32,-16,16,32));c['platforms'][receiver][0]+=dx;c['goal'][0]+=dx;c['exit_port'][0]+=dx
  for step in c['control_plan']:
   if step['op']=='settle':step['target_x']+=dx
  c['factory_mutation']='shift_receiver_and_goal_'+str(dx)
 elif c.get('saws'):
  for step in c['control_plan']:
   q=step.get('trigger',{}).get('dynamic',{})
   if q.get('kind')=='saw_phase':
    lo=(q['window'][0]+rng.choice((-.125,.125,.25)))%1;q['window']=[lo,(lo+.075)%1]
  c['factory_mutation']='change_visible_saw_departure_window'
 else:
  options=[s for s in c['control_plan']if s['op']=='jump_release'and s.get('trigger',{}).get('after',0)>2]
  if options:
   step=rng.choice(options);step['trigger']['after']+=rng.choice((-2,2));c['factory_mutation']='change_release_timing_2_frames'
  else:c['factory_mutation']='no_supported_mutation'
 return c

def propose(engine,args,spec):
 proposals=[];rejects=[]
 caps=spec['available_capabilities']if spec else None
 families=filter_families(spec,['thorn_wall','hook_saw','sky_ascent'])if spec else None
 for offset in range(args.seeds):
  seed=args.seed+offset
  ps=motion_proposals(seed,args.words,families=families,available_capabilities=caps)
  if spec and 'sky_ascent'in families:
   ws=Grammar(caps).derive(seed+31,limit=500,max_depth=12,min_actions=6)
   ws=[w for w in ws if 'wall_jump'in w and 'air_jump'in w and'recoil'in w and any(a.startswith('hook_')for a in w)]
   for i,w in enumerate(ws[:args.words*2]):
    c=ports(compile_probe(w,caps,seed+500+i,wall_layout='same'),probe=True);c.update(id=f'sky-mixed-p{i}',family='sky_ascent',max_frames=1200,trace_all=True);ps.append(c)
  for p in ps:p['id']=f'seed{seed}-'+p['id']
  proposals+=ps
 modules=[]
 for p,r,evidence in engine.run(proposals,'motion'):
  cs,rs=turn_into_modules([p],[r]);rejects+=rs
  for c in cs:
   frames=c.pop('reference_frames')
   if spec:
    try:
     c=transform_candidate(c,frames,spec);v=check_candidate(c,spec)
     if v:rejects.append(dict(id=c['id'],reason='region_constraints',violations=v));continue
     c['family']='sky_ascent';modules.append(c)
    except RegionSpecError as e:rejects.append(dict(id=c['id'],reason='region_transform',detail=str(e)))
   elif c['family']=='hook_saw':
    c['reference_frames']=frames;modules+=saw_variants(c,periods=(2.4,))
   else:modules.append(c)
 if not spec:
  for offset in range(args.seeds):
   for c in ferry_candidates(args.seed+700+offset,args.ferries):c['id']=f'seed{args.seed+offset}-'+c['id'];modules.append(c)
 return modules,rejects,len(proposals)

def run(args):
 start=time.perf_counter()
 if min(args.seeds,args.words,args.calibration,args.validation,args.batch_size)<1 or args.rounds<0:raise ValueError('invalid search budget')
 spec=prepare_regions(args.region,args.capabilities.split(','))if args.region else None
 engine=Engine(ROOT/'results'/args.name,args.batch_size);out=engine.out;archive=BehaviorArchive()
 if spec:(out/'region_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
 policy=copy.deepcopy(POLICY)
 (out/'quality_policy.json').write_text(json.dumps(policy,indent=2))
 candidates,rejections,proposal_count=propose(engine,args,spec)
 repair_receipt=[]
 if args.repair_job:
  if not args.repair_catalog or not args.repair_cases:raise ValueError('repair requires its source catalog and cases')
  job=json.loads(Path(args.repair_job).read_text());source=json.loads(Path(args.repair_catalog).read_text())
  from .feedback import check_catalog
  check_catalog(source)
  if job.get('test_only')is not False or job.get('schema')!='pcg/factory-repair-job/v1'or job.get('catalog_sha256')!=source['catalog_sha256']:raise ValueError('stale_or_test_repair_job')
  if source['physics_binding']['engine_sha256']!=engine.binding['engine_sha256']or source['physics_binding']['source_index_sha256']!=engine.binding['source_index_sha256']:raise ValueError('repair_physics_binding_changed')
  originals={c['factory_id']:c for c in json.loads(Path(args.repair_cases).read_text())['cases']}
  for i,task in enumerate(job['tasks']):
   base=originals.get(task['candidate_uid'])
   if not base or module_hash(base)!=task['module_sha256']:raise ValueError('stale_repair_module')
   if task['target']not in ('unreadable_landing','excessive_wait'):
    repair_receipt.append(dict(task=task,status='manual_design_review_required'));continue
   child=mutate(dict(case=base,uid=task['candidate_uid']),10000+i,target=task['target'])
   if spec and check_candidate(child,spec):repair_receipt.append(dict(task=task,status='region_constraints_rejected'));continue
   candidates.append(child);repair_receipt.append(dict(task=task,status='child_sent_to_full_validation',child_uid=candidate_hash(child)))
 (out/'repair_receipt.json').write_text(json.dumps(repair_receipt,ensure_ascii=False,indent=2))
 all_entries={};rounds=[];seen=set()
 pending=candidates
 for generation in range(args.rounds+1):
  pending=[c for c in pending if candidate_hash(c)not in seen]
  for c in pending:seen.add(candidate_hash(c))
  entries=evaluate(engine,pending,args.seed+200000,args.calibration,f'discovery{generation}')
  for e in entries:archive.insert(e);all_entries[e['uid']]=e
  rounds.append(dict(generation=generation,evaluated=len(entries),feasible_cells=len(archive.feasible),infeasible_cells=len(archive.infeasible)))
  parents=sorted(archive.infeasible.values(),key=lambda e:e['violation'])[:4]+sorted(archive.feasible.values(),key=lambda e:-e['quality'])[:4]
  pending=[]
  for i,parent in enumerate(parents):
   for j in range(2):
    c=mutate(parent,generation*100+i*2+j)
    if spec:
     issues=check_candidate(c,spec)
     if issues:rejections.append(dict(id=c['id'],reason='mutated_region_constraints',violations=issues));continue
    pending.append(c)
 # Holdout is performed once on preselected discovery elites. No holdout-guided
 # search, seed retry or replacement by a more fortunate policy.
 elites=sorted(archive.feasible.values(),key=lambda e:(-e['quality'],e['uid']))
 finalists=[];geometries=set()
 for e in elites:
  if e['scenario_sha256']in geometries:continue
  geometries.add(e['scenario_sha256']);finalists.append(e)
  if len(finalists)>=args.finalists:break
 final=evaluate(engine,[e['case']for e in finalists],args.seed+900000,args.validation,'holdout',levels=('clean','mild','moderate'))
 final_by_id={e['uid']:e for e in final};altcases=[];altowners={}
 for e in finalists:
  reference=e['witness']
  if not reference:continue
  for c in alternatives(reference['case']):
   c['id']=e['uid'][:16]+'-'+c['id'];altcases.append(c);altowners[c['id']]=e['uid']
 shortcuts=collections.defaultdict(list)
 def cost(word):
  optional=set()
  for action,cap in [('wall_jump','wall_climb'),('air_jump','double_jump'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple'),('anchor_jump','grapple')]:
   if action in word:optional.add(cap)
  return optional,len(word)
 for c,r,evidence in engine.run(altcases,'alternatives'):
  uid=altowners[c['id']];reference=all_entries[uid]['best']['word'];word=list(actual_word(r));a,n=cost(reference);b,m=cost(word)
  if r['ok']and(b<a or(a==b and m<n)):shortcuts[uid].append(dict(word=word,alternative=c['alternative'],evidence=evidence))
 catalog=[];review_cases=[]
 for e in finalists:
  f=final_by_id[e['uid']];stats=f['discovery'];admission=gate(stats,shortcuts[e['uid']],bool(e['case'].get('saws')or e['case'].get('moving_platforms')),policy)
  witness=f['witness']or e['witness'];row=dict(uid=e['uid'],scenario_sha256=e['scenario_sha256'],family=e['case']['family'],features=e['features'],calibration=e['discovery'],validation=stats,shortcut_witnesses=shortcuts[e['uid']],admission=admission,formal_game_ready=False)
  catalog.append(row)
  if admission['status']!='awaiting_human_review'or not witness:continue
  c=copy.deepcopy(witness['case']);c['recorded_frames']=witness['recorded_frames'];c.pop('noise',None)
  c['review_warnings']=[];c['admission_status']='awaiting_human_review';c['factory_id']=e['uid'];c['factory_evidence']=witness['evidence'];c['module_sha256']=module_hash(c)
  row['module_sha256']=c['module_sha256'];review_cases.append(c)
 rng=random.Random(args.seed+77);rng.shuffle(review_cases)
 for i,c in enumerate(review_cases):c['title']=c['review_alias']=f'样例 {i+1:02d}'
 binding={k:v for k,v in engine.binding.items()if k!='source_files'}
 manifest=dict(schema='pcg/factory-catalog/v1',run_id=args.name,seed=args.seed,quality_policy=policy,quality_policy_sha256=digest(policy),physics_binding=binding,candidates=catalog,review_modules=[dict(uid=c['factory_id'],module_sha256=c['module_sha256'],alias=c['review_alias'])for c in review_cases],human_feedback_count=0,approved_offline_count=0,formal_game_ready=False)
 manifest['catalog_sha256']=digest(manifest)
 summary=dict(schema='pcg/factory-summary/v1',seed=args.seed,proposals=proposal_count,initial_candidate_policies=len(candidates),evaluated_policies=len(all_entries),rounds=rounds,feasible_behavior_cells=len(archive.feasible),infeasible_behavior_cells=len(archive.infeasible),holdout_finalists=len(finalists),awaiting_human_review=len(review_cases),rework=sum(x['admission']['status']=='rework'for x in catalog),approved_offline=0,human_feedback=0,physics_cases=engine.sim.cases,batches=len(engine.batches),batch_size=args.batch_size,wall_seconds=time.perf_counter()-start,source_snapshot_files=len(engine.hashes),unseen_phases_seed=args.seed+900000,limits=['Finite automated policy evidence only; no human fun or formal game/region admission.','Observed behavior cells, not a percentage of all possible gameplay.','Failure to find a lower-cost alternative does not prove necessity.'])
 for n,v in [('catalog',manifest),('summary',summary),('archive_history',archive.history),('rejections',rejections),('review_cases',{'cases':review_cases}),('search_cases',{'cases':[e['case']for e in all_entries.values()]}),('discovery_entries',list(all_entries.values()))]:
  (out/(n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2 if n in('summary','catalog','rejections')else None))
 print(json.dumps(summary,ensure_ascii=False,indent=2));return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',type=int,default=751100);p.add_argument('--seeds',type=int,default=2);p.add_argument('--words',type=int,default=2);p.add_argument('--ferries',type=int,default=3);p.add_argument('--rounds',type=int,default=1);p.add_argument('--finalists',type=int,default=8);p.add_argument('--calibration',type=int,default=4);p.add_argument('--validation',type=int,default=12);p.add_argument('--batch-size',type=int,default=12);p.add_argument('--region');p.add_argument('--capabilities',default='move,jump,double_jump,wall_climb,grapple,shot_recoil');p.add_argument('--repair-job');p.add_argument('--repair-catalog');p.add_argument('--repair-cases');run(p.parse_args())
if __name__=='__main__':main()
