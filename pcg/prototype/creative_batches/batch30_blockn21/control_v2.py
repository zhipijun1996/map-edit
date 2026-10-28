"""B rises outside the upper corner before real recoil moves it inward."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from . import control_v1 as original
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def candidate(target='B',delay=0):
 if target=='C':return original.candidate(2 if delay==0 else 3)
 if target!='B'or delay not in [0,4]:raise ValueError('outside two registered verticalB controls')
 c=rules.candidate(target,delay);b=rules.branch(target,delay);b[2:2]=[cmd('axis',value=0),ground(),cmd('wait',8)];out=[]
 for q in rules.prefix()+b:
  q=copy.deepcopy(q)
  if q['op']!='settle'or q['target_x']==24:out.append(q);continue
  if q['target_x']==576:out +=[cmd('axis',value=1),wait_x(576),cmd('axis',value=0),ground()]
  elif q['target_x']==384:out +=[cmd('axis',value=0),cmd('wait',10),cmd('axis',value=-1),wait_x(384,-1),cmd('axis',value=0),ground()]
  else:raise ValueError('outside nonterminalBstopdomain')
 c['control_plan']=out;c['id']+='-vertical-control-v2';c['rule_parameters'].update(program_source=str(Path(__file__).relative_to(HERE.parents[3])),program_version=2,vertical_before_inward_recoil=True)
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'control_v1.py',HERE/'control-flow-domain-v1.json',HERE/'control-flow-domain-v2.json',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate('B',d)for d in [0,4]],'two-real-verticalB-controls'):
  m=original.measured(c,r);v=dict(case=c,measured=m,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],eligible=m['eligible'],margin=m['minimum_fullbody_margin'],reasons=m['purpose']['reasons'],actual=v['actual'],causal=m['purpose']['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=20,new_candidates=0,eligible=sum(v['measured']['eligible']for v in rows)))
if __name__=='__main__':main()
