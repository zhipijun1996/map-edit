"""Fixture setup correction: a Cell spawn is not a new Module entry anchor.

Preserve v1 rejected definitions. Keep original legal entry/exit anchors, and
only initialize the isolated Cell actor on the carrier's actual phase pose.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
import sys
from . import probe_ideas_recovery_v1 as previous
from .new_ideas_v1 import rows, label

def run(row):
    source = inspect.getsource(previous.run).replace('extra-recovery-v1', 'extra-recovery-v2').replace("            c['entry_port'] = list(c['spawn'])\n", '')
    namespace = dict(previous.__dict__)
    exec(compile(source, __file__, 'exec'), namespace)
    namespace['run'](row)

if __name__ == '__main__':
    for row in rows():
        if label(row) in sys.argv[1:]:
            run(row)
