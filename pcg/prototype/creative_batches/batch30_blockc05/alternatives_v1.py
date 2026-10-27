"""Exact new world, original18 active counter policies after real dock walk."""
import copy
from pcg.prototype.creative_batches.batch30_c05.alternatives_v1 import alternatives as parent

def alternatives(c):
 core=copy.deepcopy(c);prefix=copy.deepcopy(c['control_plan'][:5]);core['control_plan']=core['control_plan'][5:]
 out=parent(core)
 for v in out:v['control_plan']=copy.deepcopy(prefix)+v['control_plan']
 return out
