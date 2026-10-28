"""Same first-eight falsifiers on final rule, with old failed evidence retained."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from .core_v1 import cases as old_cases
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def cases():
 out=[]
 for i,old in enumerate(old_cases()):
  c=rules.candidate(1 if i==1 else 0)
  if i<2:out.append(c);continue
  for k in ['counterexample_kind','validation_fixture','goal','max_frames','spawn']:
   if k in old:c[k]=copy.deepcopy(old[k])
  if i==6:c['latches'][0]['initial_open']='A'
  c['id']+='-counter-'+c['counterexample_kind'];c['control_plan']=rules.access_position(old['control_plan']);out.append(c)
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(0)]))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':write(out/'preflight.json',checks);raise ValueError('original preflight rejected before physics')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'core_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run(cases(),'last-rule-eight'):
  q=common.checked_purpose(rules,c,r);external=rules.outcome(c,r);pairs=r.get('workshop',{}).get('paired_gates',[])
  v=dict(case=c,purpose=q,external=external,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},actual_pair=pairs);rows.append(v);write(out/'results.json',rows)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],external=external['ok'],actual=v['actual'],pair=pairs)),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=8,new_candidates=0,scope='lastRulecore; reverseUNKNOWNunlessindependentlyqualified'))
if __name__=='__main__':main()
