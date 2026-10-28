"""Frozen machinery proposal implementation v3; original Engine/components only."""
import copy,json,math
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v2 import candidates as probe_candidates
from pcg.prototype.creative_batches.machinery.probe_v1 import board
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.rules import cmd,settle,wait_x,launch
from pcg.prototype.workshop.counterexamples import alternatives as common_counters
from pcg.prototype.workshop.production_recipes import specification as unused
from pcg.prototype.workshop.engine import ROOT
RECIPES=['elevator-headroom','carrier-rendezvous','saw-pursuit']
def candidates(recipe):
 out=[]
 for c in probe_candidates():
  if c['family']!=recipe:continue
  c=copy.deepcopy(c);c['production_recipe']=recipe;c['parent_family']='moving_platform'if recipe!='saw-pursuit'else'dynamic_saw'
  c['rule_parameters']=dict(relationship=recipe,source_task='/root/machinery_creator',search='two or three declared phase windows; no held selection',human_fun='unreviewed')
  c['generation_rule']=dict(id='creative-machinery/'+recipe,version=3,source_type='llm_subagent_proposal',source_task='/root/machinery_creator',parameters=c['rule_parameters'])
  c['trace_all']=False;out.append(c)
 return out

def specification(recipe):
 c=candidates(recipe)[0]
 return dict(schema='map-notes/challenge-specification/v1',id='creative-machinery/v3/'+recipe,region='plains',required_family=recipe,objective=dict(relationship=recipe,world_state='real dynamic phase and support',human_fun='unreviewed'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=1900,max_height=1400,max_port_span_x=1400),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=8,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(request):
 recipe=request['recipe'];s=specification(recipe);cs=candidates(recipe)
 for c in cs:c['map_specification']=s;c['idea_ids']=['machinery/'+recipe]
 return dict(status='requires_physics',specifications=[s],cases=cs)
def purpose(c,r):
 fs=r.get('frames',[]);why=[];causal={}
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<8:why.append('reward_not_claimed')
 family=c['production_recipe']
 if family=='elevator-headroom':
  carried=[f for f in fs if f.get('support_id')=='carrier'and abs(f.get('axis',0))<.01]
  gain=max((f['y']for f in carried),default=0)-min((f['y']for f in carried),default=0)
  causal=dict(neutral_supported_frames=len(carried),real_carried_height=gain)
  if gain<300:why.append('vertical_world_transport_not_used')
 elif family=='carrier-rendezvous':
  a=[f for f in fs if f.get('support_id')=='carrier'];b=[f for f in fs if f.get('support_id')=='other'];
  causal=dict(first_support_frames=len(a),second_support_frames=len(b),support_sequence=bool(a and b and a[0]['frame']<b[0]['frame']))
  if len(a)<12 or len(b)<6 or not causal['support_sequence']:why.append('two_independent_moving_supports_not_used')
 else:
  inside=[f for f in fs if 300<f['x']<675 and 395<f['y']<440]
  ahead=[f for f in inside if f.get('saws')and f['saws'][0]['position'][0]>f['x']+30]
  dropped=[f for f in fs if 700<f['x']<900 and f['y']>460]
  causal=dict(corridor_samples=len(inside),hazard_ahead_samples=len(ahead),drop_escape_samples=len(dropped))
  if len(inside)<25 or len(ahead)<len(inside)*.9 or not dropped:why.append('follow_released_space_then_drop_not_used')
 return dict(ok=not why,reasons=why,causal=causal)
def alternatives(c):
 out=common_counters(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for hold in [8,16,24]:
  for dy in [.15,.5,.8660254,1.]:
   add('direct-recoil-'+str(hold)+'-'+str(dy),launch(hold,hold+6,dy,205)+[settle(c['exit_port'][0],6)])
 add('direct-walk',[cmd('axis',value=1),settle(c['exit_port'][0],after=6)])
 if c['production_recipe']=='elevator-headroom':
  for hold in [8,16,24]:add('vertical-shore-recoil-'+str(hold),[cmd('axis',value=1),wait_x(220),cmd('jump'),cmd('jump_release',after=hold),cmd('shoot',after=6,direction=[0,1]),settle(c['exit_port'][0],6)])
 if c['production_recipe']=='carrier-rendezvous':
  # Carry on first, then try to skip second support entirely with maximal jump/recoil.
  for dy in [.15,.5,.8660254]:
   plan=copy.deepcopy(c['control_plan'][:10])+[cmd('axis',value=1),wait_x(695),cmd('jump'),cmd('jump_release',after=20),cmd('shoot',after=6,direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)]
   add('skip-second-support-'+str(dy),plan)
 if c['production_recipe']=='saw-pursuit':
  for delay in [0,30,60,90,120,150,180,210]:add('blind-entry-'+str(delay),[cmd('wait',after=delay),cmd('axis',value=1),settle(c['exit_port'][0],after=6)])
 return out
if __name__=='__main__':
 run('workshop-creative-machinery-production-v3',requests=[dict(recipe=r)for r in RECIPES],cycles=3,library_root=ROOT/'results/workshop-creative-machinery-library-v3',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[Path(__file__).with_name('probe_v1.py'),Path(__file__).with_name('probe_v2.py')])
