if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from . import probe_ideas_v1 as previous
from .lift_idea_v1 import rows,label

def main():
    source=inspect.getsource(previous.run).replace('approved-ideas-', 'approved-lift-')
    namespace={**previous.__dict__,'label':label};exec(compile(source,__file__,'exec'),namespace)
    namespace['run'](rows()[0],sys.argv[1])
if __name__=='__main__':main()
