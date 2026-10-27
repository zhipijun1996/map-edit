"""One real fork world; other incoming directions and Map requests are unknown."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules
from .alternatives_v2 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v2.py',HERE/'control-selection-v2.json']
CONTROL=json.loads((HERE/'control-selection-v2.json').read_text())['controls']

def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='Only3portA->B/A->Cworldregistered;D/fourportneedsfreshphysicalproof')],searched=dict(interfaces=[0],ordered_pairs=[['A','B'],['A','C']]),new_physics_cases=0,production_admitted=False)
 cases=[rules.candidate(t,CONTROL[t])for t in ['B','C']]
 if not isinstance(spec,dict)or digest(spec)!=digest(cases[0]['map_specification']):return dict(status='needs_design',conflicts=[dict(field='request',reason='Onlyexplicitderivedforkdemandregistered; actualMapallincidentpairs/currency/ingressstate notsilentlysubstituted')],searched=dict(interfaces=[0],port_count=3,ordered_pairs=[['A','B'],['A','C']],rewards=[],block_size=128),negotiable=['Matchthisexactdirectedforkrequirement','Newphysicalproof forotherorderedpairs/ports','Separaterewardversion/budgetbinding'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_explicit_fork_demand',request_id=spec['id'],source_request_sha256=digest(spec),request_origin='model_authored_notactualMaprequest',registered_ordered_pairs=[['A','B'],['A','C']],unknown_ordered_pairs=[['B','A'],['B','C'],['C','A'],['C','B']],map_added_terrain=0,production_admitted=False,unresolved=['ActualMapjointspatialassignment/completeincidentpairrequirements','Boundarycrossing','Arbitraryingressresources/worldstate','Failurefloorretry','Regionalreturn/fullMap'])
 for c in cases:
  c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=copy.deepcopy(response);c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_explicit_fork_demand',cases=cases,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: onlyN06threeportinterface0')
 return candidate_for_request(rules.candidate('B',CONTROL['B'])['map_specification'],interface)['cases']

purpose=rules.purpose
