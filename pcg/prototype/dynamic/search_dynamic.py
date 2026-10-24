#!/usr/bin/env python3
"""Bounded primitive/action synthesis and temporal-window search using real objects."""
import argparse,copy,json,time,collections
from simulator import ROOT,Simulator
from generators import motion_proposals,turn_into_modules,saw_variants,ferry_candidates,with_phases,actual_word

def run(args):
 sim=Simulator(ROOT/'results'/args.name);start=time.perf_counter()
 probes=motion_proposals(args.seed,args.words);pres=sim.run(probes,'00-motion')
 modules,reasons=turn_into_modules(probes,pres);candidates=[]
 for c in modules:
  if c['family']=='thorn_wall':c.pop('reference_frames',None);candidates.append(c)
  else:candidates+=saw_variants(c,periods=(2.4,3.2) if not args.pilot else (2.4,))
 candidates+=ferry_candidates(args.seed+700,args.ferries)
 for c in candidates:c['synthesis_stage']='calibration_search'
 calibration=[];owners=[]
 phases=(0.,.25,.5,.75) if not args.pilot else (0.,)
 for ci,c in enumerate(candidates):
  for p in with_phases(c,phases):calibration.append(p);owners.append(ci)
 rs=sim.run(calibration,'01-calibration');groups=collections.defaultdict(list)
 for i,c,r in zip(owners,calibration,rs):groups[i].append(dict(case=c,result=r))
 scored=[]
 for i,c in enumerate(candidates):
  rows=groups[i];score=sum(e['result']['ok'] for e in rows)
  if score:scored.append(dict(case=c,calibration_success=score,calibration_trials=len(rows),reference=next(e for e in rows if e['result']['ok'])))
 # One temporal policy per primitive geometry; all losses remain in raw outputs.
 archive={}
 for e in scored:
  c=e['case'];key=c['id'].split('-s')[0] if c['family']=='hook_saw' else c['id']
  if key not in archive or e['calibration_success']>archive[key]['calibration_success']:archive[key]=e
 summary=dict(schema='pcg/dynamic-search/v3',seed=args.seed,motion_proposals=len(probes),materialized_motion=len(modules),candidate_policies=len(candidates),calibration_cases=len(calibration),calibration_success=sum(r['ok'] for r in rs),archive_entries=len(archive),physics_cases=sim.cases,wall_seconds=time.perf_counter()-start,groups={},motion_rejections=reasons,failure_reasons=dict(collections.Counter(r['reason'] for r in rs if not r['ok'])))
 for family in ('thorn_wall','hook_saw','carrier_double','carrier_recoil'):
  rows=[r for c,r in zip(calibration,rs) if c['family']==family];entries=[e for e in archive.values() if e['case']['family']==family]
  summary['groups'][family]=dict(trials=len(rows),success=sum(r['ok'] for r in rows),archive_entries=len(entries))
 (sim.out/'summary.json').write_text(json.dumps(summary,indent=2));(sim.out/'archive.json').write_text(json.dumps(list(archive.values())));(sim.out/'candidate-policies.json').write_text(json.dumps(candidates));print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=740100);p.add_argument('--words',type=int,default=3);p.add_argument('--ferries',type=int,default=6);p.add_argument('--name',default='dynamic-search-v1');p.add_argument('--pilot',action='store_true');run(p.parse_args())
