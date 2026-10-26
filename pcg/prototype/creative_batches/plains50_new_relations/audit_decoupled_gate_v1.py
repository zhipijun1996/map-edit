"""Supplemental cheap setup alternatives requested by independent AI critic."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.production_v1 import compiler,purpose
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x
HERE=Path(__file__).parent

def candidates():
 out=[]
 for base in compiler({})['cases'][::2]:
  for x in [80,180,220]:
   for delay in [0,30]:
    c=copy.deepcopy(base);c['id']+='-counter-ground-preopen-then-airbrake-'+str(x)+'-'+str(delay);c['counterexample_kind']='ground-preopen-then-airbrake';c['control_plan']=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='pocket-bell')),cmd('wait',after=delay)]+copy.deepcopy(base['control_plan']);out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-brake-decoupling-audit-v1';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'production_v1.py',HERE/'probe_v1.py']);rows=[]
 for c,r,ev in e.run(candidates(),'critic-decoupling-policies'):
  row=dict(id=c['id'],safe_stable=r.get('ok'),purpose=purpose(c,r),shots=r.get('shots'),evidence=ev);rows.append(row);print(json.dumps(dict(id=c['id'],ok=r.get('ok'),purpose=row['purpose']['ok'])),flush=True)
 (out/'summary.json').write_text(json.dumps(dict(schema='pcg/supplemental-counterexample-audit/v1',cases=len(rows),safe_stable=sum(bool(r['safe_stable'])for r in rows),scope='same-gun necessity remains finite evidence; canonical witnesses are single-shot, separate setup strategies are tested explicitly',rows=rows),indent=2))
