import argparse,json,math
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def shot_geometry(r):
 fs={f['frame']:f for f in r.get('frames',[])};out=[]
 for sh in [s for s in r.get('plains',{}).get('events',[])if s['type']=='shot_origin'][:2]:
  en=fs[sh['frame']]['plains']['enemies'][0];m=sh['muzzle'];dx,dy=en['x']-m[0],en['y']-m[1];d=math.hypot(dx,dy);theta=math.atan2(dy,dx);aa=[]
  for ax in [-14,14]:
   for ay in [-16,16]:
    vx,vy=dx+ax,dy+ay;dd=math.hypot(vx,vy);a=math.atan2(math.sin(math.atan2(vy,vx)-theta),math.cos(math.atan2(vy,vx)-theta));b=math.asin(min(1,3/dd));aa.extend([a-b,a+b])
  out.append(dict(shot_id=sh['shot_id'],frame=sh['frame'],muzzle=m,enemy=[en['x'],en['y']],range=d,symmetric_static_half_angle_degrees=min(-math.degrees(min(aa)),math.degrees(max(aa)))))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interface',type=int,choices=[0,1],default=0);p.add_argument('--controls',type=int,nargs='+',default=[0]);p.add_argument('--level',choices=['clean','mild','moderate'],default='clean');p.add_argument('--trials',type=int,default=1);p.add_argument('--routes',nargs='*');a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES);rows=[]
 bases=[c for control in a.controls for c in rules.layouts(rules.RECIPES[0],a.interface,control)if not a.routes or c['route_spec']['id']in a.routes];cs=[instantiate(c,261032001,a.level,j)for c in bases for j in range(a.trials)]
 for c,r,ev in e.run(cs,'bounded-r3-v1-'+a.level):
  row=dict(id=c['id'],route_spec=c['route_spec'],interface=c['interface'],control=c['rule_parameters']['control'],purpose=rules.purpose(c,r),shot_geometry=shot_geometry(r),evidence=ev,result_summary={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks','returns']});rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),rows=rows))
