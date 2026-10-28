"""Real failed ingress, retained stair and vertical retry in the same world."""
import argparse,json,math
from pathlib import Path
from . import rules_v2 as rules
from . import control_v1 as old_control
from . import control_v2 as control
from .screen_v1 import DEPS
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def candidate(index=0):
 if index not in [0,1]:raise ValueError('onlytworegisteredmissMretrycontrols')
 c=control.candidate('C',0);pre=rules.prefix()[:15];pre[14]=cmd('shoot',direction=[-.9,-math.sqrt(.19)])
 shoot=[-.3,math.sqrt(.91)]if index==0 else[-.4,math.sqrt(.84)]
 back=[cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=-1),wait_x(400,-1),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=shoot),cmd('axis',value=1),wait_x(576),cmd('axis',value=0),ground(),cmd('wait',8)]
 c['control_plan']=old_control.compile_plan(dict(c,control_plan=pre+back+rules.branch('C',0)));c['id']=f'b30-blockn21-v2-A-C-missedM-recovery-c{index}'
 c['route_spec'].update(id='A-to-C-missedM-recovery',role='recovery');c['fixture_kind']='missedM-recovery';c['rule_parameters'].update(recovery_control=index,recovery_shot=shoot,program_source=str(Path(__file__).relative_to(HERE.parents[3])))
 return c
def purpose(c,r):
 q=rules.purpose(c,r);fs=r.get('frames',[]);M=q['causal']['M_first'];step=next((f for f in fs if M and f['frame']<M['frame']and f.get('grounded')and f.get('support_id')=='Platform7'),None)
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];miss=shots[1]if len(shots)>1 else None
 retry=next((f for f in shots if step and M and step['frame']<f['frame']<M['frame']),None)
 if not step or step.get('shot_charges',0)<1:q['reasons'].append('actual_retained_recovery_stair_resource_missing')
 if not miss or miss.get('grounded')or miss.get('shot_charges')!=0:q['reasons'].append('actual_failed_airshot_consumption_missing')
 if not retry or retry.get('grounded')or retry.get('shot_charges')!=0:q['reasons'].append('actual_vertical_retry_airshot_consumption_missing')
 q['causal'].update(actual_recovery_step=({k:step.get(k)for k in ['frame','x','y','support_id','shot_charges']}if step else None),actual_missed_shot=miss['frame']if miss else None,actual_retry_shot=retry['frame']if retry else None)
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if a.stage=='clean':cs=[candidate(i)for i in [0,1]]
 else:
  i=json.loads((HERE/'recovery-selection-v1.json').read_text())['control'];cs=[instantiate(candidate(i),271130231,l,k)for l in ['mild','moderate']for k in range(3)]
 deps=[Path(__file__),HERE/'recovery-protocol-v1.json',HERE/'screen_v1.py',*DEPS]
 if a.stage=='noise':deps.append(HERE/'recovery-selection-v1.json')
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'actual-missedM-recovery-'+a.stage):
  q=purpose(c,r);m=old_control.measured(c,r);eligible=q['ok']and m['minimum_fullbody_margin']is not None and m['minimum_fullbody_margin']>=0
  v=dict(case=c,purpose=q,eligible=eligible,margins=m['margins'],evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],eligible=eligible,reasons=q['reasons'],actual=v['actual'],step=q['causal']['actual_recovery_step'],margin=m['minimum_fullbody_margin'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_candidates=0,passed=sum(v['purpose']['ok']for v in rows)))
if __name__=='__main__':main()
