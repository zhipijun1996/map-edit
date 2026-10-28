import argparse,copy,json,math
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
HERE=Path(__file__).parent
def cases():
 out=[rules.candidate('B'),rules.candidate('C')]
 c=rules.candidate('C');s=next(q for q in c['control_plan']if q.get('aim_cell',{}).get('receiver')=='second');s.pop('aim_cell');s['direction']=[-.25,math.sqrt(1-.25**2)];c['id']+='-omit-second-freegun';out.append(c)
 c=rules.candidate('B');c['control_plan'][4]=cmd('wait');c['id']+='-omit-first';out.append(c)
 c=rules.candidate('C');b=rules.branch('C');c['control_plan']=rules.prefix()+[cmd('axis',value=1),wait_x(680),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence',receiver='second')),cmd('wait',16),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.25,math.sqrt(1-.25**2)])]+b[5:];c['id']+='-ground-stage2-extra-freegun';out.append(c)
 c=rules.candidate('C');pre=rules.prefix()[:11];pre[10]=cmd('shoot',direction=[.8,.6]);c['control_plan']=pre+[cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),wait_x(400),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.3,math.sqrt(.91)]),settle(576),ground(),cmd('wait',8)]+rules.branch('C');c['id']+='-missM-recovery-attempt';out.append(c)
 out.extend([rules.candidate('B',4),rules.candidate('C',4)])
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(k)for k in ['B','C']]))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':write(out/'preflight.json',checks);raise ValueError('originalpreflightrejected0physics')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run(cases(),'first-eight-real-sequence-fork'):
  q=rules.purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],M=q['causal']['M_first'],relay=q['causal']['branch_first_landing'],final=q['causal']['final_sequence'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_candidates=0))
if __name__=='__main__':main()
