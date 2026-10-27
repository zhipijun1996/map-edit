"""Few real pre-stop/no-stop controls before any wider production work."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def candidate(kind):
 c=rules.candidate(0,0);p=c['control_plan'];shots=[i for i,q in enumerate(p)if q['op']=='shoot'];park=shots[1]
 if kind.startswith('no-stop'):
  p[park]=cmd('wait');p[park+1]=cmd('wait',0 if kind=='no-stop-immediate'else 8)
 else:
  delay=15 if kind=='shore-prestop-15'else 100
  p=[cmd('axis',value=1),wait_x(130),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='deck-control')),cmd('wait',delay),cmd('shoot',aim_target=[1320,538]),cmd('axis',value=1),wait_x(1260),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,.8660254038]),settle(1640,0)]
 c['control_plan']=p;c['id']+='-counter-'+kind;c['counterexample_kind']=kind
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(k)for k in ['no-stop-immediate','no-stop-wait8','shore-prestop-15','shore-prestop-100']],'cheap-controls'):
  q=common.checked_purpose(type('Core',(),{'purpose':staticmethod(rules.core_purpose)}),c,r);v=dict(case=c,core_purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],core=q['ok'],reasons=q['reasons'],actual=v['actual'],final_dock=q['causal']['final_dock'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_candidates=0,scope='sameB/rewardcomparedwithactualpersistentgatecondition; doesnotassertparkingnecessary'))
if __name__=='__main__':main()
