"""Relayout calibration: separate a target window from destructive recoil angle."""
import argparse,copy,json
from .engine import ROOT,PlainsEngine
from .synthesis import shot_events,materialize
from .phrases import enemy_bell_gear
from .evaluation import purpose

def run(name,source):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);old=json.loads((ROOT/'results'/source/'qualified.json').read_text());probes=[];targets={};rows=[];candidates=[]
 for i,e in enumerate(old):
  c=copy.deepcopy(e['case']);s=shot_events(e['result'])[1];bell=[s['muzzle'][0]-180,s['muzzle'][1]+80]
  c.update(id=f'relay-flight-{i}',family='enemy_refund',platforms=[c['platforms'][0]],thorns=[],saws=[],goal=[100000,0,100,100],exit_port=[120,420],max_frames=200,trace_all=True)
  c['latches']=[dict(id='refund_bell',bell=bell,gate=[10000,0,24,180],open_seconds=4)]
  c['control_plan']=c['control_plan'][:next(j+1 for j,p in enumerate(c['control_plan'])if p['op']=='shoot'and p.get('aim_cell',{}).get('kind')=='bell')]
  c.pop('challenge_requirements',None);probes.append(c);targets[c['id']]=bell
 (out/'protocol.json').write_text(json.dumps(dict(scope='Calibration discovery; not holdout',probes=len(probes),bell_offset_from_measured_second_muzzle=[-180,80],reason='Reactive aim hit both targets but an elevated bell drove downward recoil under timing error; derive a lower target and remeasure the landing, without changing player/enemy physics'),indent=2))
 for c,r,ev in engine.run(probes,'relay-flight'):
  rows.append(dict(id=c['id'],stage='flight',shots=r.get('shots'),reason=r['reason'],evidence=ev))
  for landing in materialize(c,r):
   grown=enemy_bell_gear(landing,r,len(candidates),bell_position=targets[c['id']]);grown['synthesis']['input_policy']='real_target_bearing_then_independent_noise';grown['synthesis']['target_offset']=[-180,80];candidates.append(grown)
 qualified=[]
 for c,r,ev in engine.run(candidates,'relay-geometry'):
  p=purpose(c,r);rows.append(dict(id=c['id'],stage='geometry',ok=p['ok'],reason=r['reason'],purpose=p,evidence=ev))
  if p['ok']:qualified.append(dict(case=c,result=r,evidence=ev))
 for key,value in [('summary',dict(scope='Calibration discovery only',probes=len(probes),geometries=len(candidates),qualified=len(qualified),physics_cases=engine.sim.cases)),('rows',rows),('qualified',qualified)]:(out/(key+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2 if key=='summary'else None))
 print(json.dumps(dict(probes=len(probes),geometries=len(candidates),qualified=len(qualified))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
