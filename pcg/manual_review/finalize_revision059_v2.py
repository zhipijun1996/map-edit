"""Preserve native clean candidates explicitly as unqualified; no formal allocation."""
import inspect,sys
from pcg.migration import core
from . import finalize_revision059_v1 as base
from .continue_revision059_v1 import rows,label
folder_for=base.folder_for

def demo(row,version):
 s=inspect.getsource(base.freeze).replace("assert core.read(screen)['passed']and core.read(native)['passed']", "assert core.read(native)['passed']");ns={**base.__dict__};exec(compile(s,__file__,'exec'),ns);ns['freeze'](row,version);f=folder_for(row);selection=core.read(f/'selection.json');selection.update(allGatesPassed=False,selectedForFormal=False,rule='Explicit clean native demonstration; phase/noise screen did not pass. No new formal or holdout.');core.write(f/'selection.json',selection);core.write(f/'qualification-not-run.json',dict(passed=False,status='UNQUALIFIED_PLAYABLE_CANDIDATE',reason='Frozen program has complete clean native replay; phase/noise screen still fails. HQ02 original projectile interception also remains unproven.',designImpossible=False,newIndependentHoldout=False))
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[3:]:demo(r,sys.argv[2])
