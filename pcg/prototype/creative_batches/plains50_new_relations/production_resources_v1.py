"""Resource benefit creates a turn problem; recovered shot also opens high door."""
import argparse,copy,math
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.probe_v3 import adverse_refund,refund_gate
from pcg.prototype.creative_batches.plains50_new_relations.production_v1 import specification
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.counterexamples import alternatives as generic_alternatives
from pcg.prototype.workshop.rules import cmd,wait_x,settle,launch
from pcg.prototype.plains.evaluation import observed
HERE=Path(__file__).parent

def compiler(request):
 name=request['recipe'];cs=[];ss=[]
 if name not in ['adverse-refund-reversal','refill-short-gate']:return dict(status='needs_design',gaps=['unsupported exact resource relationship'],cases=[])
 for v in [0,1]:
  source=adverse_refund(v)if name=='adverse-refund-reversal'else refund_gate(v);source['rule_parameters']['interface']=v;s=specification(source,v);s['risk_reward']['amount']=16;ss.append(s)
  for delay in [18,22]:
   c=copy.deepcopy(source);c['id']=f'p50-{name}-i{v}-d{delay}';c['control_plan'][5]['trigger']['after']=delay;c['map_specification']=s;c['production_recipe']=name;c['idea_ids']=['p50-new/'+name];c['generation_rule']=dict(id='plains50-new/'+name,version=1,source_type='current_codex_subagent',parameters=c['rule_parameters']);cs.append(c)
 return dict(status='requires_physics',specifications=ss,cases=cs)

def purpose(c,r):
 fs=r.get('frames',[]);why=[];b=observed(c,r)
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<16:why.append('reward_not_claimed')
 if b['refunds']<1 or not b['continuous_two_air_shots']:why.append('actual_air_hit_refund_chain_missing')
 shots=[(f,e)for f in fs for e in f.get('accepted',[])if e['type']=='shot']
 causal=dict(actual_refunds=b['refunds'],continuous_two_air_shots=b['continuous_two_air_shots'])
 if c['family']=='adverse-refund-reversal':
  reversal=len(shots)>=2 and shots[0][1]['direction'][0]>.1 and shots[1][1]['direction'][0]<-.1
  before=[f['x']for f in fs if shots and shots[0][0]['frame']<=f['frame']<shots[1][0]['frame']]if len(shots)>1 else[]
  causal.update(opposite_recoil_shots=reversal,actual_backward_dx=min(before)-before[0]if before else None)
  if not reversal or not before or min(before)-before[0]>-10:why.append('resource_gain_did_not_create_reversal_problem')
 else:
  hits=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open'];g=c['latches'][0]['gate']
  cross=[f for f in fs if f['x']-12<g[0]+g[2]and f['x']+12>g[0]and f['y']+18>g[1]and f['y']-18<g[1]+g[3]]
  causal.update(actual_gate_hits=len(hits),body_door_cross_frames=len(cross),same_shot_scope='canonical witness only; early opening that preserves refill chain is allowed')
  if not hits or not cross:why.append('real_refill_gate_crossing_missing')
 return dict(ok=not why,reasons=why,behavior=b,causal=causal)

def alternatives(c):
 out=generic_alternatives(c)
 def add(k,p):
  d=copy.deepcopy(c);d['id']+='-counter-'+k;d['counterexample_kind']=k;d['control_plan']=p;out.append(d)
 for hold in [8,16,24]:
  for dy in [.5,.8660254037844386,1.]:add(f'one-shot-direct-{hold}-{dy}',launch(hold,hold+6,dy,205)+[settle(c['exit_port'][0],6)])
 # Kill or consume the nearby enemy before leaving the original bank, then try
 # the high landing with the real remaining resource state.
 for n in [1,3]:
  p=[cmd('axis',value=0)]+[cmd('shoot',after=24 if i else 0,aim_cell=dict(kind='enemy',id='ammo-sentry'))for i in range(n)]+[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(c['exit_port'][0],6)];add('pre-damage-enemy-'+str(n),p)
 if c['family']=='refill-short-gate':
  for delay in [0,30,60]:
   p=[cmd('shoot',aim_cell=dict(kind='bell',id='refill-gate-bell')),cmd('wait',after=delay)]+copy.deepcopy(c['control_plan']);add('ground-preopen-'+str(delay),p)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-plains50-new-resource-production-v1');a=p.parse_args()
 run(a.name,requests=[dict(recipe='adverse-refund-reversal'),dict(recipe='refill-short-gate')],cycles=2,compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'probe_v3.py',HERE/'production_v1.py'])
