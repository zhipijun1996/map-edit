"""Original timed-latch three-port pass-receiver fork, exact demand only."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),HERE/'control-selection-v1.json']
CONTROLS=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['play_hint']='先真实落中央台回枪；选左或右，跳到相应风铃外侧再回身射击。反冲把你推向同一枪打开的出口。两铃各开自己的短时门。'
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['map_request_response']=dict(status='requires_physics',request_origin='explicit_new_threeport_static_vantage_demand',registered_ordered_pairs=[['A','B'],['A','C']],unknown_ordered_pairs=[['B','A'],['B','C'],['C','A'],['C','B']],map_added_terrain=0,new_gameplay_family=False,family_comparison='G09sightlinebacktrackforkcomposition;newfamilyclaimwithheld',new_Cell=False,inherited_parent_physics=False,unresolved=['ActualMapincidentassignment/allrequiredpairs','Boundarycrossing/seams/fullMap','Secondlowingress/arbitraryresources','Missedshotgenericreturn/floorrecovery','Humanfun/playtest/production'])
 return c
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design:onlyregisteredN14threeportinterface0')
 return[metadata(rules.candidate(t,CONTROLS[t]))for t in ['B','C']]
purpose=rules.purpose
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]
def candidate_for_request(spec,interface=0):
 wanted=layouts(RECIPES[0],0)[0]['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_threeport_static_vantage_demand',reason='OnlyAoriginalingress->B/Cindependentclosedtimeddoors, norewards andfrozengeometry. Fourport/allpairs/reward/arbitraryphase/space notquietlysubstituted.')],searched=dict(interfaces=[0],ports=3,rule_revisions=2,maximum_rule_revisions=2,maximum_probe_cases=80,block_size=128,registered_pairs=[['A','B'],['A','C']],unknown_pairs=[['B','A'],['B','C'],['C','A'],['C','B']]),negotiable=['Exactthreeport/staticgeometry/demand','Freshindependentsecondentry/reward/spaceversion'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),new_physics_cases=0,production_admitted=False,assembly='UNKNOWN')
