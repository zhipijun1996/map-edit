"""Compare actual formal generator output and actual isolated Map evidence.

Different scales/runtime scopes are kept explicit; no aggregate fun score.
"""
import argparse,json,math,statistics,html
from collections import deque
from pathlib import Path
from ..run import write

def metrics(nodes,edges,start,goal):
 adj={k:set()for k in nodes}
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 distances={start:0};q=deque([start])
 while q:
  n=q.popleft()
  for other in adj[n]:
   if other not in distances:distances[other]=distances[n]+1;q.append(other)
 return dict(places=len(nodes),connections=len(edges),independent_cycles=len(edges)-len(nodes)+1,
  junctions=sum(len(v)>=3 for v in adj.values()),leaves=sum(len(v)==1 for v in adj.values()),
  shortest_declared_goal_edges=distances.get(goal),reachable_places=len(distances))

def svg(nodes,edges,title):
 xs=[p[0]for p in nodes.values()];ys=[p[1]for p in nodes.values()]
 def xy(p):return (50+(p[0]-min(xs))/max(1,max(xs)-min(xs))*900,70+(p[1]-min(ys))/max(1,max(ys)-min(ys))*500)
 parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 640"><rect width="1000" height="640" fill="#14232b"/>',f'<text x="24" y="30" fill="#ead39a" font-size="22">{html.escape(title)}</text>']
 for a,b in edges:
  x,y=xy(nodes[a]);u,v=xy(nodes[b]);parts.append(f'<path d="M{x},{y} L{u},{v}" stroke="#799e9b" stroke-width="3"/>')
 for k,p in nodes.items():
  x,y=xy(p);parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#e6b56c"/><text x="{x+10}" y="{y+4}" fill="white" font-size="15">{html.escape(k)}</text>')
 return ''.join(parts)+'</svg>'

def run(run_dir,baseline,formal,out):
 run_dir=Path(run_dir);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 c=json.loads((run_dir/'compiled.json').read_text());coverage=json.loads((run_dir/'coverage.json').read_text())
 rows=[]
 for r in json.loads(Path(baseline).read_text())['rows']:
  m=r['manifest'];nodes={v['id']:v['position']for v in m['areas']};edges=[(v['a'],v['b'])for v in m['connections']]
  rows.append(dict(seed=r['seed'],content_version=m['version'],family=m['family'],manifest_hash=m['manifest_hash'],
   topology=metrics(nodes,edges,'area_0_1',m['prep_id']),module_instances=len(m['nodes']),
   enemies=len(m['enemies']),treasure_chests=len(m['rewards']),merchant=bool(m['merchant_id']),boss=True,
   generation_ms=r['generation_usec']/1000,fallback=m['fallback_id'],
   action_recipes=sorted({e.get('recipe','')for e in m['connections']})))
  if len(rows)==1:(out/'formal-topology.svg').write_text(svg(nodes,edges,'主游戏正式 v12 · Seed 0 · 探索地点图'))
 nodes={k:v['center']['position']for k,v in c['nodes'].items()};edges=[(e['from'],e['to'])for e in c['exploration_graph']['edges']]
 (out/'new-topology.svg').write_text(svg(nodes,edges,'新风谷 · 8 Modules · 2 回环 + 远端奖励支路'))
 f=json.loads(Path(formal).read_text());frames=f['frames']
 formal_route=dict(seed=f['root_seed'],content_version=f['manifest']['version'],route_reached=f['route_reached'],
  ticks=f['tick_count'],seconds=f['tick_count']/60,shots=sum(e.get('kind')=='shot_accepted'for e in f['events']),
  initial_health=frames[0]['health'],final_health=frames[-1]['health'],
  scope='Original live formal Harness, main preparation route; boss/campaign excluded; privileged input policy; no injected resources or actor teleport')
 new=dict(topology=metrics(nodes,edges,'west','east'),module_instances=len(c['modules']),enemies=len(c['case']['enemies']),
  treasure_chests=len(c['case']['reward_sites']),merchant=True,boss=False,
  actual_route_rows=[dict(id=r['id'],seconds=r['seconds'],shots=len(r['shots']),rewards=r['rewards'])for r in coverage['rows']],
  source_audit=json.loads((run_dir/'assembly-audit.json').read_text()),
  runtime_scope='One fixed eight-Module small region, two loops + far cache spur; complete original physics world, isolated economy. No boss/campaign or broad-seed guarantee.')
 result=dict(schema='pcg/plains-formal-vs-valley/v1',formal_main_commit='26e7f2a4459623f35613a857da8a75e89daa3e62',
  formal_generations=rows,formal_live_route=formal_route,new_map=new,
  cautions=['20 formal exploration areas / ~60 Module instances versus 8 experimental Modules: counts and times are not equal-scale quality comparisons',
   'Formal 5 seeds have different topologies; the new content is one frozen spatial grammar, not a five-seed diversity result',
   'Formal original enemies, boss, Fog of War, two-map campaign and persistence are more complete',
   'New sample demonstrates coupled recoil/actuation, local locked treasure separation and source-owned seamless geometry; no human fun score',
   'Generator wall times and movie software-render cost are not runtime FPS or equal-algorithm speed benchmarks'])
 write(out/'comparison.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--baseline',required=True);p.add_argument('--formal',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=run(a.run,a.baseline,a.formal,a.out);print(r['formal_live_route']);print(r['new_map']['topology'])
