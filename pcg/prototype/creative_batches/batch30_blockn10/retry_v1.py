"""Late second shot is really recaptured by Near; same-world M re-landing retries."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def candidate():
 k=json.loads((HERE/'control-selection-v1.json').read_text())['control'];c=rules.candidate(k);p=c['control_plan'];j=max(i for i,q in enumerate(p)if q['op']=='jump')
 late=[cmd('wait',120),cmd('jump'),cmd('shoot',4,aim_cell=dict(kind='bell',id='far')),cmd('jump_release'),cmd('axis',value=-1),ground(),cmd('axis',value=0),cmd('wait',8),cmd('axis',value=-1),wait_x(992,-1),*rules.rest()]
 c['control_plan']=p[:j]+late+p[j:];c['id']+='-sameworld-late-retry';c['max_frames']=2300
 c['validation_fixture']=dict(kind='same_world_late_near_recapture_then_M_retry',no_module_enrollment=True,no_reset=True,no_reconstruction=True,deliberate_delay_ticks=120)
 return c
def purpose(c,r):
 q=common.checked_purpose(rules,c,r);fs=r.get('frames',[]);hits=q['causal']['actual_hits'];near=[e['frame']for e in hits if e['id']=='near'];far=[e['frame']for e in hits if e['id']=='far'];last=near[-1]if near else None;fhit=far[0]if far else None
 closed=[f['frame']for f in fs if near and last is not None and near[0]+20<f['frame']<last and any(v['id']=='near'and not v['open']and v['bell_layer']==8 and v['gate_layer']==1 and not v['gate_disabled']for v in f.get('n10',[]))]
 recatch=[f for f in fs if last is not None and fhit is not None and last<f['frame']<fhit and rules.over(f,c['platforms'][1])and f.get('shot_charges')==1]
 if len(near)!=2 or len(far)!=1:q['reasons'].append('actual_near_far_receiver_late_rehit_order_missing')
 if not closed:q['reasons'].append('actual_near_layer8_close_before_late_shot_missing')
 if not recatch:q['reasons'].append('actual_same_M_recapture_renewal_after_late_shot_missing')
 if r.get('shots')!=3 or r.get('jumps')!=3:q['reasons'].append('actual_fixed_retry_actions_missing')
 q['causal'].update(actual_closed_before_late_shot=closed,actual_M_recapture_frames=[f['frame']for f in recatch],actual_latest_near_to_far_ticks=fhit-last if fhit is not None and last is not None else None,actual_retry_actions={k:r.get(k)for k in ['shots','jumps','ticks']},scene_reconstruction=False)
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'retry-protocol-v1.json',HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 def run(cases,stage):
  for c,r,ev in e.run(cases,stage):
   q=purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],latest_window=q['causal']['actual_latest_near_to_far_ticks'])),flush=True)
 run([candidate()],'clean-retry')
 if rows[-1]['purpose']['ok']:run([instantiate(candidate(),271129918,l,0)for l in ['mild','moderate']],'noise-retry')
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),scope='exactcontinuousdelayedretryfixture; nogenericretry/seamproof',new_candidates=0))
if __name__=='__main__':main()
