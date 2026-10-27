import json
from pathlib import Path
from . import rules_v1 as rules,cell_probe_v1 as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

def cases():
 cs=old.cases()
 for c in cs:c.update(id=c['id'].replace('-v1-','-v2-'),entry_port=[-400,882],exit_port=[-350,882],fixture_scope='Explicit carrier unit initial spawn; not static port ingress evidence')
 return cs

def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn03-cell-v2',extra_sources=[Path(__file__),Path(old.__file__),Path(__file__).parent/'cell_fixture-repair-v2.json',*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases(),'cell'):
  row=dict(id=c['id'],check=old.check(c,r),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
