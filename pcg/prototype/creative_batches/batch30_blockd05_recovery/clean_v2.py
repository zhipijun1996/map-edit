import json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockd05-independent-recovery-clean-v2',extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([rules.fixture(i,k)for i in [0,1]for k in range(3)],'final-bounded-recovery-clean'):
  q=rules.purpose(c,r);shots=[f for f in r.get('frames',[])if any(v.get('type')=='shot'for v in f.get('accepted',[]))];st=shots[1]['frame']if len(shots)>1 else 99999;hop=[f for f in r.get('frames',[])if st<=f['frame']<st+90]
  row=dict(id=c['id'],case=c,purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},floor_hop_min_body_bottom=min((f['y']+18 for f in hop),default=None),original_parked_deck_top=353);rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,result=row['result'],floor_hop_min_body_bottom=row['floor_hop_min_body_bottom'])),flush=True)
 selected={}
 for i in [0,1]:
  good=[r for r in rows if r['case']['interface']==i and r['purpose']['ok']]
  if good:selected[str(i)]=min(r['case']['validation_fixture']['control']for r in good)
 write(e.out/'screen.json',dict(actual_cases=e.sim.cases,rows=rows,controls=selected,new_modules=0))
 write(HERE/'control-selection-v2.json',dict(schema='pcg/block-D05-recovery-control-selection/v2',controls=selected,selected_before_full_calibration=True,source_run=str(e.out.relative_to(ROOT.parent))))
if __name__=='__main__':main()
