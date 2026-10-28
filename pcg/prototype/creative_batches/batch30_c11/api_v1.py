"""Frozen wide PR-D02 repair; real steeper demand not assumed supported."""
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['alternatives_v1.py','control-selection-wide-v1.json','main_v1.gd','main_v1.tscn']]]
purpose=rules.purpose
def specification(c):
 return dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C11/{c["interface"]}',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=c['interface'],core=c['rule_parameters']['core'],independent_new_family_claim=False,repair_lineage='PR-D02 oldshore-prepark actualfalsification and oldmoderate6/12; new version requires actualcarrierdescent/bodyclearance not inverse-axisword',rear_boarding_is_allowed=True,controls='Originalstart/pause only, noautomaticdocking or actorattachment'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='descent')],space=dict(max_width=2100,max_height=1500,max_port_span_x=1400),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],thorns='original visible nearroof face protects clearance, no hidden damage budget',lowerfloor='internal only, no extra safeport'),resource_state=dict(reset_between_components=False,entry='Original groundedA/fresh resources; real carrier parked atdeclared start',exit='Observed stableB/reward under originalresources, carrier keeps realphase/running state. Generic external state transfer UNKNOWN.'),return_conditions='B->A, arbitrary dynamic entry phase, sameworld failed-departure recovery and external seams UNKNOWN until exactfixture. No port swap inferred.',budget=dict(generator_candidates=4,director_revisions=0))
def layouts(recipe,interface):
 if recipe not in RECIPES or interface!=0:raise ValueError('needs_design: only wide descendingcarrier currently screened against knownshore-prepark; steep demand not inferred')
 c=rules.candidate(0,0);c['challenge_route']=True;c['native_scene']='res://prototype/creative_batches/batch30_c11/main_v1.tscn';c['map_specification']=specification(c);c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]));return[c]
