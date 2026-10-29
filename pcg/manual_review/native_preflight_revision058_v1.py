import inspect,sys
from pcg.migration import revision058_runtime_v4 as pair_backend,revision058_runtime_v1 as backend,revision058_runtime_v3 as access_backend,godot_package
from . import native_preflight_ideas_v1 as previous
from .continue_revision058_v1 import rows,label

def main():
 source=inspect.getsource(previous.run).replace('approved-ideas-','approved-r058-')
 for row in rows():
  if label(row)not in sys.argv[2:]:continue
  namespace={**previous.__dict__,'label':label,'backend':godot_package if label(row)=='42'else access_backend if label(row)=='s07'else pair_backend if label(row)=='s11'else backend};exec(compile(source,__file__,'exec'),namespace);namespace['run'](row,sys.argv[1])
if __name__=='__main__':main()
