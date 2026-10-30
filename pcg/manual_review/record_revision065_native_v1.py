"""Actual native scene films for the final relay controller and recovery reward."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from . import record_revision058_native_v2 as previous
from .continue_revision065_lift_v1 import OUT,rows
from .run_revision066_lift_v1 import folder_for
def main():
 bonus='bonus'in sys.argv[1:];source=OUT/'fixtures/missed-boarding-wait-chest-v2'if bonus else folder_for(rows()[0]);name='lift-recovery-chest'if bonus else'lift'
 s=inspect.getsource(previous.run).replace("'-v2'if n=='42'else'-v1'","'-v1'").replace('revision058_native_movie_v1','revision060_native_movie_v2')
 ns={**previous.__dict__,'label':lambda r:name,'folder_for':lambda r:source,'OUT':OUT};exec(compile(s,__file__,'exec'),ns);ns['run'](rows()[0])
if __name__=='__main__':main()
