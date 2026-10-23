#!/usr/bin/env python3
"""Region input -> primitive proposals -> geometry transform -> real validation.

This experimental compiler supports only explicitly registered generator families.
It does not interpret prose, invent a missing mechanism, or certify human fun.
"""
import argparse,copy,json,time,collections
from simulator import ROOT,Simulator
from generators import motion_proposals,turn_into_modules,Grammar,compile_probe,ports
from regions import prepare_regions,filter_families,transform_candidate,check_candidate,RegionSpecError
from evaluate_dynamic import purpose

def run(args):
 # Validate before starting Godot, including proposed/unimplemented mechanics.
 spec=prepare_regions(args.region,args.capabilities.split(','))
 families=filter_families(spec,['thorn_wall','hook_saw','sky_ascent'])
 if not families:raise RegionSpecError('no_registered_generator_family_for_region')
 out=ROOT/'results'/args.name
 out.mkdir(parents=True,exist_ok=True)
 (out/'region-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
 start=time.perf_counter();sim=Simulator(out)
 traversal=spec.get('traversal',{})
 probes=motion_proposals(args.seed,args.words,families=families,available_capabilities=spec['available_capabilities'],max_depth=min(args.max_depth,traversal.get('max_depth',32)),min_actions=max(args.min_actions,traversal.get('min_actions',1)))
 if 'sky_ascent'in families:
  caps=spec['available_capabilities']
  mixed=Grammar(caps).derive(args.seed+31,limit=500,max_depth=min(args.max_depth,traversal.get('max_depth',32)),min_actions=max(6,args.min_actions))
  mixed=[w for w in mixed if 'wall_jump'in w and 'air_jump'in w and 'recoil'in w and any(a.startswith('hook_') for a in w)]
  for i,word in enumerate(mixed[:args.words*2]):
   c=ports(compile_probe(word,caps,args.seed+500+i,wall_layout='same'),probe=True)
   c.update(id=f'sky-mixed-p{i}',family='sky_ascent',max_frames=1200,trace_all=True);probes.append(c)
 raw=sim.run(probes,'00-motion');modules,rejected=turn_into_modules(probes,raw)
 candidates=[]
 for case in modules:
  reference=case.pop('reference_frames')
  try:
   c=transform_candidate(case,reference,spec)
   violations=check_candidate(c,spec)
   if violations:rejected.append(dict(id=c['id'],reason='region_constraints',violations=violations));continue
   c['source_family']=c['family'];c['family']='sky_ascent' if spec['id']=='sky_islands' else c['family']
   c['trace_all']=True;candidates.append(c)
  except RegionSpecError as e:rejected.append(dict(id=case['id'],reason='region_transform',detail=str(e)))
 results=sim.run(candidates,'01-regional-geometry');archive=[]
 for c,r in zip(candidates,results):
  receipt=purpose(c,r)
  if not receipt['ok']:
   rejected.append(dict(id=c['id'],reason='physics_or_action_purpose',physics_reason=r['reason'],purpose=receipt));continue
  valid=copy.deepcopy(c);valid['region_profile']['validation_status']='real_physics_and_action_word_passed'
  archive.append(dict(case=valid,result=r,purpose=receipt))
 # Command timing disturbance evaluates this automatic policy, not human skill.
 noisy=[];owners=[]
 for i,e in enumerate(archive):
  for level,timing,angle in [('mild',1,2),('moderate',3,6)]:
   for trial in range(args.trials):
    c=copy.deepcopy(e['case']);c['id']+=f'-{level}-{trial}';c['noise']=dict(seed=args.seed+1000+trial,timing_frames=timing,aim_degrees=angle)
    noisy.append(c);owners.append(dict(module=i,level=level,trial=trial))
 nr=sim.run(noisy,'02-disturbance');groups={}
 for level in ('mild','moderate'):
  rows=[(c,r) for c,r,l in zip(noisy,nr,owners) if l['level']==level]
  groups[level]=dict(trials=len(rows),safe_stable=sum(r['ok'] for c,r in rows),purpose_valid=sum(purpose(c,r)['ok'] for c,r in rows))
 summary=dict(schema='pcg/region-search/v1',region=spec['id'],profile_sha256=spec['profile_sha256'],available_capabilities=spec['available_capabilities'],seed=args.seed,proposals=len(probes),materialized=len(modules),region_constraint_pass=len(candidates),physics_and_purpose_pass=len(archive),disturbance=groups,physics_cases=sim.cases,wall_seconds=time.perf_counter()-start,rejection_counts=dict(collections.Counter(e['reason'] for e in rejected)),limits=['Research input only; no formal region/Bible acceptance.','Supports registered mechanisms and synthesis families; arbitrary prose/unknown mechanics are not implemented.','No human fun, minimum ability requirements, or full-game integration established.'])
 for name,value in [('summary',summary),('archive',archive),('rejections',rejected),('disturbance-labels',owners)]:
  (out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2 if name in ('summary','rejections') else None))
 print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--region',required=True);p.add_argument('--capabilities',default='move,jump,double_jump,wall_climb,grapple,shot_recoil');p.add_argument('--seed',type=int,default=742100);p.add_argument('--words',type=int,default=4);p.add_argument('--max-depth',type=int,default=12);p.add_argument('--min-actions',type=int,default=4);p.add_argument('--trials',type=int,default=8);p.add_argument('--name',default='region-sky-v1');run(p.parse_args())
