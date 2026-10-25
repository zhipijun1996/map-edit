"""Independent actual-world policies against a frozen regional candidate.

Coverage changes inputs only. No cells are deleted, no resources replenished,
no teleportation, no recalibration from independent phase results.
"""
import argparse,copy,json,sys,traceback
from pathlib import Path
from .materialize import RegionEngine,case_for
from ..director import REPO
from ..run import write
from ..r2_full.orchestrate import logical_route,partitioned_cover
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
sys.path.insert(0,str(REPO/'experiments/l4-mapgen'))
import region_network

def cases_for(c,mode,phases=None):
 g=c['exploration_graph'];approaches=region_network.approach_routes(g)
 normal=[case_for(c,logical_route(c,[*route['nodes'][1:],g['goal']]),'approach-'+str(i))for i,route in enumerate(approaches)]
 rest=next(n['id']for n in g['nodes']if n['role']=='rest')
 returned=case_for(c,logical_route(c,[rest,g['entry']]),'camp-and-continuous-return')
 # Original Definition requires distinct entry/exit positions. Finish at a
 # real source-owned dock after returning; no coordinate or state assignment.
 entry=c['nodes'][g['entry']]
 support=entry['center']['support_indices'][0];slab=c['case']['platforms'][support]
 x=slab[0]+16 if abs(entry['center']['position'][0]-(slab[0]+16))>1 else slab[0]+slab[2]-16
 if abs(x-entry['center']['position'][0])<=1:raise ValueError('no_distinct_safe_return_marker_on_entry_bank')
 y=entry['center']['position'][1]
 target=dict(id='verification-finish/returned-entry-bank',position=[x,y],region=[x-4,y-4,8,8],grounded=True,support_indices=[support])
 returned['pilot_program'].append(dict(id='returned-entry-bank-marker',kind='walk',target=target,edge_id='returned-entry-bank',budget_ticks=360))
 returned.update(goal=target['region'],exit_port=target['position'])
 normal.append(returned)
 if mode=='routes':return normal
 if mode=='holdout':
  result=[]
  for v in normal:
   for phase in (phases if phases is not None else [.07,.29,.59,.83]):
    trial=copy.deepcopy(v);trial['id']+='-phase-'+str(phase)
    for item in trial['saws']+trial['moving_platforms']:item['initial_phase']=phase
    result.append(trial)
  return result
 if mode=='negative':
  result=[]
  main=normal[0]
  targets=[v for v in main['pilot_program']if v.get('action_intent','').startswith('airborne downward')]
  for index,target in enumerate(targets):
   trial=copy.deepcopy(main);trial['id']='full-region-omit-spire-shot-'+str(index)
   selected=next(v for v in trial['pilot_program']if v['id']==target['id'])
   for op in selected['control_plan']:
    if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
   result.append(trial)
  # A full-hold cheaper alternative to the first omitted recoil, preserving
  # every wait interval and all other geometry/state in the route.
  if result:
   trial=copy.deepcopy(result[0]);trial['id']='full-region-omit-first-shot-long-jump'
   for op in next(v for v in trial['pilot_program']if v['id']==targets[0]['id'])['control_plan']:
    if op['op']=='jump_release':op['trigger']['after']=24
   result.append(trial)
  return result
 if mode=='core':
  subset=copy.deepcopy(c)
  subset['exploration_graph']['edges']=[e for e in g['edges']if e['purpose']in ['regional_route','boss_gate']]
  tours=partitioned_cover(subset,12)
  return [case_for(c,v['r2_semantics']['logical_route'],'core-coverage-'+str(i))for i,v in enumerate(tours)]
 raise ValueError('unknown_verification_mode')

def run(source,name,mode,phase_protocol=None):
 source=Path(source).resolve();out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_region_verification_exists')
 out.mkdir(parents=True)
 c=json.loads((source/'compiled.json').read_text());write(out/'compiled.json',c)
 binding={str(p.relative_to(REPO)):file_sha(p)for p in [source/'compiled.json',source/'physics/source_binding.json',source/'module-library/documents/manifest.json']}
 write(out/'source-candidate.json',dict(files=binding,source=str(source),geometry_digest=digest(c['case']),selection='frozen before independent verification; changes to the candidate invalidate this run'))
 phases=None
 if phase_protocol:
  phase_protocol=Path(phase_protocol).resolve();phase_data=json.loads(phase_protocol.read_text());phases=phase_data['independent_phases']
  if len(phases)!=4 or any(not 0<=p<1 for p in phases):raise ValueError('four_finite_independent_phases_required')
  write(out/'independent-phase-protocol.json',dict(source=str(phase_protocol),sha256=file_sha(phase_protocol),protocol=phase_data))
 cases=cases_for(c,mode,phases);write(out/'cases.json',dict(cases=cases))
 write(out/'protocol.json',dict(mode=mode,expected='all reject'if mode=='negative'else'all pass',cases=len(cases),maximum_local_revisions=0,
  independent_phases=(phases if phases is not None else [.07,.29,.59,.83])if mode=='holdout'else[],world_resets_within_route=0,target_met=False,quality_admitted=False,
  scope='Full physical world; core mode excludes unresolved reward/shortcut obligations from its requested route coverage, not from actual collision world'))
 engine=RegionEngine(out/'physics');rows=[]
 for v,r,ev in engine.run(cases,'region-'+mode):
  f=r.get('pilot',{}).get('failure',{})
  row=dict(id=v['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),jumps=r.get('jumps'),hp=r.get('hp'),failure=f,evidence=ev)
  rows.append(row);write(out/'summary.json',dict(rows=rows,all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),expected_results_met=len(rows)==len(cases)and all(r['ok']!=(mode=='negative')for r in rows),target_met=False))
  print(json.dumps(dict(id=v['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),failure_leg=f.get('leg_id'),actual=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--name',required=True);p.add_argument('--mode',choices=['routes','core','negative','holdout'],default='routes');p.add_argument('--phase-protocol');a=p.parse_args();print(run(a.source,a.name,a.mode,a.phase_protocol))
