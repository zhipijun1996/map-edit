"""Final S09 calibration repair; keep both earlier samples and formal history."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core
from . import repaired_samples_revision063_v2 as previous,finalize_revision063_v1 as final
from .continue_revision063_v1 import rows,label
final.ROOT=core.REPO/'pcg/manual_review/implementation/revision-063-repaired-samples-v2'
previous.VERSIONS={**previous.VERSIONS,'s09':'repair-v10'}
def deliver_repaired(row):
 source=inspect.getsource(final.deliver).replace("'-delivery-final-v1'","'-repaired-delivery-repair-v10'")
 ns={**final.__dict__};exec(compile(source,__file__,'exec'),ns);ns['deliver'](row)
source=inspect.getsource(previous.run).replace('final.deliver(row)','deliver_repaired(row)');ns={**previous.__dict__,'deliver_repaired':deliver_repaired};exec(compile(source,__file__,'exec'),ns)
if __name__=='__main__':ns['run'](next(r for r in rows()if label(r)=='s09'))
