"""Preserve all original18 exact counterpolicies after actual dock approach."""
import copy
from pcg.prototype.creative_batches.batch30_c07.alternatives_v1 import alternatives as original
def alternatives(c):
 core=copy.deepcopy(c);prefix=copy.deepcopy(c['control_plan'][:5]);core['control_plan']=core['control_plan'][5:];out=original(core)
 for v in out:v['control_plan']=copy.deepcopy(prefix)+v['control_plan']
 return out
