"""Frozen C10 under-pocket only; actual continuous recovery is a required witness."""
import copy
from pathlib import Path
from . import rules_v3 as rules
from . import suite_v1 as probes
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(probes.__file__)]

def specification(cs):
 c=cs[0]
 return dict(schema='map-notes/challenge-specification/v1',id='batch30/C10/under',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],content_role='conditional_recovery_switch',core='Retained real airborne shot reverses an actual missed bank into opened internal roof cavity; real air access restores paired world and continuous retry. Recovery cavity is not external port.',strategy_variants=['nominal','miss_restore_retry'],normal_route_may_remain_valid=True,core_conditional_recovery_is_actual_witness_not_forced_player_sequence=True),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id=v['route_spec']['id'])for v in cs],space=dict(max_width=1600,max_height=1200,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],recovery_cavity='internal no bonus; does not increase map port count'),resource_state=dict(reset_between_components=False,entry='Original supportedA, Aopen/Bclosed; original single-air-shot resources. Both canonical witnesses share complete physical world.',exit='Observed stableB after nominal or exact continued miss/restoration; other world/resource entering states UNKNOWN'),return_conditions='Required fixture is A miss -> cavity -> restoredA -> retryB. This is not B->A, arbitrary failure recovery or seam proof; those remainUNKNOWN.',budget=dict(generator_candidates=4,director_revisions=0))

def layouts(recipe,interface):
 if recipe not in RECIPES or interface!=0:raise ValueError('needs_design: C10 upper interface correction fired below actual cavity floor in all4 samples; 3-rule cycle exhausted. Only under-pocket interface supported, no automatic substitution.')
 cs=[rules.materialize(0,'main',0),rules.materialize(0,'retry',0)]
 cs[0]['route_spec']['id']='nominal';cs[1]['route_spec']['id']='miss-restore-retry'
 spec=specification(cs)
 for c in cs:
  c['map_specification']=spec;c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return cs

def purpose(c,r):
 if c.get('counterexample_kind'):
  v=copy.deepcopy(c);v['rule_parameters']['route']='main';q=rules.purpose(v,r);q['causal']['counter_goal_policy']='Nominal/shorter valid route to same reward is allowed: recovery is conditional utility, never a compulsory detour.';return q
 return rules.purpose(c,r)

def alternatives(c):
 if c['rule_parameters']['route']=='main':return probes.alternatives(c)
 normal=rules.materialize(0,'main',0);out=[]
 for alt in probes.alternatives(normal):
  v=copy.deepcopy(c);v['id']+='-counter-'+alt['counterexample_kind'];v['counterexample_kind']=alt['counterexample_kind'];v['control_plan']=alt['control_plan'];out.append(v)
 ix=[i for i,q in enumerate(c['control_plan'])if q['op']=='shoot']
 for index,label in zip(ix,['omit-correction','omit-restoration','omit-retry-recoil']):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan'][index]=dict(op='wait',trigger=dict(after=v['control_plan'][index]['trigger']['after']));out.append(v)
 return out
