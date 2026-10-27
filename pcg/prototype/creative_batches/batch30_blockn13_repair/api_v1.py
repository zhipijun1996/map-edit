"""One East interface, honest parking/no-stop alternatives and scoped return sidecar."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
EXPORT_SCRIPT=HERE/'export_v1.mjs';COUNTER_CLASSIFIER=rules.COUNTER_CLASSIFIER
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['control']
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json',HERE/'probe-receipt-v1.json',HERE/'return_v1.py',HERE/'export_v1.mjs']
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: one East N13 repair interface only; mirrored physics untested')
 receipt=json.loads((HERE/'probe-receipt-v1.json').read_text())
 if receipt['status']!='screened_requires_original_full':raise ValueError('needs_design: required repair screen incomplete')
 c=rules.candidate(0,CONTROL)
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['scope_limits']=dict(independent_new_family_claim=False,choice='NoStop faster cheaper outbound is legitimate. Nominal parking keeps actual deck/Dock for a possible return; no claim it is the only return solution.',return_evidence=receipt['continuous_return'],fresh_B_A='UNKNOWN',arbitrary_ingress_phase='UNKNOWN',seam='UNKNOWN',wholeMap='UNKNOWN',human_fun='UNKNOWN',production_admitted=False)
 c['map_request_response']=dict(status='requires_physics',source='explicitderived12coinA2Dockcomposition',registered_ordered_pairs=[['A','B']],unknown_ordered_pairs=[['B','A']],actualMapRewardBinding='UNKNOWN',map_added_terrain=0,assembly='UNKNOWN')
 return[c]
def candidate_for_request(spec,interface=0):
 cs=layouts(RECIPES[0],0)
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(cs[0]['map_specification']):return dict(status='needs_design',conflicts=[dict(field='request',reason='Only exact derived East two-port/12coin/sharedpausedcarrier/Dock demand supported; no mirror, fresh reverse, no-reward rewrite or actual Map budget claim.')],searched=dict(interfaces=[0],ordered_pairs=[['A','B']],parent_failed_cases=51,maximum_new_probes=29),negotiable=['New request/state/reward binding with fresh physics','Independently verified reverse/phase/seam'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=cs,assembly='UNKNOWN',production_admitted=False)
purpose=rules.purpose
alternatives=rules.alternatives
