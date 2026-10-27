"""Versioned failure interface; no unsupported substitution or store writes."""
from . import rules_v2 as rules

def for_request(spec):
 return dict(schema='pcg/module-generation-response/v1',status='needs_design',conflicts=[dict(field='A_to_B',reason='Neutral boarding holds actor at carrier centre-95.9px. At endpoint actor1184<absolute departure trigger1240; real walk toward leading deck is missing.'),dict(field='A_to_C',reason='Airborne projectile reverses actual platform, but departure from left lip plus13-frame hit flight leaves actor at846 while platform1076 at landing; actual floor replaces carrier catch.'),dict(field='new_Cell_consumer',reason='Original B has start/pause only. manual_reverse_on_hit/v1 requires isolated Cell installation, signed clock/direction persistence and new mechanism contract; no output is certified for B.')],searched=dict(source_proposal='B31-N03',rule_revisions=2,actual_engine_cases=32,original_preflight_rejections=8,executed_Cell_cases=8,Cell_checks_passed=8,module_clean_cases=16,module_clean_purpose_passed=0,full_calibration='NOT_RUN',holdout='NOT_RUN',shape=[1536,1024],ports=['A','B','C'],pairs=[['A','B'],['A','C']]),negotiable=['Fresh registered successor proposal with real on-deck repositioning before departure','Explicit new Cell support in B; do not replace by original pause','Separate boundary crossing, recovery, return and persistence verification'],actual_new_physics_cases=0,new_modules=0,new_families=0,production_admitted=False)

if __name__=='__main__':
 import json
 print(json.dumps(for_request({}),ensure_ascii=False,indent=2))
