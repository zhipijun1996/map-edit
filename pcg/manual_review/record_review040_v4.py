"""167's actual lower-left Port identifier, with a new output directory."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from . import record_review040_v1 as previous
def run(row):
 source=inspect.getsource(previous.run).replace("+'-v1'","+'-v4'").replace("'entry-to-exit_upper_right'","'entry_left-to-exit_upper_right'")
 scope={**previous.__dict__};exec(compile(source,__file__,'exec'),scope);scope['run'](row)
if __name__=='__main__':
 for r in previous.rows():
  if r['reviewId']=='167':run(r)
