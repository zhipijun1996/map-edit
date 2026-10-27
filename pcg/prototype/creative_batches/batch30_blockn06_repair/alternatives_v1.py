"""Same actual searches with repaired ordinary jump submission."""
import copy
from pcg.prototype.creative_batches.batch30_blockn06.alternatives_v2 import alternatives as old
from pcg.prototype.workshop.rules import cmd

def alternatives(c):
 out=old(c)
 for v in out:
  if v['counterexample_kind'].startswith('ordinary-M-jump-'):
   p=v['control_plan'];j=next(i for i,q in enumerate(p)if q['op']=='jump_release'and i>8)
   p.insert(j,cmd('jump'))
 return out
