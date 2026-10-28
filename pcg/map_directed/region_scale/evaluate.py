"""Evidence-derived route/coverage diagnostics; scale never grants quality."""
import argparse,gzip,json,math
from pathlib import Path
from collections import Counter
from ..run import write
from ..director import REPO
from pcg.prototype.factory.core.engine import file_sha

def traces(run):
 run=Path(run);cases={v['id']:v for v in json.loads((run/'cases.json').read_text())['cases']}
 for b in json.loads((run/'physics/batches.json').read_text()):
  p=run/'physics'/b['gzip_path']
  if file_sha(p)!=b['gzip_sha256']:raise ValueError('trace_bytes_drift')
  for r in json.loads(gzip.decompress(p.read_bytes()))['results']:yield cases[r['id']],r

def route_row(case,r):
 frames=r.get('frames',[])
 stationary=sum(math.hypot(*f.get('real_velocity',[0,0]))<1 for f in frames)
 legs=r.get('pilot',{}).get('legs',[])
 complete={v['id']for v in legs if v.get('ok')}
 arcs=sorted({(v['edge_id'],v['edge_from'],v['edge_to'])for v in case['pilot_program']if v.get('edge_terminal')and v['id']in complete})
 return dict(id=r['id'],passed=r['ok'],reason=r['reason'],ticks=r.get('ticks'),seconds=(r.get('ticks')or 0)/60,
  shots=r.get('shots'),jumps=r.get('jumps'),health=r.get('hp'),
  stationary_world_fraction=stationary/len(frames)if frames else None,
  continuous_distance=sum(math.hypot(b['x']-a['x'],b['y']-a['y'])for a,b in zip(frames,frames[1:])),
  observed_directed_arcs=arcs,visited_places=r.get('extra',{}).get('visited_nodes',[]),
  claimed_challenges=r.get('extra',{}).get('optional_challenge_events',[]),
  failure=r.get('pilot',{}).get('failure',{}),
  caution='Stationary fraction includes aiming/arrival/phase observation; it is not a fun score or an exact waiting classification')

def acceptance(c,rows):
 g=c['exploration_graph'];expected={(e['id'],a,b)for e in g['edges']for a,b in ([(e['from'],e['to']),(e['to'],e['from'])]if e['bidirectional']else[(e['from'],e['to'])])}
 observed={tuple(a)for r in rows for a in r['observed_directed_arcs']}
 missing=sorted(expected-observed)
 blockers=[]
 if missing:blockers.append('whole_map_directed_coverage_incomplete')
 if c.get('unresolved_rewards'):blockers.append('reward_demands_not_materialized')
 if not c['case'].get('reward_sites'):blockers.append('no_actual_challenge_chests')
 if not c['case'].get('enemies'):blockers.append('enemy_ecology_not_materialized')
 blockers+=['district_landform_and_action_diversity_not_admitted','physical_gate_bypass_probes_not_completed','boss_encounter_and_campaign_not_integrated','cross_seed_physical_diversity_not_validated','human_fun_unreviewed']
 return dict(target_met=False,quality_admitted=False,production_admitted=False,declared_directed_arcs=len(expected),
  observed_directed_arcs=len(expected&observed),missing_directed_arcs=missing,blockers=blockers,
  scope='Finite policy coverage never proves arbitrary physical reachability or no softlock. Reward/return obligations remain required.')

def run(source,runs,out):
 c=json.loads((Path(source)/'compiled.json').read_text());rows=[];sources={}
 for run in runs:
  path=Path(run)
  rows += [dict(run=str(path),**route_row(case,r))for case,r in traces(path)]
  sources[str(path/'physics/batches.json')]=file_sha(path/'physics/batches.json')
 result=dict(schema='pcg/full-region-physical-diagnostics/v1',source_candidate=str(source),
  actual_macro_instances=len(c['modules']),actual_core_places=len(c['exploration_graph']['core_nodes']),
  reserved_bounds=c['case']['world_bounds'],actual_cells={k:len(c['case'][k])for k in ['platforms','saws','moving_platforms','latches','enemies','reward_sites']},
  source_sha256=sources,rows=rows,acceptance=acceptance(c,rows))
 write(Path(out),result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--runs',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(run(a.source,a.runs,a.out)['acceptance'])
