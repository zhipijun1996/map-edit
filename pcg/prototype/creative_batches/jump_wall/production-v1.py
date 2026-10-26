"""Three distinct jump/wall proposals on original Godot and regular gate."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import gated
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.production_loop import run
OWN=Path(__file__);ADAPTER=OWN.with_name('runner-capabilities-v1.gd')
FAMILIES=['late-air-rise','step-off-wall-return','switchback-wall-ascent']
def cases(family):
 out=[]
 for k in range(4):
  if family=='late-air-rise':
   c=base(f'late-air-rise-v1-{k}');c['capabilities']=['move','jump','double_jump'];c['family']=family;c['platforms']=[[-160,438,400,100],[120,140,140,140],[340,318,240,40]];c['one_way_platform_indices']=[2];reward(c,420,300)
   finish(c,420,300,[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',8+k%2*2),wait_x(276+k//2*4),cmd('jump'),cmd('jump_release',12),settle(420,5)])
  elif family=='step-off-wall-return':
   c=copy.deepcopy(json.loads((ROOT/f'results/workshop-creative-jump-wall-candidate-probes-v1/return-{k}.json').read_text())['case']);c['id']=family+'-v1-'+str(k);c['platforms'][2][3]=24;x,y=c['exit_port'];c['goal']=[x-25,y-4,50,8]
  else:
   c=copy.deepcopy(json.loads((ROOT/f'results/workshop-creative-jump-wall-candidate-probes-v1/switch-{k}.json').read_text())['case']);c['id']=family+'-v1-'+str(k)
  c.update(production_recipe=family,parent_family=family,trace_all=True,max_frames=480)
  c['rule_parameters']=dict(relationship=family,control_candidate=k,capability_guard_adapter='runner-capabilities-v1 routes legacy guard only; actual declared capabilities validated/applied by unchanged original Adapter',source_type='llm_subagent_proposal',task_name='/root/jump_wall_creator',human_fun='unreviewed',return_status='UNKNOWN')
  c['generation_rule']=dict(id='creative/jump-wall/'+family,version=1,parameters=c['rule_parameters']);c['idea_ids']=['llm-subagent/jump-wall/'+family];out.append(c)
 return out
def spec(family):
 c=cases(family)[0]
 return dict(schema='map-notes/challenge-specification/v1',id='creative/jump-wall/'+family+'/0',region='plains',required_family=family,objective=dict(relationship=family),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=1800,max_height=1400,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=8,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported actual declared capabilities; pre-input snapshot',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(req):
 f=req['recipe'];s=spec(f);cs=cases(f)
 for c in cs:c['map_specification']=s
 return dict(status='requires_physics',specifications=[s],cases=cs)
def kicks(r):
 return [f for f in r.get('frames',[])if any(e.get('state')=='wall_kick'for e in f.get('accepted',[]))]
def purpose(c,r):
 fs=r.get('frames',[]);reasons=[];causal={};snap=r.get('capability_snapshot',{})
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if sorted(snap.get('declared',[]))!=sorted(c['capabilities']):reasons.append('actual_capability_snapshot_mismatch')
 if snap.get('jump_enabled')!=('jump'in c['capabilities']) or snap.get('shoot_enabled')!=('shot_recoil'in c['capabilities']):reasons.append('ability_binding_mismatch')
 if r.get('workshop',{}).get('coins',0)<8:reasons.append('reward_not_actually_claimed')
 f=c['production_recipe'];ks=kicks(r);airs=[q for q in fs if any(e['type']=='air_jump'for e in q.get('accepted',[]))]
 if f=='late-air-rise':
  causal=dict(air_jump_positions=[[q['x'],q['y']]for q in airs],roof_right=260,body_half_width=12)
  if not airs or not any(q['x']-12>260 and q['y']>280 for q in airs):reasons.append('second_jump_not_preserved_until_full_body_cleared_roof')
  if r.get('wall_jumps',0)or r.get('shots',0):reasons.append('unexpected_propulsion')
 elif f=='step-off-wall-return':
  attach=[q for q in fs if q['traversal_state']=='wall_attach'];causal=dict(wall_kick_positions=[[q['x'],q['y']]for q in ks],attach_frames=len(attach),kick_without_ordinary_jump=not snap.get('jump_enabled'),exit_rise=c['entry_port'][1]-c['exit_port'][1])
  if not ks or not attach or not any(q['y']>c['entry_port'][1]+5 for q in attach)or not any(q['vx']< -80 for q in fs if ks and q['frame']>ks[0]['frame']):reasons.append('step_off_contact_then_reverse_not_observed')
  if r.get('air_jumps',0)or r.get('shots',0):reasons.append('unexpected_propulsion')
 else:
  causal=dict(wall_kick_positions=[[q['x'],q['y']]for q in ks],guarded_right_wall_y=[200,380])
  if not any(q['x']>150 for q in ks)or not any(q['x']<90 for q in ks):reasons.append('both_distinct_wall_launches_not_observed')
  if r.get('air_jumps',0)or r.get('shots',0):reasons.append('unexpected_propulsion')
 return dict(ok=not reasons,reasons=reasons,causal=causal,behavior=dict(air_jumps=r.get('air_jumps',0),wall_jumps=r.get('wall_jumps',0),shots=r.get('shots',0)))
def alternatives(c):
 out=[];x=c['exit_port'][0]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']=c['id']+'-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for axis in [-1,0,1]:
  for wait in [0,45]:add(f'walk-{axis}-{wait}',[cmd('axis',value=axis),cmd('wait',wait),settle(x,1)])
 for hold in [4,8,16,24]:
  add(f'single-jump-{hold}',[cmd('axis',value=1),wait_x(205 if c['production_recipe']=='late-air-rise'else130),cmd('jump'),cmd('jump_release',hold),settle(x,5)])
 for idx,q in enumerate(c['control_plan']):
  if q['op']=='jump':
   p=copy.deepcopy(c['control_plan']);p[idx]['op']='wait';add('omit-jump-'+str(idx),p)
 if c['production_recipe']=='late-air-rise':
  for delay in [0,3,6,9,12,15,18,21,25,30]:add(f'early-or-late-double-{delay}',[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',4),cmd('jump',delay),cmd('jump_release',12),settle(x,5)])
 else:
  for delay in [8,12,16,20,30,45,60,75,90]:
   add('same-wall-return-'+str(delay),[cmd('axis',value=1),gated('jump','wall_attach',min_after=3),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),cmd('axis',delay,value=1),gated('jump','wall_attach',min_after=3,timeout=150),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),settle(x,5)])
 return out
if __name__=='__main__':
 run('workshop-creative-jump-wall-production-v1',[dict(recipe=f,interfaces=[0])for f in FAMILIES],cycles=3,library_root=ROOT/'results/workshop-creative-jump-wall-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=OWN,extra_sources=[ADAPTER],runner_script=ADAPTER)
