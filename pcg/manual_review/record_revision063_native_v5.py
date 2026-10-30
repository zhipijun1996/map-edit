if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from . import record_revision058_native_v2 as previous
from .continue_revision063_v1 import rows,label,OUT
from .record_revision063_native_v1 import folder_for
source=inspect.getsource(previous.run).replace("'-v2'if n=='42'else'-v1'","'-v5'").replace('revision058_native_movie_v1','revision060_native_movie_v2')
source=source.replace("{'42':'C-to-exit','s02':'B-to-T','s07':'L-to-T','s09':'B-to-L','s11':'B-to-R','s12':'B-to-T','s15':'L-to-R'}","{'s09':'L-to-B'}")
ns={**previous.__dict__,'rows':rows,'label':label,'OUT':OUT,'folder_for':folder_for};exec(compile(source,__file__,'exec'),ns)
if __name__=='__main__':ns['run'](next(r for r in rows()if label(r)=='s09'))
