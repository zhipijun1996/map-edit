"""Three-port cross fork; rejected symmetric four-port request stays rejected."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters,counter_policy_v1 as policy,critical_v1 as critical
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),Path(critical.__file__),Path(policy.__file__),*policy.SOURCE_DEPENDENCIES,HERE/'counter-policy-v1.json',HERE/'control-selection-v1.json']
COUNTER_CLASSIFIER=policy.classify
CONTROLS=json.loads((HERE/'control-selection-v1.json').read_text())['controls']['0']
def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['play_hint']='同一中台：向后平射横渡，保留东侧开口；或空中向下击铃，同枪打开顶门、关闭侧门，上穿后落固定高台。经东岸多跳一次也能绕回高廊。'
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['counter_scope_policy']=dict(id='N17/paid-internal-A-staged-detour/v1',nominal_upward_and_body_purpose_strict=True,allowed='ActualwithinownedM/B/fixedupper/relay/Cwithfullresources, nofeweractualguns/strictlymorejumps/noearlieroriginalstableC. Onecounterwitnessnotrobustgenericcertificate.',cheap_D_exemptions=False)
 c['map_request_response']=dict(status='requires_physics',request_origin='explicit_native_threeport_noreward_cross_fork',registered_ordered_pairs=[['A','B'],['A','C']],unknown_ordered_pairs=[['B','A'],['B','C'],['C','A'],['C','B']],map_added_terrain=0,new_gameplay_family=False,new_Cell=False,first_upper='ActualfixedPlatform3, notclosedsidegatecatch',fourport_request='needs_design:cheapDwallcrest/bypassM+pair beatsnominal; two-rulesexhausted. No4portqualificationfrom8clean.',unresolved=['ActualMapincidentassignment/allrequiredpairs','Pairedv3Cellconsumerinstallation','Genericmiss/floorretry/return/arbitraryentry','Boundarycrossing/seams/fullMap','Humanfun/playtest/production'])
 return c
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design:N17only3portinterface0;4portsharedMrequestrefuted')
 return[metadata(rules.candidate(t,CONTROLS['A-'+t]))for t in ['B','C']]
purpose=rules.purpose
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]
def candidate_for_request(spec,interface=0):
 wanted=layouts(RECIPES[0],0)[0]['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_threeport_cross_fork',reason='OnlyA->B/CoriginalpairedinitialAclosed/Bopen,noreward,frozenworld. 4portDsharedMrequirementrefutedby1gun1jumpD->B199fand1gun4jumpD->C369f, cheaperthanrequestedMroute; nointentrenameorquietsubstitution.')],searched=dict(interfaces=[0,1],eligible_interfaces=[0],rule_revisions=2,maximum_rule_revisions=2,maximum_probe_cases=80,block_size=128,required_pairs=[['A','B'],['A','C']],fourport_nominal_clean_passes=8,fourport_cheap_refutations=2),negotiable=['Exactthreeportworld/demand','FutureexplicitasymmetricDchallengeproposalwithnewintentandfreshversion/full','Freshreward/resource/space/returnadaptation'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),new_physics_cases=0,production_admitted=False,assembly='UNKNOWN')
