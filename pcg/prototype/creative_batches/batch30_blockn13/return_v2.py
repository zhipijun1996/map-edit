"""Exact same actor/world A-B-A cost comparison; not a fresh B-A Module route."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from .cheap_v2 import candidate as cheap
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.dynamic.generators import dynamic
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def candidate(park=True,delay=0):
 c=rules.candidate(0,0)if park else cheap('no-stop-immediate');c.pop('counterexample_kind',None)
 p=c['control_plan'];assert p[-1]['op']=='settle'
 back=[wait_x(1638),cmd('axis',value=0),ground(),cmd('wait',12+delay),cmd('axis',value=-1),wait_x(1424,-1),cmd('jump'),cmd('jump_release',20),dynamic('wait','on_platform',query=dict(id='parking-deck'),timeout=450),cmd('axis',value=0),ground(),cmd('wait',8)]
 if park:back +=[cmd('shoot',aim_cell=dict(kind='bell',id='deck-control')),cmd('wait',16)]
 back +=[wait_x(440,-1),cmd('axis',value=-1),wait_x(26,-1),cmd('axis',value=0),ground(),cmd('wait',12)]
 c['control_plan']=p[:-1]+back;c['goal']=[17,586,14,8];c['max_frames']=2200;c['id']+='-sameworld-return-'+('park'if park else'no-stop')+'-d'+str(delay)
 c['validation_fixture']=dict(kind='exactA_B_A_sameworld',actual_goal_port='A',definition_marker_port='B',no_module_enrollment=True,no_fresh_B_A_claim=True,park=park,deliberate_B_wait=delay)
 return c
def purpose(c,r):
 q=common.checked_purpose(type('Core',(),{'purpose':staticmethod(rules.core_purpose)}),c,r);fs=r.get('frames',[]);visits=[f for f in fs if f.get('grounded')and abs(f['x']-1640)<7 and abs(f['y']-462)<1];claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')]
 if len(visits)<6:q['reasons'].append('actual_stable_B_visit_missing')
 if len(claims)!=1:q['reasons'].append('actual_once_only_reward_transaction_missing')
 late=[f for f in fs if visits and f['frame']>visits[-1]['frame']and f.get('support_id')=='parking-deck'];transport=max((f['x']for f in late),default=0)-min((f['x']for f in late),default=0)
 if transport<400:q['reasons'].append('actual_real_carrier_return_transport_missing')
 q['causal'].update(actual_B_visit_frames=[f['frame']for f in visits],actual_once_claims=claims,return_carrier_transport_dx=transport,scene_reconstruction=False,actual_cost={k:r.get(k)for k in ['shots','jumps','ticks']},deliberate_wait=c['validation_fixture']['deliberate_B_wait'])
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'return-protocol-v2.json',HERE/'cheap_v2.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([candidate(True,0)]+[candidate(False,d)for d in [0,120,160,200]],'same-world-return-comparison'):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],return_dx=q['causal']['return_carrier_transport_dx'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_candidates=0,scope='exactsameworldreturn/costcomparisononly; nofreshB-A/seam/heldclaim'))
if __name__=='__main__':main()
