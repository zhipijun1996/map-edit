"""Unqualified demonstration freezes and corrected native delivery; no second formal."""
import inspect,sys
from pcg.migration import core,physics
from . import finalize_revision058_v1 as base
from .continue_revision058_v1 import rows,label,AUTH
folder_for=base.folder_for

def demo(row,version):
 source=inspect.getsource(base.freeze).replace("assert core.read(screen)['passed']and core.read(native)['passed']", "assert core.read(native)['passed']")
 ns={**base.__dict__};exec(compile(source,__file__,'exec'),ns);ns['freeze'](row,version)
 f=folder_for(row);selection=core.read(f/'selection.json');screen=core.read(core.resolve_artifact(selection['screen']['path']));selection.update(allGatesPassed=screen['passed'],selectedForFormal=False,rule='Explicit native demonstration only after bounded control stop or post-formal runtime correction. Never inherits former admission.');core.write(f/'selection.json',selection)
 core.write(f/'qualification-not-run.json',dict(passed=False,status='UNQUALIFIED_PLAYABLE_CANDIDATE',reason='S11 third-receiver runtime corrected after original formal; no second formal this round'if label(row)=='s11'else'Bounded controls stopped without all-route phase/noise screen pass',newIndependentHoldout=False,originalFormal='pcg/results/approved-r058-s11-qualified-final-v1/migration-physics.json'if label(row)=='s11'else None,designImpossible=False))
def deliver(row):
 source=inspect.getsource(base.deliver)
 # base builds the existing delivery function in a namespace, so edit only its
 # run-name replacement expression, retaining original native/compiler gates.
 source=source.replace(".replace('approved-r053-','approved-r058-')", ".replace('approved-r053-','approved-r058-').replace(\"'-delivery-final-v1'\",\"'-delivery-final-v2'\")"if label(row)=='s11'else".replace('approved-r053-','approved-r058-')")
 ns={**base.__dict__};exec(compile(source,__file__,'exec'),ns);ns['deliver'](row)
if __name__=='__main__':
 for r in rows():
  wanted=sys.argv[3:]if sys.argv[1]=='demo'else sys.argv[2:]
  if label(r)in wanted:(demo(r,sys.argv[2])if sys.argv[1]=='demo'else deliver(r))
