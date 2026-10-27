"""Four real directed relations in one unchanged initial paired-bridge world."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules,alternatives_v1 as counters
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),HERE/'control-selection-v1.json']
CONTROLS=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
PAIRS=[['A','B'],['A','C'],['D','B'],['D','C']]
UNKNOWN=[['A','D'],['D','A'],['B','A'],['B','D'],['B','C'],['C','A'],['C','D'],['C','B']]

def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['map_request_response']=dict(status='requires_physics',request_origin='explicit_new_interface_demand_notactualMapplan',registered_ordered_pairs=PAIRS,unknown_ordered_pairs=UNKNOWN,request_source='pcg/prototype/creative_batches/batch30_blockn06_fourport/demand-v1.json',map_added_terrain=0,new_gameplay_family=False,inherited_parent_physics=False,unresolved=['ActualMapcompleteincidentrequirements/jointspace','Boundarycrossingandseams','HighB/Centry/arbitraryworldstate','Retainedfloorretry','Bpairedv3Cellinstallation','FullMap/humanapproval'])
 return c


def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: onlynew4portsharedworld interface0')
 return[metadata(rules.candidate(e,t,CONTROLS[e+'-'+t]))for e in ['A','D']for t in ['B','C']]


def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]


def candidate_for_request(spec,interface=0):
 wanted=layouts(RECIPES[0],0)[0]['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_fourport_demand',reason='OnlysupportedA/Dlowentry-to-B/Chighdestination matrix, exactphysicalCellinitialstate/geometry/capabilities/no-reward demand. Notall12relations, highentry, arbitraryphase orotherrewardversion.')],searched=dict(interfaces=[0],ports=4,required_pairs=PAIRS,unknown_pairs=UNKNOWN,block_size=128,maximum_rule_revisions=2,maximum_probe_cases=80),negotiable=['Exactregistered4directedrelationsandgeometry','Freshindependentphysical/state/size/rewardadaptation'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),response=copy.deepcopy(layouts(RECIPES[0],0)[0]['map_request_response']),new_physics_cases=0,production_admitted=False)
