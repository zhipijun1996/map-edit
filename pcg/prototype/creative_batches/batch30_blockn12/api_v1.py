"""Frozen single-world three-port recoil investment fork; no old trace proof."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules,alternatives_v1 as counters
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),HERE/'control-selection-v1.json']
CONTROLS=json.loads((HERE/'control-selection-v1.json').read_text())['controls']

def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['play_hint']='同一空中枪：先陡向反冲登近高岸取箱，或稍晚向后平射飞向远低岸。底岸是内部保留地貌，不是第四出口。'
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['map_request_response']=dict(status='requires_physics',request_origin='explicit_Block_native_three_side_port_demand_notbounded_oldshoreadaptation',registered_ordered_pairs=[['A','B'],['A','C']],unknown_ordered_pairs=[['B','A'],['B','C'],['C','A'],['C','B']],map_added_terrain=0,new_gameplay_family=False,inherited_parent_physics=False,reward_allocation=dict(amount=12,status='explicit_upper_reward_requirement_notzero_reward_Maprequest'),unresolved=['ActualMapincidentassignment/allrequiredpairs','Boundarycrossing/seams/fullMap','Arbitraryingress/resources','Oldrewardrejoinorbottomfloorretry','Fourportsecondentry','Humanplaytest/production'])
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design:onlynewBlock-native3portinterface0')
 return[metadata(rules.candidate(t,CONTROLS[t]))for t in ['B','C']]

purpose=rules.purpose
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]

def candidate_for_request(spec,interface=0):
 wanted=layouts(RECIPES[0],0)[0]['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_threeport_demand',reason='OnlysameworldA-to-highB/lowC with originalrecoil/fullresources andexplicit12coinuppercache. No fourthport, reverse, rejoin, zero-reward or changedspace certification.')],searched=dict(interfaces=[0,1],eligible_interfaces=[0],second_interface='SameheightC:oneactualcornercatchfailspreregistered24pxsupportmargin, othertwomiss; noqualifiedcontrol',ports=3,required_pairs=[['A','B'],['A','C']],unknown_pairs=[['B','A'],['B','C'],['C','A'],['C','B']],rule_revisions=2,maximum_rule_revisions=2,maximum_probe_cases=80,block_size=128),negotiable=['Exactregisteredthreeport/nativegeometry/rewardrequest','Freshindependentresource/port/rewardadaptation'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),new_physics_cases=0,production_admitted=False,assembly='UNKNOWN')
