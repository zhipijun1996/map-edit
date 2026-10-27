"""Explicit outer control repair; original physical world is unchanged."""
import math
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn13 import rules_v2 as parent
from pcg.prototype.creative_batches.batch30_blockn13 import alternatives_v2 as original_counters
from pcg.prototype.creative_batches.batch30_blockn13.counter_policy_v1 import classify
HERE=Path(__file__).parent
RECIPES=parent.RECIPES
RUNNER_SCRIPT=parent.RUNNER_SCRIPT
NATIVE_SCENE=parent.NATIVE_SCENE
EXPORT_SCRIPT=parent.EXPORT_SCRIPT
COUNTER_CLASSIFIER=classify
SOURCE_DEPENDENCIES=[Path(parent.__file__),*parent.SOURCE_DEPENDENCIES,Path(original_counters.__file__),HERE/'protocol-v1.json',HERE.parent/'batch30_blockn13/counter_policy_v1.py',HERE.parent/'batch30_blockn13/cheap_v2.py',HERE.parent/'batch30_blockn13/original-cycle-receipt-v1.json',HERE.parent/'batch30_blockn13/noise-failure-audit-v1.json',HERE.parent/'batch30_blockn13/aim-relative-audit-v1.json']
def candidate(interface=0,control=0):
 if interface!=0 or control not in [0,1]:raise ValueError('needs_design: only East front controls; no mirrored physics')
 c=parent.candidate(0,2+control)
 shots=[q for q in c['control_plan']if q['op']=='shoot']
 shots[-1]['direction']=[-math.sqrt(.5),math.sqrt(.5)]
 c['id']=f'b30-blockn13-repair-v1-i0-c{control}'
 c['rule_parameters'].update(outer_repair=1,parent_control=2+control,repair_control=control,exit_shot_direction=shots[-1]['direction'])
 c['generation_rule'].update(id='batch30/N13-repair',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['map_specification']['id']='batch30/N13-repair/0'
 c['map_specification']['objective'].update(control_repair='front near stop and shallower down-left leave shot; original geometry and gate purpose retained')
 c['layout_title']='靠前停台，斜射离台保留停靠门'
 return c
purpose=parent.purpose
core_purpose=parent.core_purpose
def alternatives(c):
 return original_counters.alternatives(c)
