"""Frozen C01 Block adapters for two explicit derived content demands.

The demands consume current Map geometry rules, but are not a response to the
upstream no-reward exp1_0 request: this recipe retains its real 12-coin chest.
"""
import copy
import json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_c01.alternatives_v2 import alternatives
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,
                    HERE/'control-selection-v2.json',
                    HERE.parent/'batch30_c01/alternatives_v2.py']
CONTROL={int(k):v for k,v in json.loads((HERE/'control-selection-v2.json').read_text())['controls'].items()}


def candidate_for_request(spec,interface=0):
    if interface not in CONTROL:
        return dict(status='needs_design',conflicts=[dict(field='interface',reason='outside_registered_two_interface_domain')],new_physics_cases=0)
    c=rules.candidate(interface,CONTROL[interface]);expected=c['map_specification']
    if not isinstance(spec,dict)or digest(spec)!=digest(expected):
        return dict(status='needs_design',conflicts=[dict(field='request',reason='only_exact_derived_Block128_C01_demands_registered; no arbitrary adaptation or reward substitution')],
            searched=dict(interfaces=[0,1],ordered_pairs=[['A','B']],capabilities=['move','jump','shot_recoil'],reward='actual12coinchest'),
            negotiable=['explicit new demand and geometry search','no-reward revision with fresh counters and physics','independent direction/state verification'],new_physics_cases=0,production_admitted=False)
    c['source_map_request']=copy.deepcopy(spec)
    c['map_request_response']=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),
        request_origin='task_a_derived_current_Map_contract_demand; not_B_exp1_0',
        registered_ordered_pairs=[['A','B']],reward='real12coinchest; not_major_item_budget',
        satisfied_static_fields=['Block128','connected_polyomino','W/E_boundary_cell_centres','ground64_internal_staging','preserved_recovery_terrain'],
        unresolved=['B_joint_port_assignment','arbitrary_entry_state','boundary_crossing','B_to_A','major_item_or_reward_budget_service','full_Map'],
        map_added_terrain=0,production_admitted=False)
    c['native_block_scene']=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3]))
    c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    return dict(status='candidate_for_joint_mapping',case=c,response=c['map_request_response'])


def layouts(recipe,interface):
    if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside_registered_BlockBridge_domain')
    request=rules.candidate(interface,CONTROL[interface])['map_specification']
    return [candidate_for_request(request,interface)['case']]


def purpose(c,r):return rules.purpose(c,r)
