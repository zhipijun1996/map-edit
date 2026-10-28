"""C07 horizontal wall-brake adapter, not an independent family/production claim."""
from pathlib import Path
from . import rules_v3 as rules
from .accepted_policy_v1 import purpose
from .alternatives_v1 import alternatives
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v2.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['accepted_policy_v1.py','alternatives_v1.py','main_v2.gd','main_v2.tscn','control-selection-v1.json']]]
def layouts(recipe,interface):
 if recipe not in RECIPES or interface!=0:raise ValueError('needs_design: vertical shaft C07 controls4/4 failed real onward exit, no substitution or fake second interface')
 c=rules.candidate(0,1);c['challenge_route']=True;c['native_scene']='res://prototype/creative_batches/batch30_c07/main_v2.tscn'
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/C07/0',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,core='one falling shot opens front passage and closes real braking wall; subsequent actual recoil contact and pocket support enable efficient onward jump',collision_is_nominal_skill_not_only_solution=True,novelty='effective collision-use adaptation, independent family unconfirmed',allowed_extra_action_policies='Actual extra original groundjump plus actual postshot landing renewal; can return initial rock, land pocket, or use original lower steps. Same-goal costs and actual world state remain reported.',canonical_pair=dict(open_a=True,open_b=False),alternative_pair_states=[dict(open_a=True,open_b=False),dict(open_a=False,open_b=True)]),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='brake')],space=dict(max_width=1450,max_height=1100,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],pocket='internal transfer support, not extra port',lower_steps='costly recovery/alternative, not main route or safe extra port'),resource_state=dict(reset_between_components=False,entry='Original groundedA/fresh resources; forwardA closed/brakingB open',exit='Actual stable selectedB/reward; nominal forwardA open/brakingB closed, separately paid alternatives can retain initial pair state. Generic state transfer UNKNOWN.'),return_conditions='B->A and all external seams UNKNOWN. Small exact firstmiss floor->rightsteps->B fixture passes12/13 and retains initial pair; no generic recovery/return inferred.',budget=dict(generator_candidates=4,director_revisions=0))
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return[c]
