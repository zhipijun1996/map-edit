"""Calibration repair: earlier first shot and target placement from its real ray."""
import argparse,itertools,json,collections,math
from .engine import ROOT,PlainsEngine
from .synthesis import probe,enemy_materialize,materialize,identity,shot_events
from .phrases import enemy_bell_gear
from .evaluation import purpose

def run(name):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);probes=[];enemies=[];candidates=[];rows=[]
 for i,(hold,shot,x)in enumerate(itertools.product((10,12),(16,20),(-.2,.25))):probes.append(probe('enemy_refund',100+i,hold,shot,[x,math.sqrt(1-x*x)],18))
 (out/'protocol.json').write_text(json.dumps(dict(scope='Calibration-only repair; holdout not yet run',probes=8,holds=[10,12],first_shots=[16,20],aim_x=[-.2,.25],second_delay=18,reason='Old calibration showed late-shot body contact and missed first hit; preserve enemy physics and change action timing/target geometry'),indent=2))
 for c,r,ev in engine.run(probes,'early-shot-motion'):
  child=enemy_materialize(c,r);rows.append(dict(id=c['id'],stage='motion',materialized=child is not None,evidence=ev))
  if child:enemies.append(child)
 for c,r,ev in engine.run(enemies,'real-enemy-motion'):
  rows.append(dict(id=c['id'],stage='enemy_motion',shots=r.get('shots'),events=r.get('plains',{}).get('events',[]),evidence=ev))
  for child in materialize(c,r):
   grown=enemy_bell_gear(child,r,len(candidates))
   if grown:candidates.append(grown)
 qualified=[]
 for c,r,ev in engine.run(candidates,'enemy-phrase-geometry'):
  p=purpose(c,r);rows.append(dict(id=c['id'],stage='geometry',ok=p['ok'],reason=r['reason'],purpose=p,evidence=ev))
  if p['ok']:qualified.append(dict(case=c,result=r,evidence=ev))
 summary=dict(scope='Calibration discovery only, not holdout',probes=len(probes),real_enemy_probes=len(enemies),geometries=len(candidates),qualified=len(qualified),physics_cases=engine.sim.cases)
 for key,value in [('summary',summary),('rows',rows),('qualified',qualified),('candidates',dict(cases=candidates))]:(out/(key+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2 if key=='summary'else None))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
