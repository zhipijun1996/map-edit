"""One supported C03 world, two actual routes; lower demand explicitly rejected."""
from pathlib import Path
from . import rules_v4 as rules
from .alternatives_v2 import alternatives
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['control-selection-v1.json','alternatives_v2.py','runner_v1.gd','main_v1.gd','main_v1.tscn']]]
purpose=rules.purpose
PAIR_STATES=[dict(id='window-path-pair',open_a=False,open_b=True)]
def layouts(recipe,interface):
 if recipe not in RECIPES or interface!=0:raise ValueError('needs_design: C03 lower-grotto requirement failed real player-harm/moderate gate; only side-grotto interface0 supported, see control-selection-v1.json')
 out=[rules.candidate(0,'air'),rules.candidate(0,'staged')]
 spec=rules.prior.specification(0,out[0]);spec['objective'].update(supported_interfaces=[0],route_world_outcomes={c['route_spec']['id']:dict(required_pair_states=PAIR_STATES)for c in out},unsupported_demand=dict(id='B30-C03/under',status='needs_design',reason='real player_harm and poor moderate samples; not substituted'))
 for c in out:
  c['map_specification']=spec;c['required_pair_states']=PAIR_STATES
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return out
def required_world_outcome(c,r):
 pairs={x['id']:x for x in r.get('workshop',{}).get('paired_gates',[])}
 return dict(ok=all(all(pairs.get(s['id'],{}).get(k)==v for k,v in s.items()if k!='id')for s in c.get('required_pair_states',[])),required_pair_states=c.get('required_pair_states',[]),actual_pair_states=list(pairs.values()))
def dead_fixture():return rules.dead_fixture(0)
