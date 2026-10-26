"""Input repair only: distinct Definition port and clear air-test gates."""
import argparse,copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from . import probe_v1 as old
HERE=Path(__file__).parent

def cases():
 out=old.cases()
 for c in out:
  c['id']+='-v2'
  if c['probe_kind']in ['initial','twice']:
   c['exit_port']=[120,420];c['goal']=[95,416,50,8];c['control_plan'][-1]['target_x']=120
  if c['probe_kind']=='airborne':c['latches'][0].update(gate=[750,250,24,188],paired_gate=[1050,250,24,188])
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(old.__file__)]+old.SOURCE_DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,b in e.run(cases(),'cell-probe'):
  q=old.check(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows))
if __name__=='__main__':main()
