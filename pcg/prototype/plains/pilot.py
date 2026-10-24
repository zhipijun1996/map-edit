"""Discovery only; do not turn pilot retries into held-out validation."""
import argparse,collections,copy,json
from .engine import ROOT,PlainsEngine
from .synthesis import proposals,enemy_materialize,materialize,shot_events,identity
from ..factory.core.quality import module_hash

def summarize(case,result,evidence):
 return dict(id=case['id'],uid=identity(case),family=case['family'],ok=result['ok'],reason=result['reason'],shots=result.get('shots',0),jumps=result.get('jumps',0),air_jumps=result.get('air_jumps',0),ticks=result['ticks'],min_y=min((f['y']for f in result['frames']),default=10000),max_x=max((f['x']for f in result['frames']),default=-10000),events=result.get('plains',{}).get('events',[]),evidence=evidence)
def run(name):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);probes=proposals();enemy_probes=[];candidates=[];rows=[]
 for c,r,e in engine.run(probes,'motion-discovery'):
  rows.append(summarize(c,r,e))
  if c['family']=='enemy_refund':
   child=enemy_materialize(c,r)
   if child:enemy_probes.append(child)
  else:candidates+=materialize(c,r)
 for c,r,e in engine.run(enemy_probes,'enemy-motion-discovery'):
  rows.append(summarize(c,r,e));candidates+=materialize(c,r)
 unique={identity(c):c for c in candidates};candidates=list(unique.values());qualified=[]
 for c,r,e in engine.run(candidates,'geometry-discovery'):
  row=summarize(c,r,e);rows.append(row)
  if r['ok']:
   qualified.append(dict(case=c,result=r,evidence=e))
 summary=dict(probes=len(probes),enemy_probes=len(enemy_probes),geometries=len(candidates),safe_stable=len(qualified),families=dict(collections.Counter(e['case']['family']for e in qualified)),physics_cases=engine.sim.cases,scope='Discovery/calibration only; no holdout, fun rating or approval')
 for n,data in [('summary',summary),('rows',rows),('candidates',{'cases':candidates}),('qualified',qualified)]:
  (out/(n+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2 if n=='summary'else None))
 print(json.dumps(summary,indent=2));return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
