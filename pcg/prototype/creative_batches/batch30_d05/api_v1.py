"""Two receiver demands for the real mounted-bell interception prototype."""
import copy,math
from pathlib import Path
from . import rules_v1 as original
from .search_v1 import alternatives as old_alternatives
from pcg.prototype.workshop.rules import cmd,settle,wait_x,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=original.RECIPES
RUNNER_SCRIPT=original.RUNNER_SCRIPT
NATIVE_SCENE=original.NATIVE_SCENE
SOURCE_DEPENDENCIES=original.SOURCE_DEPENDENCIES+[Path(original.__file__),HERE/'search_v1.py',HERE/'protocol-v2.json']
CONTROL={0:0,1:0}

def materialize(interface=0,control=0):
 c=original.candidate(interface,control)
 if interface:
  c['platforms'][1]=[1180,300,340,150]
  c['exit_port']=[1280,282];c['goal']=[1255,278,50,8]
  c['reward_sites']=[];original.reward(c,1280,282,12)
  c['control_plan'][-1]=settle(1280)
 c['id']=f'b30-d05-api1-i{interface}-c{control}'
 c['capabilities']=original.CAPS[:]
 c['ports']=[dict(id='A',position=[80,420],support_index=0,normal=[-1,0]),dict(id='B',position=c['exit_port'],support_index=1,normal=[1,0])]
 c['route_spec']=dict(id='air-start-interception',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True)
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['layout_title']='风铃台追接 / '+('远岸'if interface==0 else'抬高接收岸')
 c['generation_rule']=dict(id='human-d05/bell-carrier-catch',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/D05/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='same air shot recoils actor and starts its mounted-bell carrier; carrier intercepts actor before grounded renewal and second bank jump'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id='air-start-interception')],space=dict(max_width=2400,max_height=1600,max_port_span_x=1400),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original supported actor and initially parked carrier',exit='observed stable B only; arbitrary carrier phase UNKNOWN'),return_conditions='Missed catch has lower recovery terrain; exact retry fixtures separate. Reverse B to A UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside registered D05 demands')
 return [materialize(interface,CONTROL[interface])]

def purpose(c,r):
 return original.purpose(c,r)

def alternatives(c):
 out=old_alternatives(c)
 target=c['exit_port'][0]
 # All inherited policies target the actual B, not an obsolete receiver.
 for v in out:
  for q in v['control_plan']:
   if q.get('op')=='settle':q['target_x']=target
  v['goal']=copy.deepcopy(c['goal'])
 # Ground-start then deliberately stay on the deck and jump after the roof:
 # this is a stronger falsifier than the earlier fixed walking scripts.
 board=copy.deepcopy(c['control_plan'][:5])
 for x in [760,820,880,930]:
  for dy in [.15,.6,.8660254]:
   v=copy.deepcopy(c);v['id']+=f'-counter-ride-launch-{x}-{dy}';v['counterexample_kind']='ground-start-ride-launch'
   v['control_plan']=board+[cmd('shoot',aim_cell=dict(kind='bell',id='catch-bell')),cmd('axis',value=0),wait_x(x),cmd('jump'),cmd('jump_release',20),cmd('axis',value=1),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(target)];out.append(v)
 return out
