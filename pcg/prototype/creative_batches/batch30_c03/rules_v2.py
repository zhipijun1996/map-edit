"""C03 core repair with real closed-window staged escape when enemy is gone."""
import copy,math
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def staged_plan(control=0):
 return [cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',[12,16,20,24][control]),cmd('shoot',6,direction=[-.7,math.sqrt(.51)]),wait_x(635),*rest(),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[.2,math.sqrt(.96)]),cmd('wait',8),cmd('axis',value=-1),settle(450,6)]
def candidate(interface=0,control=0,route='air'):
 c=old.candidate(interface,0,route);c['id']=f'b30-c03-v2-i{interface}-{route}-c{control}'
 c['platforms'][1]=[330,100,260,60]
 c['control_plan'][1]['trigger']['after']=10;c['control_plan'][7]['trigger']['after']=[12,14,16,18][control]
 if route=='staged':c['control_plan']=staged_plan(control)
 c['rule_parameters'].update(control=control,route=route,bell_delay_after_hit_shot=[12,14,16,18][control],receiver_left=330)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','enemies','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C03',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['challenge_route']=True
 return c
def purpose(c,r):
 fs=r.get('frames',[]);stage=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform2'];jumps=[f for f in fs if any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))]
 staged=c['route_spec']['id']=='staged' or (bool(c.get('counterexample_kind'))and len(stage)>=6 and len(jumps)>=2)
 if not staged:q=old.purpose(c,r)
 else:
  why=[]
  if not r.get('ok'):why.append(r.get('reason','not_stable'))
  if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
  if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
  if r.get('returns'):why.append('unexpected_reset')
  if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
  if len(stage)<6 or len(jumps)<2:why.append('actual_staged_ground_renewal_missing')
  q=dict(ok=not why,reasons=why,causal=dict(kind='declared_staged_alternative',staged_support_frames=len(stage),staged_ground_jumps=[f['frame']for f in jumps]),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
 pairs=r.get('workshop',{}).get('paired_gates',[]);state=next((p for p in pairs if p['id']=='window-path-pair'),{})
 if state.get('open_a')is not False or state.get('open_b')is not True:q['reasons'].append('exit_not_window_closed_passage_open')
 gx,gy,gw,gh=c['latches'][0]['paired_gate'];cross=next((f['frame']for f in fs if f['x']-12>=gx+gw),None)
 if cross is None:q['reasons'].append('body_did_not_clear_actual_passage')
 q['causal'].update(actual_window_path_exit_state=state,body_passage_clear_frame=cross,staged_support_frames=len(stage))
 q['ok']=not q['reasons'];return q
def dead_fixture(control=0):
 c=candidate(0,control,'staged')
 clear=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',10),cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',18,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',18,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',18),cmd('axis',value=-1),wait_x(80,-1),*rest(),cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',15)]
 c['id']+='-actual-death-fixture';c['control_plan']=clear+staged_plan(control);c['max_frames']=1800;c['validation_fixture']=dict(kind='actual_enemy_death_staged_fallback',no_module_enrollment=True);return c
