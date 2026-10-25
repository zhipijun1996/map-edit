import json,copy,importlib.util
from pathlib import Path
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd,wait_x,settle
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('resource_v6',HERE/'recipes-v6.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=json.loads((ROOT/'results/workshop-creative-resource-routes-v6/round-01/source-candidates.json').read_text())['cases'][0]
cs=[]
for x in [245,260,275]:
 for delay in [0,4,8,12,18,26,34]:
  c=copy.deepcopy(base);c['id']+='-counter-low-ray-'+str(x)+'-'+str(delay);c['counterexample_kind']='low-ray-timing'
  c['control_plan']=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',delay,aim_cell=dict(kind='bell',id='under-key')),settle(385,6)];cs.append(c)
eng=WorkshopEngine(ROOT/'results/workshop-creative-resource-routes-v6-deep-counters',extra_sources=[Path(__file__),HERE/'recipes-v6.py',HERE/'runner-v1.gd'],runner_script=HERE/'runner-v1.gd')
rows=[]
for c,r,e in eng.run(cs,'deep-counter'):
 p=m.purpose(c,r);row=dict(id=c['id'],safe_stable=r.get('ok'),purpose=p,evidence=e)
 rows.append(row)
 print(c['id'],r.get('ok'),p['ok'],p['reasons'],flush=True)
(eng.out/'summary.json').write_text(json.dumps(rows,indent=2))
