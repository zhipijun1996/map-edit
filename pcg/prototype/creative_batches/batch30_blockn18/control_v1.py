"""Authorized four real shoot-position controls within the unchanged v2 world."""
import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
POSITIONS=[748,760,772,784]
def candidate(index):
 if index not in range(4):raise ValueError('outsideauthorizedfourBcontrols')
 c=rules.candidate('B');x=POSITIONS[index]
 c['control_plan']=rules.prefix()+[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),ground(),cmd('wait',8)]+rules.tail('B')
 c['id']+='-position-'+str(x);c['rule_parameters'].update(B_shoot_position=x,control_index=index,control_source=str(Path(__file__).relative_to(HERE.parents[3])))
 return c
def measured(c,r):
 q=rules.purpose(c,r);land=q['causal']['relay_first'];p=c['platforms'][3]
 values={'left':land['x']-12-p[0],'right':p[0]+p[2]-land['x']-12}if land else None
 return dict(eligible=bool(q['ok']and values and min(values.values())>=0),score=min(values.values())if values else None,actual_first_landing=land,fullbody_margins=values,purpose=q)
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'control-domain-v1.json',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(k)for k in range(4)],'authorized-four-real-Bshootpositions'):
  m=measured(c,r);v=dict(case=c,measured=m,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],eligible=m['eligible'],score=m['score'],reasons=m['purpose']['reasons'],actual=v['actual'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=16,new_candidates=0,eligible=sum(v['measured']['eligible']for v in rows)))
if __name__=='__main__':main()
