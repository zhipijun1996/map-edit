"""Two actual same-world A->B->A fixtures; not artificial Module selfloops."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def candidate(interface):
 controls=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
 c=rules.candidate(interface,controls[f'{interface}/outbound'],'outbound');back=rules.candidate(interface,controls[f'{interface}/return'],'return');b=c['exit_port'][:]
 # Original persistent settle would override later axes. Arrive by actual
 # crossing/ground queries instead, preserving the same actor/world/resources.
 c['control_plan']=c['control_plan'][:-1]+[wait_x(b[0]-3),cmd('axis',value=0),ground(),cmd('wait',20)]+back['control_plan']
 c['id']+='-sameworld-roundtrip';c['goal']=[17,330,14,8];c['max_frames']=2200
 c['route_spec']=dict(id='roundtrip-fixture',from_port='A',to_port='A',role='return',via_ports=['B'],required_rewards=['visible-cache'],require_bell=False)
 c['validation_fixture']=dict(kind='sameworld_A_B_A',actual_goal_port='A',definition_marker_port='B',marker_is_not_route_destination=True,no_module_enrollment=True,no_reset=True,continuous_reward_once=8)
 return c

def purpose(c,r):
 q=common.checked_purpose(rules,c,r);fs=r.get('frames',[]);b=c['ports'][1]['position'];visits=[f for f in fs if f.get('grounded')and abs(f['x']-b[0])<=7 and abs(f['y']-b[1])<1]
 claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('id')=='visible-cache'and e.get('accepted')]
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 refill=[f for f in visits if f.get('shot_charges')==1 and f.get('shot_cooldown')==0]
 if not visits:q['reasons'].append('actual_intermediate_B_dock_not_visited')
 if not refill:q['reasons'].append('actual_B_grounded_resource_cooldown_not_restored')
 if len(claims)!=1 or r.get('workshop',{}).get('coins')!=8:q['reasons'].append('original_chest_not_exactly_once8')
 if len(shots)!=2:q['reasons'].append('actual_two_direction_recoil_not_witnessed')
 q['causal'].update(B_dock_visit_frames=[f['frame']for f in visits],B_actual_full_refill_frames=[f['frame']for f in refill],actual_accepted_claims=claims,actual_sameworld_shots=[dict(frame=f['frame'],shot_charges=f.get('shot_charges'),cooldown=f.get('shot_cooldown'))for f in shots],final_original_resources={k:(fs[-1]if fs else{}).get(k)for k in ['energy','shot_charges','shot_cooldown','actor_epoch']},scene_reconstruction=False)
 q['ok']=not q['reasons'];return q

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutablefixture')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(i)for i in [0,1]],'sameworldroundtrip'):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},coins=r.get('workshop',{}).get('coins'));rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],coins=v['coins'],causal=q['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0,qualification='two_exactcontinuouscleanfixtures; no genericreturn orperturbationclaim'))

if __name__=='__main__':main()
