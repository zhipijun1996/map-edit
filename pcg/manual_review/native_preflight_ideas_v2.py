if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import ideas_runtime_v2 as backend
from . import native_preflight_ideas_v1 as previous
from .new_ideas_v1 import rows,label

def run(row,version):
 scope={**previous.__dict__,'backend':backend};exec(compile(inspect.getsource(previous.run),__file__,'exec'),scope);scope['run'](row,version)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[2:]or label(r)in sys.argv[2:]:run(r,sys.argv[1])
