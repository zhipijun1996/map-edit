"""Geometry-based closed/open chest separation, independent of pilot labels.

Exact rectangle arrangement: expand actual SOLID collision by the player half
body, flood free arrangement cells through positive-width faces. One-way floors
are omitted; only solid Module rock and the selected gate may prove separation.
This is an over-approximation of motion, hence a blocked path is meaningful;
an open path is geometry-only and still needs the real Godot route witness.
"""
from collections import deque
import argparse,json
from pathlib import Path
from ..run import write

def reachable(rects,start,goal,bounds):
 # Closed forbidden bodies include actual player half extents. Tiny tolerance
 # allows contact at a floor without allowing a finite-size hole through rock.
 rects=[(x-12+1e-5,y-18+1e-5,x+w+12-1e-5,y+h+18-1e-5)for x,y,w,h in rects]
 bx,by,bw,bh=bounds
 xs=sorted({bx,bx+bw,start[0],goal[0]}|{v for r in rects for v in [r[0],r[2]]if bx<v<bx+bw})
 ys=sorted({by,by+bh,start[1],goal[1]}|{v for r in rects for v in [r[1],r[3]]if by<v<by+bh})
 def free(i,j):
  x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
  return not any(a<x<c and b<y<d for a,b,c,d in rects)
 valid={(i,j)for i in range(len(xs)-1)for j in range(len(ys)-1)if free(i,j)}
 def at(p):return {(i,j)for i,j in valid if xs[i]-1e-7<=p[0]<=xs[i+1]+1e-7 and ys[j]-1e-7<=p[1]<=ys[j+1]+1e-7}
 seen=at(start);targets=at(goal);queue=deque(seen)
 while queue:
  i,j=queue.popleft()
  if (i,j)in targets:return True
  for n in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]:
   if n in valid and n not in seen:seen.add(n);queue.append(n)
 return False

def run(run_dir):
 run_dir=Path(run_dir);c=json.loads((run_dir/'compiled.json').read_text());case=c['case']
 rects=[r for i,r in enumerate(case['platforms'])if i not in case['one_way_platform_indices']]
 rows=[]
 for name,latch_id,start in [('bridge-cache','arch/arch-bell',[1360,520]),('bell-cache','bell/valley-bell',[1160,1040])]:
  latch=next(v for v in case['latches']if v['id']==latch_id);reward=next(v for v in case['reward_sites']if v['id'].endswith(name))
  target=reward['target']['position'];closed=reachable(rects+[latch['gate']],start,target,case['world_bounds']);opened=reachable(rects,start,target,case['world_bounds'])
  rows.append(dict(reward=reward['id'],gate=latch_id,closed_geometric_path=closed,open_geometric_path=opened,passed=not closed and opened))
 result=dict(schema='pcg/solid-chest-separation/v1',all_passed=all(r['passed']for r in rows),rows=rows,
  scope='Expanded-body free-space separation by real solid Module objects and one closed gate; ignores one-way floors and motion limits. Does not assert all exploration edges are mandatory.')
 write(run_dir/'gate-separation.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('run');a=p.parse_args();print(json.dumps(run(a.run),ensure_ascii=False,indent=2))
