import sys
from .continue_revision060_v1 import rows,label
from .execution_revision060_v1 import frozen_row
from .native_preflight_revision060_v1 import run
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[2:]:run(frozen_row(r,sys.argv[1]),sys.argv[1])
