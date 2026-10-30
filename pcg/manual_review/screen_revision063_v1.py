import inspect,sys
from . import screen_review040_v1 as previous
from .continue_revision063_v1 import rows,label
from .execution_revision063_v1 import frozen_row
def main():
 s=inspect.getsource(previous.run).replace("'approved-r040-'+row['reviewId']","'approved-r063-'+label(row)");ns={**previous.__dict__,'label':label};exec(compile(s,__file__,'exec'),ns)
 for r in rows():
  if label(r) in sys.argv[2:]:ns['run'](frozen_row(r,sys.argv[1]),sys.argv[1])
if __name__=='__main__':main()
