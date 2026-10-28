"""Read actual output witnesses, never infer coverage from planned input alone."""
import argparse,gzip,json
from pathlib import Path
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

def analyze(run):
 run=Path(run);c=json.loads((run/'compiled.json').read_text());cases=json.loads((run/'cases.json').read_text())['cases'];by={v['id']:v for v in cases};observed=set();rows=[]
 for batch in json.loads((run/'physics/batches.json').read_text()):
  path=run/'physics'/batch['gzip_path']
  if file_sha(path)!=batch['gzip_sha256']:raise ValueError('trace_drift')
  for r in json.loads(gzip.decompress(path.read_bytes()))['results']:
   case=by[r['id']];legs={v['id']:v for v in case['pilot_program']}
   for v in r['pilot']['legs']:
    leg=legs[v['id']]
    if v.get('ok')and leg.get('edge_terminal'):observed.add((leg['edge_id'],leg['edge_from'],leg['edge_to']))
   frames={v['frame']:v for v in r['frames']}
   shots=[dict(frame=e['frame'],airborne=not frames[e['frame']]['grounded'],position=e['origin'],direction=e['direction'])for e in r['plains']['events']if e['type']=='shot_origin']
   passages=[]
   for latch in case['latches']:
    x,y,w,h=latch['gate'];found=[]
    for f in r['frames']:
     if f['x']+12>x and f['x']-12<x+w and f['y']+18>y and f['y']-18<y+h:
      state=next(b for b in f['plains']['bells']if b['id']==latch['id'])
      if state['open']:found.append(f['frame'])
    passages.append(dict(bell=latch['id'],open_gate_body_overlap_frames=found))
   rows.append(dict(id=r['id'],ok=r['ok'],ticks=r['ticks'],seconds=r['ticks']/60,shots=shots,bells=[e for e in r['plains']['events']if e['type']=='bell_open'],gate_passages=passages,carrier_releases=r['extra'].get('carrier_release_events',[]),rewards=r['extra'].get('optional_challenge_events',[])))
 expected={(e['id'],e['from'],e['to'])for e in c['exploration_graph']['edges']}|{(e['id'],e['to'],e['from'])for e in c['exploration_graph']['edges']if e['bidirectional']}
 result=dict(schema='pcg/open-valley-actual-evidence/v1',observed_directions=[list(v)for v in sorted(observed)],expected_directions=len(expected),all_declared_directions_observed=expected<=observed,rows=rows,
  scope='Finite actual witnesses of planned routes; open air can permit additional physical routes; not an exhaustive reachability graph or human fun approval')
 write(run/'coverage.json',result)
 write(run/'map-recipe.json',dict(schema='pcg/direct-module-map-recipe/v1',modules=[dict(instance=m['id'],document=m['canonical_document'],placement=m['spec']['placement'])for m in c['modules']],seams=c['seams'],hard_checks=c['hard_checks']))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();r=analyze(a.run);print(r['all_declared_directions_observed'],[(v['id'],len(v['shots']))for v in r['rows']])
