"""Use the explicitly selected FULL protocol for all new fixture executions.

The earlier S04 diagnostic used the legacy default metadata and is retained,
but its rejected lineage is not admitted to any FULL qualification.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import core,physics
from . import repair_revision063_fixtures_v1 as previous
from .continue_revision063_v1 import rows,label,OUT
source=inspect.getsource(previous.run).replace("pool_protocols.runtime_protocol(f)","pool_protocols.runtime_protocol(f) if core.read(f/'migration.json').get('holdoutPool') else physics.FULL_PROTOCOL")
ns={**previous.__dict__};exec(compile(source,__file__,'exec'),ns)
if __name__=='__main__':
 for row in rows():
  if label(row)in sys.argv[1:]:ns['run'](row)
