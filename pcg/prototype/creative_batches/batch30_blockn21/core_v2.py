import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from .core_v1 import cases as first_cases
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
HERE=Path(__file__).parent
def cases():
 out=[]
 for i,old in enumerate(first_cases()):
  target=old['route_spec']['to_port'];delay=old['rule_parameters']['branch_shot_delay'];c=rules.candidate(target,delay)
  if i in [0,1,6,7]:out.append(c);continue
  suffix=old['id'].split('-d0',1)[1];c['id']+=suffix
  if i==5:
   p=rules.prefix()[:15];p[14]=cmd('shoot',direction=[.8,.6]);c['control_plan']=p+copy.deepcopy(old['control_plan'][11:])
  else:
   c['control_plan']=rules.prefix()+copy.deepcopy(old['control_plan'][14:])
   if i==3:c['control_plan'][4]=cmd('wait')
  out.append(c)
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(k)for k in ['B','C']]))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':write(out/'preflight.json',checks);raise ValueError('originalpreflightrejected0physics')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'core_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run(cases(),'last-rule-eight-real-sequence-fork'):
  q=rules.purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],M=q['causal']['M_first'],relay=q['causal']['branch_first_landing'],final=q['causal']['final_sequence'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=8,new_candidates=0))
if __name__=='__main__':main()
