"""Resume immutable repaired samples using distinct delivery experiment IDs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import core
from . import repaired_samples_revision063_v2 as previous,finalize_revision063_v1 as final
from .continue_revision063_v1 import rows,label,OUT
final.ROOT=core.REPO/'pcg/manual_review/implementation/revision-063-repaired-samples-v1'
def deliver_repaired(row):
 source=inspect.getsource(final.deliver).replace("'-delivery-final-v1'","'-repaired-delivery-'+previous.VERSIONS[n]")
 ns={**final.__dict__,'previous':previous};exec(compile(source,__file__,'exec'),ns);ns['deliver'](row)
source=inspect.getsource(previous.run).replace('final.deliver(row)','deliver_repaired(row)');ns={**previous.__dict__,'deliver_repaired':deliver_repaired};exec(compile(source,__file__,'exec'),ns)
if __name__=='__main__':
 for row in rows():
  n=label(row)
  if n not in sys.argv[1:]:continue
  f=final.folder_for(row)
  if f.exists():
   q=core.read(f/'qualification.json');assert q.get('knownCalibrationFailuresRepaired');deliver_repaired(row)
   p=OUT/'delivery-selection.json';mapping=core.read(p);mapping['overrides'][n]=core.relative(f);core.write(p,mapping)
  else:ns['run'](row)
