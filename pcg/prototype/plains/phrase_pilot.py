"""Bounded discovery for longer plains decisions. No holdout use here."""
import argparse,json,collections
from .engine import ROOT,PlainsEngine
from .phrases import motion_proposals,materialize_phrase,enemy_bell_gear
from .synthesis import identity
from .evaluation import purpose

def run(name,bases):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);source=json.loads((ROOT/'results'/bases/'qualified.json').read_text())
 probes=motion_proposals(source);candidates=[];rows=[]
 (out/'protocol.json').write_text(json.dumps(dict(scope='Discovery only; no independent holdout',source_bases=bases,flight_probes=len(probes),selected_bell_bases=2,enemy_bases=2,geometry_variants_per_flight=1),indent=2))
 for c,r,ev in engine.run(probes,'phrase-motion'):
  child=materialize_phrase(c,r);rows.append(dict(id=c['id'],stage='motion',reason=r['reason'],shots=r.get('shots'),jumps=r.get('jumps'),materialized=child is not None,evidence=ev))
  if child:candidates.append(child)
 enemies=sorted((e for e in source if e['case']['family']=='enemy_refund'),key=lambda e:identity(e['case']))[:2]
 for i,e in enumerate(enemies):
  child=enemy_bell_gear(e['case'],e['result'],i)
  if child:candidates.append(child)
 candidates=list({identity(c):c for c in candidates}.values());qualified=[]
 for c,r,ev in engine.run(candidates,'phrase-geometry'):
  p=purpose(c,r);rows.append(dict(id=c['id'],stage='geometry',reason=r['reason'],ok=p['ok'],purpose=p,evidence=ev))
  if p['ok']:qualified.append(dict(case=c,result=r,evidence=ev))
 summary=dict(scope='Discovery/calibration only; no human fun rating or approval',motion_probes=len(probes),geometries=len(candidates),qualified=len(qualified),families=dict(collections.Counter(e['case']['family']for e in qualified)),physics_cases=engine.sim.cases)
 for file,data in [('summary',summary),('rows',rows),('candidates',dict(cases=candidates)),('qualified',qualified)]:(out/(file+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2 if file=='summary'else None))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--bases',required=True);a=p.parse_args();run(a.name,a.bases)
