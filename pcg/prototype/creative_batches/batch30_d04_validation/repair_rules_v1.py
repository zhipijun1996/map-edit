"""Bounded control-only repair. No change to original D04 geometry or physics."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04 import api_v3 as api
from pcg.prototype.workshop.rules import cmd, ground, settle

HERE = Path(__file__).parent
TARGETS = [300, 285]
SOURCE_DEPENDENCIES = [Path(api.__file__), HERE/'repair-protocol-v1.json'] + api.SOURCE_DEPENDENCIES


def materialize(interface, control=0):
    c = copy.deepcopy(api.fixtures(interface, 0)[1])
    p = c['control_plan']
    assert p[52]['op'] == 'axis' and p[52]['value'] == 1
    assert p[53]['trigger']['dynamic']['value'] == 300
    assert p[57]['op'] == 'axis' and p[58]['op'] == 'jump'
    target = TARGETS[control]
    # Settle is continuing feedback, not an arrival wait. Allow30 actual
    # physics frames for convergence before original supported jump/refill.
    p[52:57] = [settle(target, 0), cmd('wait', 30), cmd('axis', value=0), ground(), cmd('wait', 8)]
    c['id'] = f'b30-d04-tail1-i{interface}-c{control}'
    c['rule_parameters']['return_tail_repair'] = dict(target_x=target, feedback_wait_frames=30, candidate_index=control)
    c['generation_rule']['validation_tail_source'] = str(Path(__file__).relative_to(HERE.parents[3]))
    c['generation_rule']['validation_tail_version'] = 1
    c['validation_fixture']['control_repair_only'] = True
    return c
