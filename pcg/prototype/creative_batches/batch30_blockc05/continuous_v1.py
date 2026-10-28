"""Four fixed same-world cases; never a substitute for family qualification."""
import argparse,copy,json
from pathlib import Path
from . import api_v1 as api
from pcg.prototype.creative_batches.batch30_c05.recovery_v1 import purpose as original_purpose
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def missed_near():
 c=api.layouts(api.RECIPES[0],0)[1];source=copy.deepcopy(c['control_plan']);c['id']+='-missed-near'
 c['control_plan']=source[:16]+[wait_x(690),cmd('axis',value=0),cmd('wait',30)]+source[16:]
 c['validation_fixture']=dict(kind='same_world_missed_near_departure_continues_far',no_module_enrollment=True,no_reset=True)
 return c

def failed_selector():
 c=api.layouts(api.RECIPES[0],0)[1];source=copy.deepcopy(c['control_plan']);i=next(i for i,q in enumerate(source)if q.get('aim_cell',{}).get('id')=='station-selector')
 c['id']+='-failed-selector-pillar';c['max_frames']=2400
 c['control_plan']=source[:i]+[cmd('shoot',direction=[-1,0]),settle(1008),cmd('wait',90),ground(),settle(920),wait_x(924,-1),ground(),cmd('wait',20),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),cmd('wait',8),settle(1020),wait_x(1016),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),cmd('wait',0),settle(1256,6)]
 c['validation_fixture']=dict(kind='same_world_failed_selector_to_original_pillar_to_far_exit',no_module_enrollment=True,no_reset=True)
 return c

def purpose(c,r):
 q=api.purpose(c,r);old=original_purpose(c,r)
 q['reasons']+=old['reasons'];q['causal']['continuous']=old['causal'];q['ok']=not q['reasons'];return q

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutablecontinuousrun')
 deps=[Path(__file__),HERE/'continuous-protocol-v1.json',Path(api.__file__),*api.SOURCE_DEPENDENCIES,HERE.parent/'batch30_c05/recovery_v1.py']
 engine=WorkshopEngine(out,extra_sources=deps,runner_script=api.RUNNER_SCRIPT);bases=[missed_near(),failed_selector()];rows=[]
 for c,r,e in engine.run(bases+[instantiate(c,271128306,'mild',0)for c in bases],'same-world-no-reset'):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=e,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'])),flush=True)
 write(out/'summary.json',dict(actual_cases=engine.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0,qualification='exactsmallcontinuousfixture_only'))

if __name__=='__main__':main()
