"""Fresh output after removing the dead session's stale X11 display lock."""
import inspect
from . import record_review040_v1 as previous
def run(row):
 source=inspect.getsource(previous.run).replace("+'-v1'","+'-v3'")
 scope={**previous.__dict__};exec(compile(source,__file__,'exec'),scope);scope['run'](row)
if __name__=='__main__':
 import sys
 for r in previous.rows():
  if r['reviewId']in sys.argv[1:]:run(r)
