"""Frozen wide C05 fork; the tall requirement is not claimed supported here."""
from pathlib import Path
from . import rules_v3 as rules
from .alternatives_v1 import alternatives
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['alternatives_v1.py','control-selection-wide-v1.json','runner_v1.gd','main_v1.gd','main_v1.tscn']]]
purpose=rules.purpose
def specification(interface,cases):
 c=cases[0]
 return dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C05/{interface}',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],junction_role='fork',core='original upward diagonal carrier supports meaningful upper-west return branch versus higher-east continuation; actual departure and original pair-state tradeoff',port_roles=c['rule_parameters']['port_roles'],route_world_outcomes={v['route_spec']['id']:dict(required_pair_states=v['required_pair_states'])for v in cases},airborne_selector_is_canonical_not_mandatory=True),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port=v['route_spec']['to_port'],role='main',route_id=v['route_spec']['id'])for v in cases],space=dict(max_width=1900,max_height=1150,max_port_span_x=1400),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],near='real upper-west onward route above original ingress arch',far='real high-east onward route beyond central pillar',recovery_floor='internal only, not an extra port'),resource_state=dict(reset_between_components=False,entry='Original supportedA, same initially parked carrier and near-open/far-closed in all route programmes',exit='Observed stable selected port/reward, actual carrier remains running; generic platform phase/resource transfer UNKNOWN'),return_conditions='All reverse ordered pairs/seams UNKNOWN. Same-world missed-departure/failure fixtures separately; no reset or inferred port interchangeability.',budget=dict(generator_candidates=4,director_revisions=0))
def layouts(recipe,interface):
 if recipe not in RECIPES or interface!=0:raise ValueError('needs_design: only wide C05 fork has both validated prototype branches; tall near controller failed original capture window, no substitution or partial fork claim')
 out=[rules.candidate(0,1,'near'),rules.candidate(0,0,'far')];spec=specification(0,out)
 for c in out:c['map_specification']=spec;c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return out
