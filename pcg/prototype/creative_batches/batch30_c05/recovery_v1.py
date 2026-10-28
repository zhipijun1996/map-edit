import argparse,copy,json
from pathlib import Path
from . import api_v1 as api
from .probe_v2 import compact
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def pillar():return dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='Platform4'),timeout=360))
def failed_selector(wait=20):
 c=api.layouts(api.RECIPES[0],0)[1];source=copy.deepcopy(c['control_plan']);shot=next(i for i,q in enumerate(source)if q.get('aim_cell',{}).get('id')=='station-selector')
 plan=source[:shot]+[cmd('shoot',direction=[-.95,(1-.95*.95)**.5]),settle(1008),pillar(),settle(920),wait_x(924,-1),ground(),cmd('wait',wait),cmd('shoot',aim_cell=dict(kind='bell',id='station-selector')),cmd('wait',20),settle(1020),wait_x(1016),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),cmd('wait',20),settle(1160,6)]
 c['id']+=f'-failed-selector-recovery-w{wait}';c['control_plan']=plan;c['max_frames']=2400;c['validation_fixture']=dict(kind='same_world_failed_selector_to_original_pillar_to_far_exit',wait_after_pillar=wait,no_module_enrollment=True)
 return c
def missed_near_departure():
 c=api.layouts(api.RECIPES[0],0)[1];source=copy.deepcopy(c['control_plan']);c['id']+='-missed-near-departure-continues-far';c['control_plan']=source[:11]+[wait_x(690),cmd('axis',value=0),cmd('wait',30)]+source[11:];c['validation_fixture']=dict(kind='same_world_missed_near_departure_continues_far',not_claiming_failed_airjump=True,no_module_enrollment=True);return c
def purpose(c,r):
 q=api.purpose(c,r);fs=r.get('frames',[])
 if c['validation_fixture']['kind'].startswith('same_world_failed'):
  shots=[f for f in fs if any(a.get('type')=='shot'for a in f.get('accepted',[]))]
  supported=[f for f in fs if len(shots)>=2 and f['frame']>shots[1]['frame']and f.get('grounded')and f.get('support_id')=='Platform4']
  if not supported:q['reasons'].append('missed_selector_pillar_recovery_missing')
  pair=q['causal'].get('pair',{});events=[e for e in pair.get('events',[])if e.get('type')=='pair_switch']
  if supported and events and events[0]['frame']<=supported[0]['frame']:q['reasons'].append('selector_did_not_really_fail_before_pillar')
  q['causal'].update(pillar_frames=len(supported),first_actual_pillar_frame=supported[0]['frame']if supported else None,recovery_keeps_same_running_carrier=True)
 else:
  started=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='carrier_toggle']
  if len(started)!=1:q['reasons'].append('carrier_was_restarted_or_rephased')
  q['causal']['single_start_then_passed_near_departure']=len(started)==1
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--kind',choices=['failed-selector','missed-departure'],required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v1.json',HERE/'probe_v2.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];clean=[]
 cs=[failed_selector(w)for w in [20,40,60]]if a.kind=='failed-selector'else[missed_near_departure()]
 for c,r,e in engine.run(cs,'continuous-clean'):
  q=purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),last={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 selected=clean[:1];write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in selected],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031201,l,k)for c in selected for l in ['mild','moderate']for k in range(6)],'continuous-perturb'):
  q=purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'recovery-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
