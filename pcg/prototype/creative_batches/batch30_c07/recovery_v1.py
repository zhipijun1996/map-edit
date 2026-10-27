import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from .probe_v1 import compact
from .counter_v3 import external
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def candidate(control=0):
 c=rules.candidate(0,1);c['id']+=f'-recovery-first-miss-c{control}';edge=[700,730,750][control]
 c['control_plan']=[*c['control_plan'][:2],cmd('shoot',direction=[1,0]),cmd('axis',value=0,after=6),cmd('wait',75),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(edge),cmd('jump'),cmd('jump_release',32),settle(820),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',32),settle(820),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),settle(650,8)]
 c['max_frames']=2200;c['validation_fixture']=dict(kind='first_miss_floor_rightstep_exit_same_world',canonical_world_state_not_claimed=True,no_module_enrollment=True)
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not external(c,r):why.append('same_reward_safe_goal_missing')
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 floor=[f for f in fs if shots and f['frame']>shots[0]['frame']and f.get('grounded')and f.get('support_id')=='Platform3']
 if not floor:why.append('actual_failed_shot_recovery_floor_missing')
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id']=='brake-pair'),{})
 if pair.get('switch_count')!=0:why.append('first_shot_did_not_really_miss')
 supports={f.get('support_id')for f in fs if f.get('grounded')}
 if not {'Platform5','Platform6'}<=supports:why.append('actual_original_recovery_steps_missing')
 return dict(ok=not why,reasons=why,causal=dict(recovery_floor_frames=len(floor),actual_supports=sorted(str(v)for v in supports),final_pair=pair,canonical_exit_world=False),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();rows=[];chosen=[]
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v1.json',HERE/'probe_v1.py',HERE/'counter_v3.py',HERE/'alternatives_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT)
 for c,r,e in engine.run([candidate(k)for k in range(3)],'first-miss-recovery-clean'):
  q=purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']and not chosen:chosen.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],causal=q['causal'],last=rows[-1]['actual']['last'],shots=r.get('shots'),jumps=r.get('jumps'))),flush=True)
 write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in chosen],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031301,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)],'first-miss-recovery-perturb'):
  q=purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
