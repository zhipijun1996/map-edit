"""Existing directional-recoil family adaptation; wall contact is optional."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),HERE/'control-selection-v1.json',HERE.parents[1]/'godot/scripts/player/player_motor.gd',HERE.parents[1]/'godot/scripts/world/shot_latch.gd']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['selected_near']
def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['layout_title']='斜射开高门 / 原墙可投影'
 c['play_hint']='向左下击铃，用同枪反冲登高岸。近墙可把多余横冲交给真实碰撞，离墙一段距离也能同成本到达。门永久打开，失败落回原岸可真落地后再试。'
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['map_request_response']=dict(status='requires_physics',request_origin='explicit_native_Wlow_Ehigh_8coin_demand',registered_ordered_pairs=[['A','B']],unknown_ordered_pairs=[['B','A']],new_gameplay_family=False,novelty='Originalmust-wallhypothesisrefutedbyequalcost/fasterdetachedroute; foldasexistingdirectionalrecoiladaptation',map_added_terrain=0,new_Cell=False,wall_projection='Realoptionalmechanismobservation_notnecessarysolutionpredicate',recovery='Onecleanactualsameworldmiss/land/refill/retryonly;generic/reversequalificationUNKNOWN',unresolved=['ActualMapincidentallpairs/rewardallocation','Reversefreshcloseddoor/arbitraryentry/resources','Genericfailure/retry/return','Boundarycrossing/seams/fullMap','Humanfun/playtest/production'])
 return c
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design:onlyN16registeredinterface0')
 return[metadata(rules.candidate(**CONTROL))]
purpose=rules.purpose
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]
def candidate_for_request(spec,interface=0):
 wanted=layouts(RECIPES[0],0)[0]['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_Wlow_Ehigh_request',reason='OnlyA->Bregisteredstaticgeometry/originalpermanentdoor and8coinrequest. Noquietreverse/zero-reward/fourport/arbitraryresources/space substitution; wallnecessityhasbeenrefuted.')],searched=dict(interfaces=[0],rules=2,maximum_rules=2,maximum_probe_cases=80,block_size=128,required_pairs=[['A','B']],unknown_pairs=[['B','A']]),negotiable=['ExactWlow_Ehigh8coinversion','Freshindependentmirror/reward/state/reversevalidation'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),new_physics_cases=0,production_admitted=False,assembly='UNKNOWN')
