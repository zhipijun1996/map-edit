"""Last-rule full ingress plus exact blocked-ray controls, no lucky phase reset."""
import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
HERE=Path(__file__).parent
def cases():
 out=[rules.candidate('B'),rules.candidate('C'),rules.candidate('B',True),rules.candidate('C',True),rules.candidate('B',True,.1),rules.candidate('C',True,.82)]
 for c in out[4:]:c['id']+='-blocked-phase'
 c=rules.candidate('C');prefix=rules.prefix();c['control_plan']=prefix+[rules.phase(.4),cmd('shoot',aim_cell=dict(kind='bell',id='high-C')),cmd('wait',16),cmd('axis',value=1),wait_x(800),cmd('jump'),cmd('jump_release',20),settle(1256),ground(),cmd('wait',10)];c['id']+='-ground-prefire';out.append(c)
 c=rules.candidate('C');s=next(q for q in c['control_plan']if q['op']=='shoot');s.pop('aim_cell');s['direction']=[-1,0];c['id']+='-freegun';out.append(c)
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(k)for k in ['B','C']]))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':write(out/'preflight.json',checks);raise ValueError('originalpreflightrejected0physics')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run(cases(),'last-rule-full-ingress-core'):
  q=rules.purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],opens=q['causal']['actual_bell_open'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=8,new_candidates=0))
if __name__=='__main__':main()
