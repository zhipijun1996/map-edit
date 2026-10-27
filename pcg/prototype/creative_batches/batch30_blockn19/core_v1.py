"""First eight actual tests, including honest non-enrollment mechanism/return fixtures."""
import argparse,copy,json,math
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def cases():
 out=[rules.candidate(0),rules.candidate(1)];base=rules.candidate(0)
 def add(kind,plan):
  c=copy.deepcopy(base);c['id']+='-counter-'+kind;c['counterexample_kind']=kind;c['control_plan']=plan;out.append(c);return c
 add('zero-gun-bridge-edge',[cmd('axis',value=1),wait_x(540),cmd('jump'),cmd('jump_release',32),settle(1000),ground()])
 common_tail=copy.deepcopy(base['control_plan'][7:])
 add('safe-shore-preopen',[cmd('axis',value=1),wait_x(280),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair')),cmd('wait',20),cmd('axis',value=1),wait_x(500),cmd('axis',value=0)]+common_tail)
 p=copy.deepcopy(base['control_plan']);p[9]=cmd('wait');add('omit-second-switch',p)
 recovery=copy.deepcopy(base['control_plan'][:6])+[cmd('axis',value=-1),cmd('wait',48),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.3,math.sqrt(.91)]),wait_x(528),cmd('axis',value=0),ground(),cmd('wait',8)]+copy.deepcopy(base['control_plan'][9:])
 add('miss-M-real-stair-recovery',recovery)
 c=add('closing-body-cell-control',[cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair')),cmd('wait',50)])
 c['latches'][0]['initial_open']='A';c['spawn']=[448,334];c['entry_port']=[448,334];c['max_frames']=70;c['validation_fixture']=dict(kind='actual_freefall_body_blocks_closing_A',no_module_enrollment=True,different_initial_gate_state=True);c['goal']=[100000,0,10,10]
 back=[wait_x(998),cmd('axis',value=0),ground(),cmd('wait',12),cmd('axis',value=-1),wait_x(870,-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.3,math.sqrt(.91)]),wait_x(540,-1),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair',receiver='access')),cmd('wait',20),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.4,math.sqrt(.84)]),settle(24),ground(),cmd('wait',10)]
 c=add('sameworld-return-attempt',copy.deepcopy(base['control_plan'][:15])+back);c['goal']=[17,330,14,8];c['max_frames']=2200;c['validation_fixture']=dict(kind='actual_A_B_A_return_attempt',no_module_enrollment=True,no_fresh_B_A_claim=True)
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(0)]))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':
  write(out/'preflight.json',checks);raise ValueError('original syntax/Block preflight rejected before physics')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 write(out/'preflight.json',checks)
 for c,r,ev in e.run(cases(),'first-eight'):
  q=common.checked_purpose(rules,c,r);external=rules.outcome(c,r)
  v=dict(case=c,purpose=q,external=external,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],external=external['ok'],actual=v['actual'],pair=q['causal']['pair_final'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_candidates=0,scope='first8actualcore/counter/component/return; nofullqualification'))
if __name__=='__main__':main()
