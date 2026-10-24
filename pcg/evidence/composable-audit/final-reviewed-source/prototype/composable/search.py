#!/usr/bin/env python3
"""Typed action-graph exploration with independent real-physics geometry replay.
This is bounded search, never an assertion of arbitrary-mechanic completeness.
"""
from pathlib import Path
import argparse,random,json,time,collections,copy,hashlib,sys
from contracts import Registry,Grammar
from synthesis import compile_probe,materialize,actual_word,behavioral_descriptor,fingerprint
from simulator import Simulator,ROOT

def expected_word(word):return tuple(op for op in word if op!='wall_contact')
def intent_ok(case,result):return actual_word(result)==expected_word(case['word'])

def run(args):
 out=ROOT/'results'/args.name;sim=Simulator(out);start=time.perf_counter();probes=[];labels=[]
 combinations=[Registry().resolve(args.capabilities)] if args.capabilities is not None else list(Registry().combinations())
 for ci,caps in enumerate(combinations):
  words=Grammar(caps).derive(args.seed+ci,limit=args.words,max_depth=7)
  if not words:words=[()]
  for wi,word in enumerate(words):
   for variant in range(args.variants):
    seed=args.seed+ci*10000+wi*100+variant
    p=compile_probe(word,caps,seed);p['id']=f'p-c{ci}-w{wi}-v{variant}';p['combo_index']=ci
    probes.append(p)
 # The same proposal/variation budget is explicit; no successful-seed cherry picking.
 pres=sim.run(probes,'00-motion-probes');candidates=[];reasons=collections.Counter()
 for p,r in zip(probes,pres):
  if not intent_ok(p,r):reasons['unrealized_motion_word']+=1;continue
  for width in (112,160):
   c=materialize(p,r,width=width,clearance=44)
   if c is None:reasons['no_receiving_surface']+=1;continue
   c['id']=p['id'].replace('p-','c-')+f'-w{width}';candidates.append(c)
 results=sim.run(candidates,'01-geometry-replay');good=[]
 for c,r in zip(candidates,results):
  if r['ok'] and intent_ok(c,r):good.append(dict(case=c,result=r,actual_word=list(actual_word(r)),descriptor=list(behavioral_descriptor(r)),geometry=fingerprint(c)))
  else:reasons[r['reason'] if not r['ok'] else 'unrealized_geometry_word']+=1
 # Keep one candidate per actual word + capability set. Wider support is an
 # explicit parameter candidate, not a new action type.
 archive={}
 for e in good:
  key=(tuple(e['case']['capabilities']),tuple(e['actual_word']))
  quality=e['case']['synthesis']['landing_width']
  if key not in archive or quality>archive[key]['case']['synthesis']['landing_width']:archive[key]=e
 summary=dict(schema='pcg/composable-search/v2',seed=args.seed,words_per_combo=args.words,variants_per_word=args.variants,capability_combinations=len(combinations),
  proposals=len(probes),geometry_candidates=len(candidates),settled_valid=len(good),unique_action_words=len({tuple(e['actual_word']) for e in good}),
  unique_geometries=len({e['geometry'] for e in good}),archive_entries=len(archive),failure_reasons=reasons,wall_seconds=time.perf_counter()-start,
  physics_calls=sim.calls,physics_cases=sim.cases,groups=[])
 for ci,caps in enumerate(combinations):
  ps=[p for p in probes if p['combo_index']==ci];cs=[c for c in candidates if c['combo_index']==ci];gs=[e for e in good if e['case']['combo_index']==ci]
  summary['groups'].append(dict(combo=ci,capabilities=sorted(caps),proposals=len(ps),geometry_candidates=len(cs),settled_valid=len(gs),actual_words=len({tuple(e['actual_word']) for e in gs})))
 (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'archive.json').write_text(json.dumps(list(archive.values())));(out/'valid.json').write_text(json.dumps(good))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=920100);p.add_argument('--words',type=int,default=8);p.add_argument('--variants',type=int,default=2);p.add_argument('--name',default='composable-calibration-v1');p.add_argument('--capabilities',nargs='*',default=None,help='Explicit registered IDs; omit to run the 16 move+jump optional sets');run(p.parse_args())
