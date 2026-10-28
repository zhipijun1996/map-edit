"""Exact terminalparameter candidate; originalfullregular decides admission."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE.parent/'batch30_blockn02_repair/alternatives_v1.py',HERE/'control-selection-v1.json']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
PRELIMINARY_QUALITY=dict(high_mild='5/6',high_moderate='2/5',low_mild='6/6',low_moderate='5/5',notice='P2catch timingfragile; notqualified. Originalfixed fullregular+held mayreject. No moreprobes withinlineage80.')

def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='onlyoneexplicitactiveforkspaceimplemented')],new_physics_cases=0,production_admitted=False)
 cases=[rules.candidate(0,CONTROL[s],s)for s in ['high','low']];expected=cases[0]['map_specification']
 if not isinstance(spec,dict)or digest(spec)!=digest(expected):return dict(status='needs_design',conflicts=[dict(field='request',reason='onlyexactderivedN02forkregistered; noactualBgraph/unknownstate/rewardservice/port substitution')],searched=dict(interfaces=[0],size=128,ordered_pairs=[['A','B'],['A','C']],reserved_dimensions=[1280,1024]),negotiable=['newphysicalspaceandfreshbudget','independentjointmappingorstateproof','receiver/catchdesignrepairifregularfails'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),request_origin='TaskAderivedcurrentMapcontract_notactualBgraph',registered_ordered_pairs=[['A','B'],['A','C']],unresolved=['Bgraphjointassignment','fourreverse/crosspairs','arbitraryingress','boundarycrossing','failure_recovery','externalstatepropagation','fullMap'],map_added_terrain=0,production_admitted=False,preliminary_quality=PRELIMINARY_QUALITY)
 for c in cases:c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=copy.deepcopy(response);c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_joint_mapping',cases=cases,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0 or set(CONTROL)!={'high','low'}:raise ValueError('needs_design: exactcurrentone-interfaceforkonly')
 request=rules.candidate(0,CONTROL['high'],'high')['map_specification'];return candidate_for_request(request,0)['cases']

purpose=rules.purpose
