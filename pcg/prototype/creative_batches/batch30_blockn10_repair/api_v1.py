"""Both same-world normal and genuine closed-Near recovery witnesses required."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from .counter_policy_v1 import classify as COUNTER_CLASSIFIER
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'counter_policy_v1.py',HERE/'control-selection-v1.json']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['control']
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design:onlyN10singleinterfacebothA-Bcanonicalroutes')
 cs=[rules.candidate(CONTROL,s)for s in ['normal','retry']]
 for c in cs:
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
  c['source_map_request']=copy.deepcopy(c['map_specification'])
  c['map_request_response']=dict(status='requires_physics',request_origin='explicit_model_authored_lowerexit_currencydemand_notactualMapnode',required_canonical_witnesses=['A-to-B','A-to-B-delayed-Near-retry'],ordered_pairs=[['A','B']],unknown_ordered_pairs=[['B','A']],map_added_terrain=0,production_admitted=False)
 return cs
def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='Onlyregisteredtwoportlowerexitworld')],new_physics_cases=0,production_admitted=False)
 cs=layouts(RECIPES[0],0)
 if not isinstance(spec,dict)or digest(spec)!=digest(cs[0]['map_specification']):return dict(status='needs_design',conflicts=[dict(field='request',reason='Onlyexactderived12currencylowerexitdemandwithbothcanonicalA-Bwitnesses. ArbitraryMaproles/rewardallocation/return/ports/statessubstitutionnotallowed')],searched=dict(interface=0,ports=2,canonical_routes=['A-to-B','A-to-B-delayed-Near-retry'],ordered_pairs=[['A','B']],currency=12,block_size=128),negotiable=['Exactderiveddemand','Freshversion+actualMapbudgetbinding','Newphysicalproof forreverse/space/state'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=cs,production_admitted=False,assembly='UNKNOWN')
purpose=rules.purpose
