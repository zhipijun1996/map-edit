"""One folded airlock; normal and genuine missed-M recovery both must qualify."""
import copy
from pathlib import Path
from . import rules_v2 as rules
from . import module_v1 as module
from .module_counters_v1 import alternatives
from .module_counter_policy_v1 import classify as COUNTER_CLASSIFIER
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['core_v1.py','core_v2.py','module_v1.py','module_counters_v1.py','module_counter_policy_v1.py','alternatives_v1.py','counter_policy_v1.py','control-selection-v1.json']]]
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: only first westhigh/eastlow exactworld; secondspace unimplemented')
 cs=[module.candidate(s)for s in ['normal','recovery']]
 for c in cs:
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
  c['source_map_request']=copy.deepcopy(c['map_specification'])
  c['scope_limits']=dict(independent_new_family_claim=False,reverse='UNKNOWN',recovery='OnlytheactualsameworldmissedM->retainedstair->airrecoil->M->B witness; notallfailurestates',sameworld_return='Knownattemptfailed; nofoldbackclaim',seam='UNKNOWN',boundary_crossing='UNKNOWN',wholeMap='UNKNOWN',human_fun='UNKNOWN',production_admitted=False)
  c['map_request_response']=dict(status='requires_physics',request_origin='explicitmodelderived10coinC02foldedadaptation_notactualMapnode',required_canonical_witnesses=['A-to-B','A-to-B-missed-M-recovery'],ordered_pairs=[['A','B']],unknown_ordered_pairs=[['B','A']],map_added_terrain=0,actualMapRewardBinding='UNKNOWN',pairedCellConsumer='BinstallationUNKNOWN',production_admitted=False)
 return cs
def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='Onlywesthigh/eastlow; eastHigh/westMid remainsunimplemented')],new_physics_cases=0)
 cs=layouts(RECIPES[0],0)
 if not isinstance(spec,dict)or digest(spec)!=digest(cs[0]['map_specification']):return dict(status='needs_design',conflicts=[dict(field='request',reason='Onlyexactderived10coin/twoports/A-to-B normal+missedMrecovery request. No fresh reverse, alteredbudget or arbitraryshape substituted.')],searched=dict(interface=0,rule_versions=2,maximum_probes=80,ordered_pairs=[['A','B']],canonical_routes=['A-to-B','A-to-B-missed-M-recovery']),negotiable=['Freshreward/port/shape version','ActualMapbudgetandjointassignment','Independentreverse/continuityproof'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=cs,assembly='UNKNOWN',production_admitted=False)
purpose=module.purpose
