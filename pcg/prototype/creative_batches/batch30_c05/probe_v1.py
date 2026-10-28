import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
def compact(c,r,e,q):
 return dict(case=c,purpose=q,evidence=e,actual=dict(ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']},shots_at=[{k:f.get(k)for k in ['frame','x','y','grounded','shot_charges']}for f in r.get('frames',[])if any(a.get('type')=='shot'for a in f.get('accepted',[]))]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,e in engine.run([rules.candidate(0,k,route)for route in ['near','far']for k in range(4)],'branch-core-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],neutral_frames=q['causal']['neutral_carried_frames'],carried_dx=q['causal']['neutral_carried_dx'],last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']},shots=r.get('shots'))),flush=True)
 write(engine.out/'probe-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
