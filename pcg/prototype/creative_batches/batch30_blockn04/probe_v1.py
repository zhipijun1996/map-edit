import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();cases=[rules.candidate('A',b,t)for t in rules.TIMERS for b in ['B','C']]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'initial-timer-clean'):
  q=rules.purpose(c,r);row=dict(id=c['id'],case=c,purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']});rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,result=row['result'])),flush=True)
 write(e.out/'screen.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
