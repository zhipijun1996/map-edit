"""C03 final first-space repair and independently constructed under-grotto demand."""
import copy,math
from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
purpose=prior.purpose
def candidate(interface=0,control=0,route='air'):
 if interface not in [0,1]:raise ValueError('outside two registered C03 spaces')
 c=prior.candidate(0,3 if route=='air'else control,route);c['id']=f'b30-c03-v3-i{interface}-{route}-c{control}'
 c['interface']=interface;c['rule_parameters'].update(interface=interface,control=control)
 if interface==0:
  c['platforms'][1]=[330,110,260,60];c['latches'][0]['bell']=[190,400];c['latches'][0]['paired_gate']=[300,-180,24,460]
  target=[450,92]
  if route=='air':c['control_plan'][7]['trigger']['after']=[18,20,22,24][control]
 else:
  c['platforms']=[[-100,238,340,45],[330,-100,260,60],[520,80,240,32],[300,438,230,45],[-100,760,1150,60],[-100,600,160,32],[200,450,180,32],[0,330,240,32]]
  c['latches']=[dict(id='window-path-pair',bell=[250,200],gate=[280,340,220,24],paired_gate=[380,-400,24,638],initial_open='B')]
  c['enemies'][0]['position']=[400,422];c['spawn']=[80,220];c['entry_port']=[80,220];c['ports'][0]['position']=[80,220]
  target=[450,-118]
  if route=='air':
   launch,delay=[(205,18),(225,20),(205,22),(225,24)][control]
   c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',10),cmd('axis',value=1),wait_x(launch),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',delay,aim_cell=dict(kind='bell',id='window-path-pair')),settle(450,6)]
  else:c['control_plan']=prior.staged_plan(control)
 c['ports'][1]['position']=target;c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8]
 c['reward_sites'][0].update(position=target,region=[target[0]-30,target[1]-5,60,10])
 c['rule_parameters'].update(geometry='side-grotto'if interface==0 else'under-grotto',bell=c['latches'][0]['bell'],receiver=c['platforms'][1],body_passage=c['latches'][0]['paired_gate'],shoot_window=c['latches'][0]['gate'])
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','enemies','latches','reward_sites']})
 c['layout_title']='借火以后把射窗封回去 / '+('侧龛高岸'if interface==0 else'下龛越唇')
 c['generation_rule']=dict(id='batch30/C03',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['max_frames']=1400
 return c

def dead_fixture(interface=0,stage_control=1):
 c=candidate(interface,stage_control,'staged');opening=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',10)]
 takeoff=([cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10)]if interface==0 else[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',16)])
 kill=[cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',35,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',35,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',40),cmd('axis',value=-1),wait_x(80,-1),*prior.rest(),cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',15)]
 c['id']+='-actual-death-fixture';c['control_plan']=opening+takeoff+kill+c['control_plan'];c['max_frames']=2200;c['validation_fixture']=dict(kind='actual_enemy_death_staged_fallback',no_module_enrollment=True)
 return c

def specification(interface,c):
 return dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C03/{interface}',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='carry a real airborne enemy-hit refill across complementary enemy-window/body-passage state exchange; closed-window staged alternative survives enemy loss'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='air'),dict(from_port='A',to_port='B',role='main',route_id='staged')],space=dict(max_width=1700 if interface==0 else 1350,max_height=1000 if interface==0 else 1250),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Original supportedA/full source resources, same enemy3HP and initial closed-window/open-passage in all routes',exit='Observed stable B with actual window closed/passage open; enemy HP differs by route and remains persistent'),return_conditions='Actual dead-enemy staged fallback and window/return fixtures separately; generic B->A and seams UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
