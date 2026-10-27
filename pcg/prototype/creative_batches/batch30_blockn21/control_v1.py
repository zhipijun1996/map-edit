"""Compile nonterminal stops into original inputs; no runtime or world edits."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
DOMAIN=[('B',0),('B',4),('C',0),('C',4)]
def compile_plan(c):
 out=[]
 for q in copy.deepcopy(c['control_plan']):
  if q['op']!='settle'or q['target_x']==c['exit_port'][0]:out.append(q);continue
  x=q['target_x']
  if x in [576,896]:out +=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),ground()]
  elif x==384:out +=[cmd('axis',value=0),cmd('wait',10),cmd('axis',value=1),wait_x(384),cmd('axis',value=0),ground()]
  else:raise ValueError('outside registered nonterminal stop compiler')
 return out
def candidate(index):
 target,delay=DOMAIN[index];c=rules.candidate(target,delay);c['control_plan']=compile_plan(c);c['id']+='-controlflow-v1';c['rule_parameters'].update(program_source=str(Path(__file__).relative_to(HERE.parents[3])),program_version=1,control_index=index)
 return c
def measured(c,r):
 q=rules.purpose(c,r);values={}
 for name,land,rect in [('M',q['causal']['M_first'],c['platforms'][2]),('branch',q['causal']['branch_first_landing'],c['platforms'][3 if c['route_spec']['to_port']=='B'else 4])]:
  if land:values[name+'_left']=land['x']-12-rect[0];values[name+'_right']=rect[0]+rect[2]-land['x']-12
 score=min(values.values())if len(values)==4 else None
 return dict(eligible=bool(q['ok']and score is not None and score>=0),minimum_fullbody_margin=score,margins=values,purpose=q)
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'control-flow-domain-v1.json',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(k)for k in range(4)],'four-real-controlflow-repairs'):
  m=measured(c,r);v=dict(case=c,measured=m,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],eligible=m['eligible'],margin=m['minimum_fullbody_margin'],reasons=m['purpose']['reasons'],actual=v['actual'],causal=m['purpose']['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=16,new_candidates=0,eligible=sum(v['measured']['eligible']for v in rows)))
if __name__=='__main__':main()
