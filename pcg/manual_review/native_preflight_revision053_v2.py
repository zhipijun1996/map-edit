import inspect,sys
from pcg.migration import revision053_runtime_v1 as backend
from . import native_preflight_ideas_v1 as previous
from .continue_revision053_v1 import rows,label

def main():
    source=inspect.getsource(previous.run).replace('approved-ideas-','approved-r053-')
    namespace={**previous.__dict__,'label':label,'backend':backend};exec(compile(source,__file__,'exec'),namespace)
    for row in rows():
        if label(row)in sys.argv[2:]:namespace['run'](row,sys.argv[1])
if __name__=='__main__':main()
