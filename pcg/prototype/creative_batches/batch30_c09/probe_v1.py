import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
def compact(c,r,e,q):
 return dict(case=c,purpose=q,evidence=e,actual=dict(ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),last={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']},commands=r.get('fired_commands'),key_frames=[{k:f.get(k)for k in ['frame','x','y','vx','vy','grounded','support_id','shot_charges']}for f in r.get('frames',[])[::40]]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,e in engine.run([rules.candidate(0,k)for k in range(4)],'sameworld-loop-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],causal=q['causal'],last=rows[-1]['actual']['last'],shots=r.get('shots'),jumps=r.get('jumps'))),flush=True)
 write(engine.out/'probe-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
