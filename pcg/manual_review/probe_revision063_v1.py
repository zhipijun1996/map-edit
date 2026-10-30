import inspect,sys
from . import probe_ideas_v1 as previous
from .continue_revision063_v1 import rows,label
from .execution_revision063_v1 import frozen_row
def main():
 s=inspect.getsource(previous.run).replace('approved-ideas-','approved-r063-');ns={**previous.__dict__,'label':label};exec(compile(s,__file__,'exec'),ns)
 for r in rows():
  if not sys.argv[2:] or label(r) in sys.argv[2:]:ns['run'](frozen_row(r,sys.argv[1]),sys.argv[1])
if __name__=='__main__':main()
