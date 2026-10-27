"""Exact same actor/world delayed closed-door return; two clean fixtures only."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .door_metrics_v1 import inspect
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def candidate(i):
 controls=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
 c=rules.candidate(i,controls[f'{i}/outbound'],'outbound');back=rules.candidate(i,controls[f'{i}/return'],'return')
 c['control_plan']=c['control_plan'][:-1]+[wait_x(741),cmd('axis',value=0),ground(),cmd('wait',110)]+back['control_plan']
 c['id']+='-sameworld-delayed-return';c['goal']=[17,330,14,8];c['max_frames']=2400
 c['route_spec']=dict(id='roundtrip-fixture',from_port='A',to_port='A',role='return',via_ports=['B'],required_rewards=[],require_bell=True)
 c['validation_fixture']=dict(kind='sameworld_A_B_A_closed_gate',actual_goal_port='A',definition_marker_port='B',marker_is_not_route_destination=True,no_module_enrollment=True,no_reset=True)
 return c

def purpose(c,r):
 q=common.checked_purpose(rules,c,r);fs=r.get('frames',[])
 visits=[f for f in fs if f.get('grounded')and abs(f['x']-744)<=7 and abs(f['y']-334)<1]
 start=visits[-1]['frame']if visits else len(fs)
 back=inspect(c,r,-1,start=start)
 bclosed=[f['frame']for f in visits if not f.get('plains',{}).get('bells',[{}])[0].get('open',True)]
 refill=[f['frame']for f in visits if f.get('shot_charges')==1 and f.get('shot_cooldown')==0]
 if not visits:q['reasons'].append('actual_B_dock_not_visited')
 if not bclosed:q['reasons'].append('actual_B_delay_until_gate_closed_missing')
 if not refill:q['reasons'].append('actual_B_ground_refill_cooldown_missing')
 if not back['actual_bell_open_events']or not back['body_door_frames']or back['full_body_clear_frame']is None:q['reasons'].append('actual_closeddoor_return_reopen_and_fullbody_missing')
 if back['closed_during_body_overlap']:q['reasons'].append('actual_closed_gate_on_return_body')
 q['causal'].update(B_visit_frames=[f['frame']for f in visits],B_closed_frames=bclosed,B_refill_frames=refill,actual_return_gate=back,scene_reconstruction=False,final_resources={k:(fs[-1]if fs else{}).get(k)for k in ['energy','shot_charges','shot_cooldown','actor_epoch']})
 q['ok']=not q['reasons'];return q

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutablefixture')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(i)for i in [0,1]],'delayedcloseddoorreturn'):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0,scope='two exact clean continuous fixtures; generic composition UNKNOWN'))

if __name__=='__main__':main()
