"""Separate same-world purpose evidence; never a standard self-route."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_blockn13 import return_v2 as parent_return
from pcg.prototype.creative_batches.batch30_blockn13 import rules_v2 as parent_rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def candidate(control):
 c=rules.candidate(0,control)
 old=parent_return.candidate(True,0)
 normal=parent_rules.candidate(0,0)
 c['control_plan']=c['control_plan'][:-1]+old['control_plan'][len(normal['control_plan'])-1:]
 c['goal']=old['goal'];c['max_frames']=2200
 c['id']+='-sameworld-A-B-A'
 c['validation_fixture']=old['validation_fixture']
 return c
def purpose(c,r):
 q=parent_return.purpose(c,r)
 visits=[f for f in r.get('frames',[])if f.get('grounded')and abs(f['x']-1640)<7 and abs(f['y']-462)<1]
 retained=[f['frame']for f in visits if any(d['occupied']and d['open']for d in f.get('n13',{}).get('docks',[]))and any(not p['running']for p in f.get('n13',{}).get('carriers',[]))]
 if len(retained)<6:q['reasons'].append('actual_B_stop_and_held_dock_visit_missing')
 q['causal']['actual_B_held_dock_frames']=retained
 q['ok']=not q['reasons']
 return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 control=json.loads((HERE/'control-selection-v1.json').read_text())['control'];c=candidate(control)
 cases=[c]+[instantiate(c,271130228,l,k)for l in ['mild','moderate']for k in range(3)]
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(parent_return.__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'sameworld-return'):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],return_dx=q['causal']['return_carrier_transport_dx'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),new_candidates=0,qualification='finite7caseSameWorldEvidenceOnly; nofullregular/held/freshB-Aclaim'))
if __name__=='__main__':main()
