"""Use the current real target position, keep the same aim/timing perturbations."""
import argparse,copy,json
from .engine import ROOT,PlainsEngine
from .evaluation import purpose

def run(name,source):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);old=json.loads((ROOT/'results'/source/'qualified.json').read_text());cases=[]
 for e in old:
  c=copy.deepcopy(e['case']);c['id']+='-reactive';shots=[p for p in c['control_plan']if p['op']=='shoot'];shots[0]['aim_cell']=dict(kind='enemy',id=c['enemies'][0]['id']);shots[1]['aim_cell']=dict(kind='bell',id=c['latches'][0]['id']);c['synthesis']['input_policy']='current_real_target_bearing_then_independent_aim_noise';cases.append(c)
 rows=[];qualified=[]
 for c,r,ev in engine.run(cases,'reactive-geometry'):
  p=purpose(c,r);rows.append(dict(id=c['id'],ok=p['ok'],reason=r['reason'],purpose=p,evidence=ev))
  if p['ok']:qualified.append(dict(case=c,result=r,evidence=ev))
 for key,value in [('summary',dict(scope='Calibration-only input-policy repair; not heldout',candidates=len(cases),qualified=len(qualified),physics_cases=engine.sim.cases)),('rows',rows),('qualified',qualified)]:(out/(key+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2 if key=='summary'else None))
 print(json.dumps(dict(candidates=len(cases),qualified=len(qualified))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
