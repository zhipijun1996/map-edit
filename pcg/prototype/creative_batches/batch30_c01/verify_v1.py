import argparse,copy,json,math
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from . import api_v1 as api
HERE=Path(__file__).parent
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def recovery(interface,control):
 c=api.layouts(api.RECIPES[0],interface)[0];source=copy.deepcopy(c['control_plan']);dx=[.2,.4,.2,.4][control];launch=[300,300,330,330][control]
 fail=source[:5]+[cmd('wait',8),*rest()]
 stairs=[cmd('axis',value=-1),wait_x(180,-1),*rest(),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[dx,math.sqrt(1-dx*dx)]),wait_x(0,-1),*rest(),cmd('axis',value=1),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.4,math.sqrt(.84)]),wait_x(180),*rest(),cmd('axis',value=1),wait_x(launch),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',0,direction=[.3,math.sqrt(.91)]),wait_x(80,-1),*rest(),cmd('shoot',aim_cell=dict(kind='bell',id='bridge-pair')),cmd('wait',35)]
 c['id']+=f'-recovery-r{control}';c['control_plan']=fail+stairs+source;c['max_frames']=2200
 c['validation_fixture']=dict(kind='same_world_failed_landing_recovery',no_module_enrollment=True,control=control)
 return c
def recovery_purpose(c,r):
 fs=r.get('frames',[]);shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];land=next((f for f in fs if shots and f['frame']>shots[0]['frame']and f.get('grounded')),None)
 state=r.get('workshop',{}).get('paired_gates',[]);events=[e for p in state for e in p.get('events',[])if e.get('type')=='pair_switch']
 why=[]
 if not r.get('ok'):why.append(r.get('reason'))
 if r.get('hp')!=5 or r.get('returns')or any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('safety_or_capability')
 if not land or land.get('support_id')!='Platform3':why.append('deliberate_first_failure_did_not_land_recovery_floor')
 if len(events)<3:why.append('world_not_rearmed_and_retried_by_real_shots')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 return dict(ok=not why,reasons=why,causal=dict(first_landing={k:land.get(k)for k in ['frame','x','y','support_id']}if land else None,switches=events),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['counters','recovery'],required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v1.json',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[]
 if a.stage=='counters':
  cs=[api.layouts(api.RECIPES[0],i)[0]for i in [0,1]]
  for c,r,e in engine.run(cs,'named-clean'):
   q=api.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],landing=q['causal']['first_landing'])),flush=True)
  kinds={'omit-shot-4','omit-shot-13','shore-flip-active-6-6-0.15','shore-flip-active-6-30-0.8660254','shore-flip-active-16-18-0.6','shore-flip-active-28-6-0.8660254','shore-flip-active-28-30-0.15','shore-flip-active-28-30-0.8660254'}
  for c,r,e in engine.run([v for c in cs for v in api.alternatives(c)if v['counterexample_kind']in kinds],'active-counter'):
   q=api.purpose(c,r);same=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and r.get('workshop',{}).get('coins',0)>=12
   rows.append(dict(case=c,result=r,purpose=q,evidence=e,same_external_outcome=same,invalidates_design=same and not q['ok']));print(json.dumps(dict(id=c['id'],same=same,purpose=q['ok'],reason=r.get('reason'))),flush=True)
 else:
  clean=[]
  for c,r,e in engine.run([recovery(i,k)for i in [0,1]for k in range(4)],'recovery-clean'):
   q=recovery_purpose(c,r);row=dict(case=c,result=r,purpose=q,evidence=e);rows.append(row);clean.append(row);print(json.dumps(dict(id=c['id'],purpose=q,reason=r.get('reason'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
  selected=[]
  for i in [0,1]:
   good=[x for x in clean if x['case']['interface']==i and x['purpose']['ok']]
   if good:selected.append(good[0]['case'])
  write(engine.out/'recovery-selection.json',dict(ids=[c['id']for c in selected],before_mild=True))
  for c,r,e in engine.run([instantiate(c,261031001,'mild',k)for c in selected for k in range(6)],'recovery-mild'):
   q=recovery_purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'])),flush=True)
 write(engine.out/'verification-results.json',rows)
if __name__=='__main__':main()
