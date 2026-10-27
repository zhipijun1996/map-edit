import argparse,json
from pathlib import Path
from . import api_v1 as api
from .validation_v5 import dead_check,rest
from .repair_v4 import compact
from pcg.prototype.workshop.rules import cmd,wait_x
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def dead_fixture(control=0):
 c=api.layouts(api.RECIPES[0],0)[1];x,gap=[(60,20),(60,22),(90,22)][control]
 before=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',10),cmd('axis',value=-1 if x<80 else 1),wait_x(x,-1 if x<80 else 1),*rest(),cmd('axis',value=-1),cmd('shoot',direction=[-1,0]),cmd('shoot',gap,direction=[-1,0]),cmd('shoot',gap,direction=[-1,0]),cmd('wait',12),wait_x(90,-1),*rest(),cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',20)]
 c['id']+=f'-horizontal-real-clear-c{control}';c['control_plan']=before+c['control_plan'];c['max_frames']=2200;c['validation_fixture']=dict(kind='actual3HP_horizontal_clear_then_staged',control=control,no_module_enrollment=True);return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v4.json',HERE/'validation_v5.py',HERE/'repair_v4.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];clean=[]
 for c,r,e in engine.run([dead_fixture(k)for k in range(3)],'horizontal-clear-clean'):
  q=dead_check(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],hp=r.get('hp'),enemy=r.get('plains',{}).get('enemies'),shots=r.get('shots'))),flush=True)
 chosen=clean[:1];write(engine.out/'selection-before-mild.json',dict(ids=[c['id']for c in chosen],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031101,'mild',k)for c in chosen for k in range(3)],'horizontal-clear-mild'):
  q=dead_check(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'validation-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,total=214+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
