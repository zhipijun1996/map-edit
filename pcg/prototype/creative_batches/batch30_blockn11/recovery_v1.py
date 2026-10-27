"""Perturb the actually observed paid fall-to-original-floor / jump-shot recovery."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 choices=json.loads((HERE/'control-selection-v1.json').read_text())['controls'];bases=[]
 for i,v in choices.items():
  c=rules.candidate(int(i),v['width'],v['control']);c=next(q for q in alternatives(c)if q['counterexample_kind']=='bottom-paid-jump-shot');bases.append(c)
 cases=[instantiate(c,271130122,l,k)for c in bases for l in ['mild','moderate']for k in [0,1]]
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'paid-floor-recovery'):
  q=common.checked_purpose(rules,c,r);floor=c['platforms'][2]
  realfloor=[f for f in r.get('frames',[])if f.get('grounded')and f.get('support_id')=='Platform2'and abs(f['y']+18-floor[1])<1]
  if not realfloor:q['reasons'].append('actual_original_floor_landing_missing')
  q['causal']['actual_floor_support_frames']=[f['frame']for f in realfloor];q['ok']=not q['reasons']
  v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),scope='boundedpaidfloorrecovery8perturbations; nooriginalregular/held/genericretrycertification',new_candidates=0))
if __name__=='__main__':main()
