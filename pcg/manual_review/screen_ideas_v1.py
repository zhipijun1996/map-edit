import inspect,sys
from . import screen_review040_v1 as previous
from .new_ideas_v1 import rows,label

def run(r,version):
 s=inspect.getsource(previous.run).replace("'approved-r040-'+row['reviewId']","'approved-ideas-'+label(row)")
 scope={**previous.__dict__,'label':label};exec(compile(s,__file__,'exec'),scope);scope['run'](r,version)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[2:]or label(r)in sys.argv[2:]:run(r,sys.argv[1])
