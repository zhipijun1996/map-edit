"""Independent exact same-world foldback fixture, no fresh phase/resource writes."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

def candidate():
 c=rules.candidate(0,'out');c['id']+='-roundtrip-original-floor';dx=c['rule_parameters']['translation'][0]
 c['control_plan']=copy.deepcopy(c['control_plan'][:-1])+[wait_x(997),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=-1),wait_x(285+dx,-1),cmd('axis',value=0),ground(),cmd('wait',20),cmd('jump'),cmd('jump_release',20),cmd('shoot',4,direction=[.5,.8660254037844386]),cmd('axis',9,value=-1),settle(-104,6)]
 c['goal']=[-129,458,50,8];c['max_frames']=1500;c['transition_kind']='carrier-original-floor-roundtrip';return c

def purpose(c,r):
 q=rules.purpose(c,r);fs=r.get('frames',[]);atb=[f for f in fs if f['grounded']and abs(f['x']-1000)<=7 and abs(f['y']-334)<=1 and abs(f['vx'])<=1];bottom=[f for f in fs if f['grounded']and abs(f['y']-674)<1 and atb and f['frame']>atb[0]['frame']]
 q['causal'].update(visited_B_stable_frames=len(atb),original_bottom_after_B_frames=len(bottom),no_world_reset=not r.get('returns'))
 if len(atb)<12:q['reasons'].append('B_not_stable_12_frames')
 if not bottom:q['reasons'].append('original_floor_not_visited_after_B')
 if r.get('returns'):q['reasons'].append('unexpected_world_reset')
 q['ok']=not q['reasons'];return q

def main():
 c=candidate();e=WorkshopEngine(ROOT/'results/workshop-batch30-blocka2-roundtrip-clean-v1',extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT)
 rows=[]
 for c,r,ev in e.run([c],'roundtrip'):
  p=purpose(c,r);row=dict(id=c['id'],purpose=p,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,general_foldback='UNKNOWN'))
if __name__=='__main__':main()
